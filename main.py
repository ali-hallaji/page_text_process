import urllib2

import tornado.web
import tornado.ioloop

from core.utils import save_to_db
from core.utils import html_body_to_list_text


class WebPageProcessing(tornado.web.RequestHandler):
    def get(self):
        words = []
        error = {}
        self.render("templates/main.html", words=words, error=error)

    def post(self):
        error = {}
        url = self.get_argument('url')
        req = urllib2.Request(url)
        try:
            html = urllib2.urlopen(req).read()
        except ValueError:
            error = {
                'msg': 'Please Enter a valid URL!'
            }
        # Process words based on questionario
        process_words = html_body_to_list_text(html)

        # Save to DB
        save_to_db(process_words)
        self.render(
            "templates/main.html",
            words=process_words[:100],
            error=error
        )


settings = {
    'debug': True,
    'static_path': 'statics'
}

application = tornado.web.Application(
    [(r"/", WebPageProcessing)],
    **settings
)


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
