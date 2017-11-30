import asyncio
import time
from gino import enable_task_local
import tornado
from tornado import web, auth, autoreload

class GoogleOAuth2LoginHandler(tornado.web.RequestHandler,
                               tornado.auth.GoogleOAuth2Mixin):

    @tornado.gen.coroutine
    def get(self):
        if self.get_argument('code', False):
            access = yield self.get_authenticated_user(
                redirect_uri='http://localhost:8888/auth/google',
                code=self.get_argument('code'))
            user = yield self.oauth2_request(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                access_token=access["access_token"])
            print('user oauth', 'user')
            print(user)
        else:
            yield self.authorize_redirect(
                redirect_uri='http://localhost:8888/auth/google',
                client_secret='CLIENTE_SECRET',
                client_id='CLIENT_ID',
                scope=['profile', 'email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user = self.get_secure_cookie("user")
        if user:
            return user.decode('utf-8')
        return None


class SecurityHandler(BaseHandler):
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def get(self):
        self.write(self.get_current_user())


async def printtime():
    while True:
        await asyncio.sleep(1)
        print(time.strftime('%H:%M:%S'))

def make_app():
    print('Iniciando server ...')
    settings = {
        "cookie_secret": "GoogleOAuth2LoginHandlerTESTE",
        "xsrf_cookies": True,
        "login_url": "/login",
        "google_oauth": {"key": '642451603973-ecjbsnls4mqdlh4aost76p4stvbo1e8n.apps.googleusercontent.com',
                         "secret": 'UABMQW3VXPf1C7XU_s82QZV7'}
    }
    return tornado.web.Application([
        (r"/login", GoogleOAuth2LoginHandler),
        (r"/auth/google", GoogleOAuth2LoginHandler),
        (r"/home", SecurityHandler)
    ], **settings, debug=True, autoreload=True, serve_traceback=True)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    enable_task_local()
    tornado.ioloop.IOLoop.current().start()
