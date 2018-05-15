import re
import urllib2
import operator
from collections import Counter

import tornado.web
import tornado.ioloop

from core.utils import text_from_html
from model.text_process import TextProcess


class WebPageProcessing(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/main.html")

    def post(self):
        url = self.get_argument('url')
        # r = requests.get(url)
        # html = r.text
        req = urllib2.Request(url)
        html = urllib2.urlopen(req).read()
        text = text_from_html(html)
        words = re.findall(r'\b\w+', text)
        words_lst = [word.lower() for word in words]
        counter = Counter(words_lst)
        top_dict = {word: count for word, count in counter.items()}
        words = sorted(
            top_dict.items(),
            key=operator.itemgetter(1),
            reverse=True
        )
        # Save to DB
        TextProcess.create(
            word='sssss',
            asyc_word='eeee',
            qty=222
        )
        self.render("templates/result.html", words=words[:100])


application = tornado.web.Application([
    (r"/", WebPageProcessing),
])


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
