import os
import sys

os.environ['WAFWFY_CONF'] = "conf/test.py"  # load test conf
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask.ext.testing import TestCase

import wafwfy
from wafwfy import redis
from wafwfy.helpers import PivotalRequest
from wafwfy.tasks import fetch_stories
from wafwfy.models import Story


class BaseTestCase(TestCase):
#    def setUp(self):
#        drop_all()
#        create_all()
#        wafwfy.data.load_data()
#
#    def tearDown(self):
#        db.session.rollback()

    def create_app(self):
        app = wafwfy.app
        return app


class PivotalRequestTestCase(BaseTestCase):
    def test_get_all_stories(self):
        request = PivotalRequest()
        request.get = lambda dummy: open('stories').read()

        self.assertEqual(len(list(request.iter_stories())), 169)


class ClearRedisTestCase(BaseTestCase):
    def setUp(self):
        redis.delete('stories')
        redis.delete('stories:unscheduled')

        for key in redis.keys('story:*'):
            redis.delete(key)


class FetchStoriesTaskTestCase(ClearRedisTestCase):

    def setUp(self):
        def fake_iter_stories(this):
            yield dict(
                id=52,
                current_state='unscheduled',
            )


        self.old_iter_stories = PivotalRequest.iter_stories
        PivotalRequest.iter_stories = fake_iter_stories

        super(FetchStoriesTaskTestCase, self).setUp()

    def tearDown(self):
        PivotalRequest.iter_stories = self.old_iter_stories

    def test_single_story(self):
        fetch_stories()

        self.assertEqual(
            redis.hgetall('story:52'),
            dict(
                current_state='unscheduled',
            )
        )

    def test_stories(self):
        self.assertEqual(redis.scard('stories'), 0)

        fetch_stories()

        self.assertEqual(redis.scard('stories'), 1)

    def test_stories_unscheduled(self):
        self.assertEqual(redis.scard('stories:unscheduled'), 0)

        fetch_stories()

        self.assertEqual(redis.scard('stories:unscheduled'), 1)


class StoryModelTestCase(ClearRedisTestCase):
    @staticmethod
    def create_story(id_=27, status='accepted'):
        Story.create(dict(
            id=id_,
            current_state=status,
        ))

    def test_create(self):
        self.assertEqual(redis.scard('stories'), 0)

        self.create_story()

        self.assertEqual(redis.scard('stories'), 1)

    def test_count_icebox(self):
        self.assertEqual(Story.count_icebox(), 0)

        self.create_story(id_=20, status="unscheduled")
        self.create_story(id_=21, status="unscheduled")
        self.create_story(id_=22, status="unscheduled")

        self.assertEqual(Story.count_icebox(), 3)

    def test_iter_icebox(self):
        self.assertEqual(len(list(Story.iter_icebox())), 0)

        self.create_story(id_=20, status="unscheduled")
        self.create_story(id_=21, status="unscheduled")
        self.create_story(id_=22, status="unscheduled")

        self.assertEqual(len(list(Story.iter_icebox())), 3)
