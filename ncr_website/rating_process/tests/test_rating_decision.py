import glob
import os
from datetime import timedelta

from django.test import TestCase

from django.utils import timezone

from issuer.models import (
    Issuer,
    InsiderList
)

from rating_process.models.issue_decision import IssueDecision

from ..models.rating_decision import RatingDecision
from ..models.rating_decision_issue import RatingDecisionIssue
from ..models.internal_score_data import InternalScoreData
from ..models.temporary_storage import Tmp
from ..models.questions import ControlQuestion
from ..models.process import Process
from ..models.insider_link import RatingDecisionInsiderLink
from ..models.view_log import ViewLog
from ..tasks import refresh_decision_attributes, update_issue_rating
from issue.models import Issue
from django.conf import settings

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

        # Corporate
        cls.issuer_corporate_obj = Issuer.objects.get(pk=1)
        cls.corporate_rating_decision_obj = RatingDecision.objects.create(
            issuer=cls.issuer_corporate_obj,
            event_type_id=1,
            rating_type_id=1)

        # Corporate real estate
        cls.issuer_corporate_re_obj = Issuer.objects.get(pk=2)
        cls.corporate_re_rating_decision_obj = RatingDecision.objects.create(
            issuer=cls.issuer_corporate_re_obj,
            event_type_id=1,
            rating_type_id=1,
            is_preliminary=True)

        # Corporate real estate
        cls.issuer_financial_obj = Issuer.objects.get(pk=3)
        cls.financial_rating_decision_obj = RatingDecision.objects.create(
            issuer=cls.issuer_financial_obj,
            event_type_id=1,
            rating_type_id=1)

        cls.process_obj = Process.objects.get(
            rating_decision=cls.corporate_rating_decision_obj)

        cls.tmp_obj = Tmp.objects.get(
            rating_decision=cls.corporate_rating_decision_obj)

        cls.senior_unsecured = Issue.objects.create(issuer=cls.issuer_corporate_obj,
                                         isin='abc123',
                                         name='Test name',
                                         maturity='2033-05-01',
                                         currency_id=1,
                                         amount=100,
                                         seniority_id=1,
                                         program_id=1,)

    def test_corporate_signals(self):
        """Assert that database records are created when a
        RatingDecision record is created."""

        self.question_obj = ControlQuestion.objects.filter(
            rating_decision=self.corporate_rating_decision_obj)[0]

        self.assertTrue(isinstance(self.issuer_corporate_obj, Issuer))
        self.assertTrue(isinstance(self.corporate_rating_decision_obj, RatingDecision))
        self.assertTrue(isinstance(self.tmp_obj, Tmp))
        self.assertTrue(isinstance(self.question_obj, ControlQuestion))
        self.assertTrue(isinstance(self.process_obj, Process))

    def test_corporate_re_signals(self):
        """Assert that database records are created when a
        RatingDecision record is created."""

        self.tmp_obj = Tmp.objects.get(
            rating_decision=self.corporate_re_rating_decision_obj)
        self.question_obj = ControlQuestion.objects.filter(
            rating_decision=self.corporate_re_rating_decision_obj)[0]
        self.process_obj = Process.objects.get(
            rating_decision=self.corporate_re_rating_decision_obj)

        self.assertTrue(isinstance(self.issuer_corporate_obj, Issuer))
        self.assertTrue(isinstance(self.corporate_re_rating_decision_obj, RatingDecision))
        self.assertTrue(isinstance(self.tmp_obj, Tmp))
        self.assertTrue(isinstance(self.question_obj, ControlQuestion))
        self.assertTrue(isinstance(self.process_obj, Process))

    def test_corporate_subscores(self):
        """ This is to test a corporate issuer."""

        self.subscores = InternalScoreData.objects.filter(
            rating_decision=self.corporate_rating_decision_obj)

        # Operating environment
        self.assertTrue(isinstance(self.subscores.get(subfactor_id=1), InternalScoreData))

        # Market position
        self.assertTrue(isinstance(self.subscores.get(subfactor_id=2), InternalScoreData))

        # Operating efficiency
        self.assertTrue(isinstance(self.subscores.get(subfactor_id=3), InternalScoreData))

        # Size and diversification
        self.assertTrue(isinstance(self.subscores.get(subfactor_id=4), InternalScoreData))

        # Financial risk assessment
        self.assertTrue(isinstance(self.subscores.get(subfactor_id=5), InternalScoreData))

        # Liquidity
        self.assertTrue(isinstance(self.subscores.get(subfactor_id=6), InternalScoreData))

        # ESG
        self.assertTrue(isinstance(self.subscores.get(subfactor_id=7), InternalScoreData))

        # Peer comparison
        self.assertTrue(isinstance(self.subscores.get(subfactor_id=8), InternalScoreData))

        # Ownership support
        self.assertTrue(isinstance(self.subscores.get(subfactor_id=9), InternalScoreData))

    def test_corporate_re_subscores(self):
        """ This is to test a corporate real estate issuer."""

        self.re_subscores = InternalScoreData.objects.filter(
            rating_decision=self.corporate_re_rating_decision_obj)

        # Operating environment
        self.assertTrue(isinstance(self.re_subscores.get(subfactor_id=1), InternalScoreData))

        # Market position, size and diversification
        self.assertTrue(isinstance(self.re_subscores.get(subfactor_id=10), InternalScoreData))

        # Portfolio assessment
        self.assertTrue(isinstance(self.re_subscores.get(subfactor_id=11), InternalScoreData))

        # Operating efficiency
        self.assertTrue(isinstance(self.re_subscores.get(subfactor_id=3), InternalScoreData))

        # Financial risk assessment
        self.assertTrue(isinstance(self.re_subscores.get(subfactor_id=5), InternalScoreData))

        # Liquidity
        self.assertTrue(isinstance(self.re_subscores.get(subfactor_id=6), InternalScoreData))

        # ESG
        self.assertTrue(isinstance(self.re_subscores.get(subfactor_id=7), InternalScoreData))

        # Peer comparison
        self.assertTrue(isinstance(self.re_subscores.get(subfactor_id=8), InternalScoreData))

        # Ownership support
        self.assertTrue(isinstance(self.re_subscores.get(subfactor_id=9), InternalScoreData))

    def test_financial_subscores(self):
        """ This is to test a financial issuer."""

        self.fin_subscores = InternalScoreData.objects.filter(
            rating_decision=self.financial_rating_decision_obj)

        # National factors
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=12), InternalScoreData))

        # Regional, cross border, sector
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=13), InternalScoreData))

        # Capital
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=14), InternalScoreData))

        # Funding and liquidity
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=15), InternalScoreData))

        # Risk governance
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=16), InternalScoreData))

        # Credit risk
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=17), InternalScoreData))

        # Market risk
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=18), InternalScoreData))

        # Other risks
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=19), InternalScoreData))

        # Market position
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=20), InternalScoreData))

        # Earnings
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=21), InternalScoreData))

        # Loss performance
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=22), InternalScoreData))

        # Transitions
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=23), InternalScoreData))

        # Borderline assessments
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=24), InternalScoreData))

        # Material credit enhancement
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=25), InternalScoreData))

        # Rating caps
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=26), InternalScoreData))

        # Peer comparison
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=8), InternalScoreData))

        # Ownership support
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=9), InternalScoreData))

    def test_model_str(self):
        """Test model representations."""

        # Test insider likn
        self.insider = InsiderList.objects.get(pk=1)
        self.insider_link = RatingDecisionInsiderLink(
            rating_decision=self.corporate_rating_decision_obj,
            insider=self.insider
        )
        self.assertEqual(str(self.insider_link), 'Pa L (Role | Primary contact)')

        # Test view log
        self.log = ViewLog.objects.create(
            rating_decision=self.corporate_rating_decision_obj,
            downloaded_by_id=1
        )
        self.assertEqual(str(self.log), 'Committee pack for Milles Rating and Dating AS was downloaded by Analytical Personone on %s' % timezone.now().strftime('%Y-%m-%d %H:%M'))

        # Test process
        self.assertEqual(str(self.process_obj), 'Process for Rating job for Milles Rating and Dating AS | setup | Current rating: False')

        # Test tmp
        self.assertEqual(str(self.tmp_obj), 'Tmp for Rating job for Milles Rating and Dating AS | setup | Current rating: False')

        # Issue
        self.issue = RatingDecisionIssue.objects.create(rating_decision=self.corporate_rating_decision_obj,
                                                        seniority_id=1,
                                                        proposed_lt=7,
                                                        decided_lt=8)
        self.assertEqual(str(self.issue), "Milles Rating and Dating AS's issues on seniority level 'senior unsecured': proposed to 'A-' and decided for 'BBB+'")

    def test_decision_attributes(self):

        # Create a confidential rating
        decision_1 = RatingDecision.objects.create(
            initiated_by_id=1,

            issuer=self.issuer_corporate_obj,

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

        RatingDecisionIssue.objects.create(
            rating_decision=decision_1,
            seniority_id=1,
            proposed_lt=4,
            decided_lt=4,
        )

        # Manual override
        decision_1.is_current=True
        decision_1.is_preliminary=True
        decision_1.decided_lt = 4
        decision_1.decided_lt_outlook = 2
        decision_1.decided_st = 2
        decision_1.save()

        # needed to update the DecisionAttributes model
        refresh_decision_attributes(decision_1)

        # Add decisions for the issue level
        update_issue_rating(decision_1)

        issue_decision = IssueDecision.objects.get(pk=1)

        # Tests IssueDecision
        self.assertEqual(issue_decision.is_current, True)
        self.assertEqual(issue_decision.issue, self.senior_unsecured)
        self.assertEqual(issue_decision.previous_rating, None)
        self.assertEqual(issue_decision.decided_lt, 4)
        self.assertEqual(issue_decision.issuedecisionattribute.is_new, True)

        # Tests RatingDecision
        self.assertEqual(decision_1.decided_lt, 4)
        self.assertEqual(decision_1.esma_rating_identifier, 4)
        self.assertEqual(decision_1.is_current, True)
        self.assertEqual(decision_1.decisionattributes.is_new_preliminary, True)
        self.assertEqual(decision_1.decisionattributes.is_new, False)
        self.assertEqual(decision_1.decisionattributes.is_lt_upgrade, False)

        # Create a public rating
        decision_2 = RatingDecision.objects.create(
            initiated_by_id=1,

            issuer=self.issuer_corporate_obj,

            event_type_id=1,
            rating_type_id=1,

            event='A public bond issue.',

            date_time_committee=timezone.now(),
            date_time_committee_confirmed=True,
            date_time_published=timezone.now(),

            proposed_lt_outlook=1,
            proposed_st=1,

            decided_lt_outlook=1,
            decided_st=1,

            chair_id=1,
            chair_confirmed=True,

            primary_analyst_id=1,
            secondary_analyst_id=1,

            recommendation_rationale='Recommendation.',
            committee_comments='Committee comments.',
        )

        RatingDecisionIssue.objects.create(
            rating_decision=decision_2,
            seniority_id=1,
            proposed_lt=4,
            decided_lt=5,
        )

        # We're creating a new object so the one
        # we created is not current anymore
        decision_1.is_current=False
        decision_1.save()

        # Manual override
        decision_2.decided_lt = 8
        decision_2.decided_lt_outlook = 3
        decision_2.decided_st = 1
        decision_2.is_current=True
        decision_2.save()

        # needed to update the DecisionAttributes model
        refresh_decision_attributes(decision_2)

        # Add decisions for the issue level
        update_issue_rating(decision_2)

        # Refresh data from db
        issue_decision = IssueDecision.objects.get(pk=1)
        issue_decision_2 = IssueDecision.objects.get(pk=2)

        # Tests IssueDecision

        # Make sure the just created decision is flagged as current
        self.assertEqual(issue_decision_2.is_current, True)

        # Make sure the previous rating id has been set
        self.assertEqual(issue_decision_2.previous_rating, issue_decision)

        # Make sure the old decision is not flagged as current
        self.assertEqual(issue_decision.is_current, False)

        # Make sure this is marked as a downgrade
        self.assertEqual(issue_decision_2.issuedecisionattribute.is_lt_downgrade, True)
        self.assertEqual(issue_decision_2.issuedecisionattribute.is_lt_upgrade, False)

        self.assertEqual(decision_2.decided_lt, 8)
        self.assertEqual(decision_2.is_current, True)
        self.assertEqual(decision_2.esma_rating_identifier, decision_1.id)
        self.assertEqual(decision_2.esma_rating_identifier, decision_1.esma_rating_identifier)
        self.assertEqual(decision_2.decisionattributes.is_lt_upgrade, False)
        self.assertEqual(decision_2.decisionattributes.is_lt_downgrade, True)
        self.assertEqual(decision_2.decisionattributes.is_outlook_change, True)
        self.assertEqual(decision_2.decisionattributes.is_st_upgrade, True)

        # Put rating on watch
        decision_3 = RatingDecision.objects.create(
            initiated_by_id=1,

            issuer=self.issuer_corporate_obj,

            event_type_id=1,
            rating_type_id=1,

            event='A public bond issue.',

            date_time_committee=timezone.now(),
            date_time_committee_confirmed=True,
            date_time_published=timezone.now(),

            proposed_lt_outlook=1,
            proposed_st=1,

            decided_lt_outlook=1,
            decided_st=1,

            chair_id=1,
            chair_confirmed=True,

            primary_analyst_id=1,
            secondary_analyst_id=1,

            recommendation_rationale='Recommendation.',
            committee_comments='Committee comments.',
        )

        RatingDecisionIssue.objects.create(
            rating_decision=decision_3,
            seniority_id=1,
            proposed_lt=4,
            decided_lt=4,
        )

        # We're creating a new object so the one
        # we created is not current anymore
        decision_2.is_current=False
        decision_2.save()

        # Manual override
        decision_3.decided_lt = 8
        decision_3.decided_lt_outlook = 5
        decision_3.decided_st = 1
        decision_3.is_current=True
        decision_3.save()

        # needed to update the DecisionAttributes model
        refresh_decision_attributes(decision_3)

        # Add decisions for the issue level
        update_issue_rating(decision_3)

        # Reload from db
        issue_decision = IssueDecision.objects.get(pk=1)
        issue_decision_2 = IssueDecision.objects.get(pk=2)
        issue_decision_3 = IssueDecision.objects.get(pk=3)

        # Tests IssueDecision
        self.assertEqual(issue_decision.is_current, False)
        self.assertEqual(issue_decision_2.is_current, False)
        self.assertEqual(issue_decision_3.is_current, True)

        self.assertEqual(decision_3.decided_lt, 8)
        self.assertEqual(decision_3.is_current, True)
        self.assertEqual(decision_3.decisionattributes.is_lt_upgrade, False)
        self.assertEqual(decision_3.decisionattributes.is_lt_downgrade, False)
        self.assertEqual(decision_3.decisionattributes.is_outlook_change, False)
        self.assertEqual(decision_3.decisionattributes.is_st_upgrade, False)
        self.assertEqual(decision_3.decisionattributes.is_watch, True)

        decision_3.decided_lt = 20
        decision_3.save()

        # needed to update the DecisionAttributes model
        refresh_decision_attributes(decision_3)

        decision_3_upd = RatingDecision.objects.get(pk=decision_3.pk)

        self.assertEqual(decision_3_upd.decisionattributes.is_default, True)

        decision_3.decided_lt = 21
        decision_3.save()

        # needed to update the DecisionAttributes model
        refresh_decision_attributes(decision_3)

        decision_3_upd_2 = RatingDecision.objects.get(pk=decision_3.pk)

        self.assertEqual(decision_3_upd_2.decisionattributes.is_selective_default, True)
