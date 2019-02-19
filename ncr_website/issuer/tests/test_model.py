import glob
import os
from datetime import datetime
from django.test import TestCase
from django.conf import settings


from ..models import (
    Issuer,
    InsiderList,
    IssuerType,
    Analyst,
    OnboardingProcess,
    EventType,
    Event
)

# Load all fixtures
GLOBAL_FIXTURES = glob.glob(settings.BASE_DIR + "/config/fixtures/*.json")
TEST_FIXTURES = glob.glob(settings.BASE_DIR + "/a_helper/test_fixtures/*.json")
FIXTURES = sorted(GLOBAL_FIXTURES) + sorted(TEST_FIXTURES)
FIXTURE_LIST = []

for f in FIXTURES:
    FIXTURE_LIST.append(os.path.abspath(f))

class RatingDecisionTest(TestCase):

    fixtures = FIXTURE_LIST

    @classmethod
    def setUpTestData(cls):
        """setUpTestData"""

        cls.live_issuers = Issuer.objects.is_live()
        cls.live_issuer = Issuer.objects.get(pk=1)
        cls.issuer_corporate_inactivated_obj = Issuer.objects.get(pk=4)

    def test_live_query(self):
        """Test the is live object."""

        self.inactivated_issuer = Issuer.objects.get(pk=4)

        self.assertIn(self.live_issuer, self.live_issuers)
        self.assertNotIn(self.inactivated_issuer, self.live_issuers)

    def test_util(self):

        self.insider = InsiderList.objects.create(issuer=self.live_issuer,
                                                  first_name='P',
                                                  last_name='L',
                                                  email='name@host.com',
                                                  role='Analyst')

        self.assertIn(self.insider, InsiderList.objects.filter(issuer=self.live_issuer))

    def test_model_str(self):
        """Test model representations."""
        self.issuer_type = IssuerType.objects.get(pk=1)
        self.analyst = Analyst.objects.get(issuer=self.live_issuer)
        self.insider = InsiderList.objects.get(pk=1)
        self.onboarding = OnboardingProcess.objects.get(issuer=self.live_issuer)
        self.event_type = EventType.objects.get(pk=1)
        self.event = Event.objects.create(issuer=self.live_issuer,
                                          triggered_by_user_id=1,
                                          event_type_id=1)

        self.assertEqual(str(self.issuer_type), 'Corporate')
        self.assertEqual(str(self.live_issuer), 'Milles Rating and Dating AS')
        self.assertEqual(str(self.analyst), 'Analysts for Milles Rating and Dating AS')
        self.assertEqual(str(self.insider), 'Pa L is on insider list for Milles Rating and Dating AS as primary contact')
        self.assertEqual(str(self.onboarding), 'Onboarding for Milles Rating and Dating AS')
        self.assertEqual(str(self.event_type), 'Issuer added')
        self.assertEqual(str(self.event), 'Milles Rating and Dating AS: "Issuer added" on %s' % datetime.today().strftime('%Y-%m-%d'))
