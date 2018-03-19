import sys
import os
import unittest
import models
from test_base import BaseTest

ROOT_DIR = os.path.join(os.path.dirname(__file__), '../')
ROOT_PATH = os.path.abspath(ROOT_DIR)
sys.path.insert(0, ROOT_PATH)


class UserTest(BaseTest):
    async def test_authenticate(self):
        await models.User.signup('felipe', 'dev@beers.com', 'abc12345')
        user = await models.User.authenticate('dev@beers.com', 'abc12345')
        self.assertTrue(user is not None)
        user_not_found = await models.User.authenticate('dev@beers.com', 'senhainvalida')
        self.assertTrue(user_not_found is None)
        query = models.User.delete.where(models.User.id == user.id)
        await query.gino.all()


class TagTest(BaseTest):
    async def test_create_tag(self):
        tag = await models.Tag.create(name='tagtest')
        self.assertTrue(tag.name == 'tagtest')
        query = models.Tag.delete.where(models.Tag.name == 'tagtest')
        await query.gino.all()

    async def test_create_tag_with_equals_name(self):
        """
        Test to verify when is created a tag, check if exists another with the same name.
        Case exists then return this one, otherwise create the new tag and return it.
        """
        tag1 = await models.Tag.create(name='tagtest')
        tag2 = await models.Tag.create(name='tagtest')
        self.assertEqual(tag1.id, tag2.id, 'The ids must be same')
        query = models.Tag.delete.where(models.Tag.name == 'tagtest')
        await query.gino.all()


class ContentTest(BaseTest):
    async def test_create_content(self):
        user = await models.User.signup('felipe', 'dev@beers.com', 'abc12345')
        content = await models.Content.create(title='Test', description='hello world', tags=['teste', 'abc', 'abc'],
                                              id_user=user.id)
        self.assertEqual(2, len(await models.Content.get_tags(content)), 'Content must contain one tag')

    async def tearDown(self):
        await models.ContentTag.delete.gino.status()
        await models.Tag.delete.gino.status()
        await models.Content.delete.gino.status()
        await models.User.delete.gino.status()


if __name__ == '__main__':
    unittest.main()
