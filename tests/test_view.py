import sys
import os
import unittest
from test_base import BaseTest, models
import json

ROOT_DIR = os.path.join(os.path.dirname(__file__), '../')
ROOT_PATH = os.path.abspath(ROOT_DIR)
sys.path.insert(0, ROOT_PATH)

from views import *
from session import Session


class ViewTest(BaseTest):
    async def setUp(self):
        await super(ViewTest, self).setUp()
        self.session = Session(None, None, None, None)
        self.user = await models.User.signup('test', 'test@test.com', '123')

    async def tearDown(self):
        query = models.User.delete.where(models.User.id == self.user.id)
        await query.gino.all()

    async def test_login(self):
        msg = {
            'msg': 'login',
            'params': {
                'email': 'test@test.com',
                'password': '123'
            }
        }
        try:
            response = await process_login(self.session, msg)
            self.assertTrue(response.find('success') != -1)
        except Exception as e:
            self.fail('Exception not excepted')


class ViewTest2(BaseTest):
    async def setUp(self):
        await super(ViewTest2, self).setUp()
        self.session = Session(None, None, None, None)

    async def test_create_user(self):
        msg = {
            'msg': 'NU',
            'params': {
                'email': 'faker@test.com',
                'password': '1234',
                'name': 'faker'
            }
        }
        try:
            response = await process_create_user(self.session, msg)
            print(response)
            self.assertTrue(response.find(b'success') != -1)
            query = models.User.delete.where(models.User.email == 'faker@test.com')
            await query.gino.all()
        except Exception as e:
            self.fail('Exception not excepted')


if __name__ == '__main__':
    unittest.main()
