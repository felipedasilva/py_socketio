from views import *


class UserAlreadyLogged(Exception):
    pass


class ProcessRequiredUser(Exception):
    pass


class Session:

    def __init__(self, session_id, remove_ip, client_version, datetime):
        self.session_id = session_id
        self.remove_ip = remove_ip
        self.client_version = client_version
        self.datetime = datetime
        self.user = None

    def set_user(self, user):
        if self.user:
            raise UserAlreadyLogged()
        self.user = user

    async def process_message(self, msg):
        msg_type = msg['msg']

        if msg_type == 'login': #Authentication
            return await process_login(self, msg)

        if self.user is None:
            raise ProcessRequiredUser()

        if msg_type == 'NU': #NEW USER
            return await process_create_user(self, msg)

        if msg_type == 'LN': #USER LIST
            return await process_list_all_users(self, msg)