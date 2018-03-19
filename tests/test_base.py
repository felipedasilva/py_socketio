import sys
import os
import asynctest
import configparser
from gino import Gino
import models

ROOT_DIR = os.path.join(os.path.dirname(__file__), '../')
ROOT_PATH = os.path.abspath(ROOT_DIR)
sys.path.insert(0, ROOT_PATH)

config = configparser.ConfigParser()
config.read(ROOT_DIR + '/config.db.ini')

db_params = None
if 'test' in config.sections():
    db_params = config['test']
else:
    raise Exception('Params db test is missing')


class BaseTest(asynctest.TestCase):
    async def setUp(self):
        await models.db.set_bind('postgresql://' + db_params['user'] + ':' + str(db_params['password']) + '@localhost/' + db_params['database'])

    async def tearDown(self):
        await models.db.pop_bind().close()