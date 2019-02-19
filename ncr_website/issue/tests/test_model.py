import glob
import os

from django.test import TestCase

from issuer.models import Issuer

from ..models import (
    Seniority,
    Issue,
)
from ..forms import (
    EditIssueForm
)
from django.conf import settings

GLOBAL_FIXTURES = glob.glob(settings.BASE_DIR + "/config/fixtures/*.json")
TEST_FIXTURES = glob.glob(settings.BASE_DIR + "/a_helper/test_fixtures/*.json")
FIXTURES = sorted(GLOBAL_FIXTURES) + sorted(TEST_FIXTURES)
FIXTURE_LIST = []

for f in FIXTURES:
    FIXTURE_LIST.append(os.path.abspath(f))


class IssueTest(TestCase):

    fixtures = FIXTURE_LIST

    @classmethod
    def setUpTestData(cls):
        """setUpTestData"""

        cls.live_issuer = Issuer.objects.get(pk=1)
        cls.senior_unsecured = Seniority.objects.get(pk=1)
        cls.issue = Issue.objects.create(issuer=cls.live_issuer,
                                         isin='abc123',
                                         name='Test name',
                                         maturity='2033-05-01',
                                         currency_id=1,
                                         amount=100,
                                         seniority_id=1,
                                         program_id=1,)
        cls.dead_issue = Issue.objects.create(issuer=cls.live_issuer,
                                              isin='abc122',
                                              name='Test name',
                                              maturity='2017-05-01',
                                              currency_id=1,
                                              amount=100,
                                              seniority_id=1,
                                              program_id=1,)

    def setUp(self):
        """SetUp."""
        self.live_issuer.refresh_from_db()
        self.senior_unsecured.refresh_from_db()
        self.issue.refresh_from_db()
        self.dead_issue.refresh_from_db()

    def test_live_trades(self):
        """Test the live trades object."""
        self.live_trades = Issue.objects.live_trades()

        self.assertIn(self.issue, self.live_trades)
        self.assertNotIn(self.dead_issue, self.live_trades)

    def test_model_str(self):
        """Test model representations."""

        self.assertEqual(str(self.senior_unsecured), 'Senior Unsecured')
        self.assertEqual(str(self.issue), 'abc123: XUA 0.0 m')

    # Valid Form Data
    def test_EditIssueForm_valid(self):
        """Test EditIssueForm."""

        form = EditIssueForm(issue_pk=1,
                             data={'isin': 'XS1234567890',
                                   'seniority': 1,
                                   'disbursement': '2018-01-01',
                                   'maturity': '2021-01-01',
                                   'currency_id': 1,
                                   'amount': 100000,
                                   'ticker': 'abc123',
                                   'name': 'issue_name',
                                   'currency': 1,
                                   'program':1,
                                   })

        self.assertTrue(form.is_valid())

    # Valid Form Data
    def test_EditIssueForm_invalid(self):
        """Test EditIssueForm."""

        form = EditIssueForm(issue_pk=1,
                             data={'isin': 'XS1234567890',
                                   'disbursement': '2018-01-01',
                                   'maturity': '2021-01-01',
                                   'currency_id': 1,
                                   'amount': 100000,
                                   'ticker': 'abc123',
                                   'name': 'issue_name',
                                   'program':1,
                                   })

        self.assertFalse(form.is_valid())
