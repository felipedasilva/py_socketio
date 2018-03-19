from gino import Gino
import hashlib
import random
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

db = Gino()


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

    def public_data(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }

    def get_json_data(self):
        return '{' + ('"id": "{}", "name": "{}", "email": "{}"'.format(self.id, self.name, self.email)) + '}'


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(), nullable=False)

    @staticmethod
    async def create(name, *args, **kwargs):
        tag = await Tag.query.where(Tag.name == name).gino.first()
        if tag:
            return tag
        return await super(Tag, Tag).create(name=name, *args, **kwargs)


class ContentTag(db.Model):
    __tablename__ = 'contents_tags'

    id_content = db.Column(db.Integer(), primary_key=True)
    id_tag = db.Column(db.Integer(), primary_key=True)

    @staticmethod
    async def create(id_content, id_tag):
        result = await ContentTag.query\
            .where(ContentTag.id_content == id_content)\
            .where(ContentTag.id_tag == id_tag)\
            .gino.first()
        if result:
            return result
        return await super(ContentTag, ContentTag).create(id_content=id_content, id_tag=id_tag)


class Content(db.Model):
    __tablename__ = 'contents'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.Unicode(100), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.Date())
    id_user = db.Column(db.ForeignKey('users.id'), nullable=False)

    @staticmethod
    async def create(*args, **kwargs):
        tags = []
        if 'tags' in kwargs:
            tags = kwargs['tags']
            del kwargs['tags']
        content = await super(Content, Content).create(*args, **kwargs)
        for tag_name in tags:
            tag = await Tag.create(tag_name)
            await ContentTag.create(id_content=content.id, id_tag=tag.id)
        return content

    @relationship
    async def user(self):
        return await User.get(self.user_id)

    @staticmethod
    async def get_tags(content):
        contents_tags = await ContentTag.query.where(ContentTag.id_content == content.id).gino.all()
        tags = []
        for content_tag in contents_tags:
            tags.append(await Tag.query.where(Tag.id == content_tag.id_tag).gino.first())
        return tags