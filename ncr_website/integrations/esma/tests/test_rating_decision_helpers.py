"""This module tests the feedback sent by ESMA."""
import glob
import os
from integrations.esma.utils.populate_rating_decision.helpers import (
    press_release_data,
    research_report_data,
    get_attributes,
)
from django.test import TestCase
from django.conf import settings
from issuer.models import Issuer
from issue.models import Issue
from rating_process.models.rating_decision import RatingDecision
from rating_process.models.press_release import PressRelease
from rating_process.models.rating_decision_issue import RatingDecisionIssue
from rating_process.models.issue_decision import IssueDecision
from upload.models import AnalyticalDocument
from rating_process.tasks import (
    refresh_decision_attributes,
    update_issue_rating
)

# Load all fixtures
GLOBAL_FIXTURES = glob.glob(settings.BASE_DIR + "/config/fixtures/*.json")
TEST_FIXTURES = glob.glob(settings.BASE_DIR + "/a_helper/test_fixtures/*.json")
FIXTURES = sorted(GLOBAL_FIXTURES) + sorted(TEST_FIXTURES)
FIXTURE_LIST = []

for f in FIXTURES:
    FIXTURE_LIST.append(os.path.abspath(f))


class RatingDecisionHelper(TestCase):

    fixtures = FIXTURE_LIST

    @classmethod
    def setUpTestData(cls):
        """setUpTestData"""

        cls.issuer = Issuer.objects.get(pk=1)
        cls.rating_decision = RatingDecision.objects.create(
            issuer=cls.issuer,
            event_type_id=1,
            rating_type_id=1
        )

        # Delete PressRelease for this test
        PressRelease.objects.get(
            rating_decision=cls.rating_decision).delete()

    def test_press_release_data(self):

        d = press_release_data(self.rating_decision)

        self.assertEqual(d, (None, False))

        press_release = PressRelease.objects.create(
            rating_decision=self.rating_decision,
            header='Test header',
            pre_amble='Test pre-amble',
            body='Test body',
        )

        d2 = press_release_data(self.rating_decision)

        self.assertEqual(d2, (press_release, True))

    def test_research_report_data(self):

        d = research_report_data(self.rating_decision)

        self.assertEqual(d, (None, False))

        research_report = AnalyticalDocument.objects.create(
            issuer_id=1,
            rating_decision=self.rating_decision,
            security_class_id=1,
            uploaded_by_id=1,
            document_type_id=15,
        )

        d2 = research_report_data(self.rating_decision)
        self.assertEqual(d2, (research_report, True))

    def test_attributes(self):

        refresh_decision_attributes(self.rating_decision)

        # Function to be tested
        d = get_attributes(False, self.rating_decision)

        self.assertEqual(d, self.rating_decision.decisionattributes)

        # Create a decision for senior debt
        RatingDecisionIssue.objects.create(
            rating_decision=self.rating_decision,
            seniority_id=1,
            proposed_lt=6,
            decided_lt=6,
        )

        # Create an issue
        Issue.objects.create(
            issuer_id=1,
            isin='xs1',
            maturity='2018-12-31',
            seniority_id=1,
            program_id=1,
        )

        # Create a decision per rating decision level and issue
        update_issue_rating(self.rating_decision)

        rating_decision_issue = IssueDecision.objects.get(pk=1)

        # Function to be tested
        d2 = get_attributes(True, rating_decision_issue)

        self.assertEqual(d2, rating_decision_issue.issuedecisionattribute)
