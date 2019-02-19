import glob
import os

from django.test import TestCase
from django.conf import settings

from user_profile.models import Profile, LeadAnalyst

GLOBAL_FIXTURES = glob.glob(settings.BASE_DIR + "/config/fixtures/*.json")
TEST_FIXTURES = glob.glob(settings.BASE_DIR + "/a_helper/test_fixtures/*.json")
FIXTURES = sorted(GLOBAL_FIXTURES) + sorted(TEST_FIXTURES)
FIXTURE_LIST = []

for f in FIXTURES:
    FIXTURE_LIST.append(os.path.abspath(f))


class UserProfileModel(TestCase):

    fixtures = FIXTURE_LIST

    @classmethod
    def setUpTestData(cls):

        cls.profile = Profile.objects.get(pk=1)
        cls.profile.title='Analyst'
        cls.profile.save()

        cls.lead_analyst = LeadAnalyst.objects.create(profile=cls.profile,
                                                      start_date='2001-01-01',
                                                      end_date='2099-12-31',)

    def test_model_str(self):
        """Test model representations."""

        self.assertEqual(str(self.profile), 'Analytical Personone, Analyst located in Norway (NO)')
        self.assertEqual(str(self.lead_analyst), 'Analytical Personone is lead analyst starting 2001-01-01 and ending 2099-12-31')

    def test_model_property(self):
        """Test model representations."""

        self.assertEqual(self.profile.full_name, 'Analytical Personone')
        self.assertEqual(self.profile.full_name_title, 'Analytical Personone, Analyst')
