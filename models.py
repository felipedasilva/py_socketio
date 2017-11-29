from gino import Gino, enable_task_local
import hashlib
import random
import asyncio

db = Gino()
loop = asyncio.get_event_loop()
enable_task_local(loop)


class UserAlreadyExistsException(Exception):
    pass


def get_hexdigest(algorithm, salt, raw_password):
    raw_password = raw_password.lower().encode("utf-8")
    salt = salt.lower().encode("utf-8")
    if algorithm == 'sha1':
        return hashlib.sha1(salt + raw_password).hexdigest()
    elif algorithm == 'bcrypt':
        import bcrypt
        return bcrypt.hashpw(raw_password, salt)
    raise Exception("Got unknown password algorithm type in password.")


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(), nullable=False)
    email = db.Column(db.Unicode(), nullable=False)

    password_algo = db.Column(db.Unicode(), nullable=False)
    password_salt = db.Column(db.Unicode(), nullable=False)
    password = db.Column(db.Unicode(), nullable=False)

    def __init__(self, *args, **kwargs):
        if 'password' in kwargs:
            params = User.crypt_password(kwargs.get('password'))
            del kwargs['password']
            kwargs.update(params)
        super(User, self).__init__(*args, **kwargs)

    @staticmethod
    def crypt_password(raw_password):
        password_algo = 'sha1'
        password_salt = get_hexdigest(password_algo, str(random.random()), str(random.random()))[:5]
        password = get_hexdigest(password_algo, password_salt, raw_password)
        return {'password_algo': password_algo, 'password_salt': password_salt, 'password': password}

    def check_password(self, raw_password):
        return self.password == get_hexdigest(self.password_algo, self.password_salt, raw_password)

    @staticmethod
    async def signup(name, email, password):
        user = await User.get_user(email=email)
        if user:
            raise UserAlreadyExistsException()
        user = await User.create(name=name.strip(), email=email.strip(), password=password)
        if user:
            return user
        return None

    @staticmethod
    async def get_user(id=None, email=None, name=None):
        if name:
            name = name.lower().strip()
            condition = User.name == name
        if email:
            email = email.lower().strip()
            condition = User.email == email
        if id:
            condition = User.id == id

        user = await User.query.where(condition).gino.first()
        if user:
            return user
        return None

    @staticmethod
    async def authenticate(email, password):
        user = await User.get_user(email=email)
        if type(user) == User:
            if user.check_password(password):
                return user
        return None
