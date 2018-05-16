import re
import nltk
import uuid
import base64
import shelve
import hashlib
import operator
from Crypto import Random
from collections import Counter
from Crypto.PublicKey import RSA

from bs4 import BeautifulSoup
from bs4.element import Comment

from model.text_process import TextProcess


def get_keys():
    global private_key, public_key
    try:
        return private_key, public_key
    except Exception:
        cursor = shelve.open('keys.db')
        private_key, public_key = cursor['keys']
        cursor.close()
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


def save_to_db(words):
    private_key, public_key = get_keys()
    for _type, word, repeat in words:
        asyc_word = encrypt_word(word, public_key)
        query = TextProcess.select().where(asyc_word == asyc_word)
        if query.exists():
            data = TextProcess.select().where(asyc_word == asyc_word).get()
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
