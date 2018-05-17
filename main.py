import urllib2

import tornado.web
import tornado.ioloop

from config import settings
from core.utils import show_urls
from core.utils import show_words
from core.utils import url_save_to_db
from core.utils import words_save_to_db
from core.utils import html_body_to_list_text


class WebPageProcessing(tornado.web.RequestHandler):
    def get(self):
        data = {}
        self.render("templates/main.html", data=data)

    def post(self):
        data = {}
        url = self.get_argument('url')
        req = urllib2.Request(url)
        try:
            html = urllib2.urlopen(req).read()
        except ValueError:
            data['error'] = {
                'msg': 'Please Enter a valid URL!'
            }
            self.render("templates/main.html", data=data)
        # Process words based on questionario
        process_words = html_body_to_list_text(html)

        # Save to DB
        words_save_to_db(process_words[:100])
        result_url = url_save_to_db(url, process_words[:100])
        data['words'] = process_words[:100]
        data['result_url'] = result_url
        self.render("templates/main.html", data=data)


class DashboardAdmin(tornado.web.RequestHandler):
    def get(self, mode=None):
        data = {}
        if mode == 'words':
            data['words'] = show_words()
        elif mode == 'urls':
            data['urls'] = show_urls()
        data['mode'] = mode

        self.render("templates/dashboard.html", data=data)


application = tornado.web.Application(
    [
        (r"/", WebPageProcessing),
        (r"/dashboard/([^/]*)", DashboardAdmin),
    ],
    **settings
)


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
