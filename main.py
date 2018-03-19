import tornado.web
import tornado.ioloop
import tornado.options
import tornado.escape
import tornado.auth
import tornado.gen
import tornado.websocket
from gino.ext.tornado import Application, GinoRequestHandler

import json
import configparser
import models

from session_manager import SessionManager

config = configparser.ConfigParser()
config.read('config.db.ini')

db_params = None
if 'prod' in config.sections():
    db_params = {}
    for name in config['prod']:
        value = config['prod'][name]
        try:
            value = int(value)
        except Exception as e:
            pass
        db_params[name] = value
else:
    raise Exception('Params db prod is missing')


class WebSocketHandler(tornado.websocket.WebSocketHandler):

    async def open(self):
        await self.application.session_manager.process_message('OPN', id(self), None)
        print("WebSocket opened", id(self))

    async def on_message(self, message):
        try:
            msg = json.loads(message)
        except Exception:
            self.write_message(json.dumps(u'{"status": "error", "detail": "Invalid formatted", "msg": "' + msg['msg']
                                          + '"}'))
            self.close()
            return

        if 'msg' not in msg:
            self.write_message(u'{"status": "error","detail": "Field \"msg\" is required", "msg": "' + msg['msg']
                               + '"}')
            self.close()
            return

        session_manager = self.application.session_manager
        response = await session_manager.process_message('REQ', id(self), msg)
        self.write_message(response)

    def on_close(self):
        self.application.session_manager.process_message('CLS', id(self), None)
        print("WebSocket closed")

    def check_origin(self, origin):
        return True


class LoginHandler(GinoRequestHandler):

    async def get(self):
        user = await models.User.authenticate('dev@beers.com', 'abc12345')
        self.set_secure_cookie('user', user.email)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user = self.get_secure_cookie("user")
        if user:
            return user.decode('utf-8')
        return None


class SecurityHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        self.write(self.get_current_user())


class WSAplication(Application):
    def __init__(self, handlers=None, default_host=None, transforms=None, **settings):
        super(WSAplication, self).__init__(handlers, default_host, transforms, **settings)
        self.session_manager = SessionManager()


if __name__ == '__main__':
    tornado.options.parse_command_line()
    tornado.ioloop.IOLoop.configure('tornado.platform.asyncio.AsyncIOMainLoop')
    settings = {
        "cookie_secret": "cookie_is_good",
        "xsrf_cookies": True,
        "login_url": "/login",
    }
    app = WSAplication([
        (r"/login", LoginHandler),
        (r"/home", SecurityHandler),
        (r"/ws", WebSocketHandler)
    ], **settings, debug=True, autoreload=True)
    loop = tornado.ioloop.IOLoop.current().asyncio_loop
    loop.run_until_complete(app.late_init(models.db, options=db_params))
    app.listen(8888)
    loop.run_forever()
