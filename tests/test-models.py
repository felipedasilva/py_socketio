import sys
import os
import asynctest
import models
import configparser

ROOT_DIR = os.path.join(os.path.dirname(__file__), '../')
ROOT_PATH = os.path.abspath(ROOT_DIR)
sys.path.insert(0, ROOT_PATH)

config = configparser.ConfigParser()
config.read(ROOT_DIR + 'config.db.ini')

db_params = None
if 'test' in config.sections():
    db_params = config['test']
else:
    raise Exception('Params db test is missing')

@asynctest.fail_on(unused_loop=False)
class BaseTest(asynctest.TestCase):
    async def setUp(self):
        await models.db.create_pool(user=db_params['user'], password=db_params['password'], database=db_params['database'])


class UserTest(BaseTest):
    async def test_authenticate(self):
        await models.User.signup('felipe', 'dev@beers.com', 'abc12345')
        user = await models.User.authenticate('dev@beers.com', 'abc12345')
        self.assertTrue(user is not None)
        user_not_found = await models.User.authenticate('dev@beers.com', 'senhainvalida')
        self.assertTrue(user_not_found is None)
        query = models.User.delete.where(models.User.id == user.id)
        await query.gino.all()
