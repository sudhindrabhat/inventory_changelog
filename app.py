import os
from app.handlers.base import BaseHandler
from app.handlers.handlers import CreateSessionHandler, \
     HttpNotFoundHandler, CreateItemHandler, ModifyItemsHandler, DeleteItemHandler, \
    CreateVariantHandler, ModifyVariantsHandler, DeleteVariantHandler, ActivityFeedHandler
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpserver
from tornado.options import define, options
from tornado.web import url

from debug_config import Config

define("port", default=8080, type=int)


class Application(tornado.web.Application):
    def __init__(self, *overrides):
        handlers = [
            url(r'/session_create', CreateSessionHandler),
            url(r'/item/create', CreateItemHandler),
            url(r'/item/modify', ModifyItemsHandler),
            url(r'/item/delete', DeleteItemHandler),
            url(r'/variant/create', CreateVariantHandler),
            url(r'/variant/modify', ModifyVariantsHandler),
            url(r'/variant/delete', DeleteVariantHandler),
            url(r'/activity/preview', ActivityFeedHandler),
            url(r'/(.*)', HttpNotFoundHandler)
        ]


        settings = {
            'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
            'xsrf_cookies': False,
            'debug': False,
            'log_file_prefix': "tornado.log"
        }

        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
