import re
import nltk
import uuid
import base64
import hashlib
import operator
from wit import Wit
from Crypto import Random
from collections import Counter
from Crypto.PublicKey import RSA

from bs4 import BeautifulSoup
from bs4.element import Comment

from config import WIT_AI_TOKEN
from model.text_process import TextProcess
from model.text_process import SentimentAnalysis


def get_keys():
    with open('private_key.pem', 'r') as f:
        private_key = RSA.importKey(f.read())
    with open('public_key.pem', 'r') as f:
        public_key = RSA.importKey(f.read())

    return private_key, public_key


def tag_visible(element):
    ignore = ['style', 'script', 'head', 'title', 'meta', '[document]']
    if element.parent.name in ignore:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


def get_salt_hash(word):
    salt = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    hashed_word = hashlib.sha512(word + salt).hexdigest()
    return hashed_word


def url_save_to_db(url, words):
    query = SentimentAnalysis.select().where(SentimentAnalysis.url == url)
    result = check_by_wit_ai(words)
    if query.exists():
        data = SentimentAnalysis.select().where(SentimentAnalysis.url == url).get()
        data.situation = result
        data.save()
    else:
        hash_url = get_salt_hash(url)
        SentimentAnalysis.create(
            salt_url=hash_url,
            url=url,
            situation=result
        )
    return result


def check_by_wit_ai(words):
    text = ""
    for item in words:
        text += (item[1] + " ")

    try:
        client = Wit(WIT_AI_TOKEN)
        result = client.message(text[:280])
    except Exception:
        result = {}

    answer = '-'
    if result and ('Sentiment' in result.get('entities', {})):
        answer = result['entities']['Sentiment'][0].get('value', '-')
    return answer


def words_save_to_db(words):
    private_key, public_key = get_keys()
    for _type, word, repeat in words:
        asyc_word = encrypt_word(word, public_key)
        query = TextProcess.select().where(TextProcess.asyc_word == asyc_word)
        if query.exists():
            data = TextProcess.select().where(TextProcess.asyc_word == asyc_word).get()
            data.qty = int(repeat)
            data.save()
        else:
            hash_word = get_salt_hash(word)
            TextProcess.create(
                word=hash_word,
                asyc_word=asyc_word,
                qty=int(repeat)
            )


def check_nn_vb(word):
    text = nltk.word_tokenize(word)
    check = nltk.pos_tag(text)
    if (check[0][1] == 'NN') or (check[0][1] == 'VB'):
        return True


def put_nn_vb(data):
    text = nltk.word_tokenize(data[0])
    check = nltk.pos_tag(text)
    trans = {'NN': 'Noun', 'VB': 'Verb'}
    return (trans[check[0][1]], data[0], data[1])


def html_body_to_list_text(html):
    text = text_from_html(html)
    words = re.findall(r'\b\w+', text)
    words_lst = [word.lower() for word in words]
    words_lst = filter(
        lambda word: check_nn_vb(word),
        words_lst
    )
    top_dict = counter_words(words_lst)
    words = sorted(
        top_dict.items(),
        key=operator.itemgetter(1),
        reverse=True
    )
    process_words = map(
        lambda x: put_nn_vb(x),
        words
    )
    return process_words


def counter_words(words_lst):
    counter = Counter(words_lst)
    top_dict = {word: count for word, count in counter.items()}
    return top_dict


def generate_keys():
    modulus_length = 256 * 4
    privatekey = RSA.generate(modulus_length, Random.new().read)
    publickey = privatekey.publickey()
    return privatekey, publickey


def encrypt_word(word, publickey):
    encrypted_msg = publickey.encrypt(str(word), 32)[0]
    encoded_encrypted_word = base64.b64encode(encrypted_msg)
    return encoded_encrypted_word


def decrypt_word(encoded_encrypted_word, privatekey):
    decoded_encrypted_msg = base64.b64decode(encoded_encrypted_word)
    decoded_decrypted_word = privatekey.decrypt(decoded_encrypted_msg)
    return decoded_decrypted_word


def show_words():
    words = []
    private_key, public_key = get_keys()
    print private_key
    for record in TextProcess.select().dicts():
        record['decrypt_word'] = decrypt_word(
            record['asyc_word'],
            private_key
        )
        new_record = put_nn_vb(
            [record['decrypt_word'], record['qty']]
        )
        words.append(new_record)
    return words


def show_urls():
    urls = []
    for record in SentimentAnalysis.select().dicts():
        urls.append(record)
    return urls
