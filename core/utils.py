import uuid
import base64
import hashlib

from bs4 import BeautifulSoup
from bs4.element import Comment


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
