import glob
import os
import datetime

from django.test import TestCase

from issuer.models import Issuer, Analyst
from django.contrib.auth.models import User

from issue.models import Issue
from issue.tasks import mature_debt

from rating_process.models.issue_decision import IssueDecision
from rating_process.models.rating_decision import RatingDecision
from rating_process.models.rating_decision_issue import RatingDecisionIssue

from django.utils import timezone
from datetime import timedelta

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

        cls.system_user = User.objects.get(username='tron')

        cls.live_issuer = Issuer.objects.get(pk=1)
        cls.analysts = Analyst.objects.filter(issuer=cls.live_issuer).update(
            primary_analyst_id=1,
            secondary_analyst_id=2,
        )

        cls.issue = Issue.objects.create(issuer=cls.live_issuer,
                                         isin='NO0010831897',
                                         name='Test name',
                                         maturity=datetime.datetime.today(),
                                         currency_id=1,
                                         amount=100,
                                         seniority_id=1,
                                         program_id=1,)

        # Create a confidential rating
        decision_1 = RatingDecision.objects.create(
            initiated_by_id=1,

            issuer=cls.live_issuer,

            event_type_id=1,
            rating_type_id=3,

            event='A new secret bond issue.',

            date_time_committee=timezone.now() - timedelta(days=10),
            date_time_committee_confirmed=True,
            date_time_published=timezone.now() - timedelta(days=10),

            proposed_lt_outlook=1,
            proposed_st=1,

            decided_lt_outlook=1,
            decided_st=2,

            chair_id=1,
            chair_confirmed=True,

            primary_analyst_id=1,
            secondary_analyst_id=1,

            recommendation_rationale='Recommendation.',
            committee_comments='Committee comments.',
        )

        cls.rating_decision_issue = RatingDecisionIssue.objects.create(
            rating_decision=decision_1,
            seniority_id=1,
            proposed_lt=4,
            decided_lt=4,
        )

        cls.issue_decision = IssueDecision.objects.create(
            rating_decision_issue=cls.rating_decision_issue,
            issue=cls.issue,

            is_current=True,
            decided_lt=7,

            date_time_committee=timezone.now(),
            date_time_communicated_issuer=timezone.now() + timedelta(
                minutes=1),
            date_time_published=timezone.now() + timedelta(
                minutes=2),

            chair=cls.system_user,
            proposed_by=cls.system_user,

            rationale='Automatic system insert due to matured issue.',

            process_step=10,
        )


    def setUp(self):
        """SetUp."""
        self.live_issuer.refresh_from_db()
        self.issue.refresh_from_db()


    def test_maturity_task(self):
        # Run mature debt task

        mature_debt()

        # Required to make this work
        self.issue.refresh_from_db()

        # Make sure the bond is flagged as matured
        self.assertTrue(self.issue.is_matured)

        rd = IssueDecision.objects.get(
            is_current=True,
            issue=self.issue,
        )

        # Make sure some of the properties are correctly set
        self.assertEqual(rd.is_current, True)
        self.assertEqual(rd.rationale, "Automatic system insert due to matured issue.")
        self.assertEqual(rd.decided_lt, 200)
