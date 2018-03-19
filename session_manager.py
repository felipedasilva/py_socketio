from session import Session
from datetime import datetime


class SessionAlreadyOpened(Exception):
    pass


class SessionNotFound(Exception):
    pass


class InvalidOptCodeError(Exception):
    pass


class SessionManager:
    def __init__(self):
        self.sessions = {}

    def open_session(self, session_id, msg):
        remove_ip = None
        client_version = None
        if msg:
            remove_ip = msg.get('RemoteIp', None)
            client_version = msg.get('ClientVersion', None)
        self.sessions[session_id] = Session(session_id, remove_ip, client_version, datetime.now())

    async def process_message(self, msg_header, session_id, msg):
        if msg_header == 'OPN':
            if session_id in self.sessions:
                raise SessionAlreadyOpened()
            self.open_session(session_id, msg)
            return

        if msg_header == 'CLS':
            if session_id not in self.sessions:
                raise SessionNotFound()
            del self.sessions[session_id]
            return

        if msg_header != 'REQ':
            raise InvalidOptCodeError()

        if session_id not in self.sessions:
            raise SessionNotFound()

        session = self.sessions.get(session_id)
        return await session.process_message(msg)
