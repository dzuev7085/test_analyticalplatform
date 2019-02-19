import glob
import os
from django.urls import reverse
from django.test import TestCase
from django.conf import settings

GLOBAL_FIXTURES = glob.glob(settings.BASE_DIR + "/config/fixtures/*.json")
TEST_FIXTURES = glob.glob(settings.BASE_DIR + "/a_helper/test_fixtures/*.json")
FIXTURES = sorted(GLOBAL_FIXTURES) + sorted(TEST_FIXTURES)
FIXTURE_LIST = []

for f in FIXTURES:
    FIXTURE_LIST.append(os.path.abspath(f))


class RatingTest(TestCase):

    fixtures = FIXTURE_LIST

    def test_dashboard_view(self):
        """Make sure the dashboard view loads properly."""
        self.client.login(username='analyst1', password='abc123')  # defined in fixture or with factory in setUp()

        # response = self.client.get(
        #     reverse('issuer_view', kwargs={'pk': 1}),
        # )

        # self.assertEqual(response.status_code, 200)
