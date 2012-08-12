import os
import sys

os.environ['WAFWFY_CONF'] = "conf/test.py"  # load test conf
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask.ext.testing import TestCase

import wafwfy
from wafwfy.helpers import PivotalRequest


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

        self.assertEqual(len(list(request.get_all_stories())), 169)
