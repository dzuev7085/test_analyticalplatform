import glob
import os

from django.test import TestCase

from issuer.models import (
    Issuer,
)

from credit_assessment.models.assessment import AssessmentJob
from credit_assessment.models.subscores import AssessmentSubscoreData
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
        cls.corporate_rating_assessment_obj = AssessmentJob.objects.create(
            issuer=cls.issuer_corporate_obj,
            initiated_by_id=1,
        )

        # Corporate real estate
        cls.issuer_corporate_re_obj = Issuer.objects.get(pk=2)
        cls.corporate_re_rating_assessment_obj = AssessmentJob.objects.create(
            issuer=cls.issuer_corporate_re_obj,
            initiated_by_id=1,
        )

        # Corporate real estate
        cls.issuer_financial_obj = Issuer.objects.get(pk=3)
        cls.financial_rating_assessment_obj = AssessmentJob.objects.create(
            issuer=cls.issuer_financial_obj,
            initiated_by_id=1,
        )

    def test_corporate_subscores(self):
        """ This is to test a corporate issuer."""

        self.subscores = AssessmentSubscoreData.objects.filter(
            assessment=self.corporate_rating_assessment_obj)

        # Operating environment
        self.assertTrue(isinstance(self.subscores.get(subfactor_id=1), AssessmentSubscoreData))

        # Market position
        self.assertTrue(isinstance(self.subscores.get(subfactor_id=2), AssessmentSubscoreData))

        # Operating efficiency
        self.assertTrue(isinstance(self.subscores.get(subfactor_id=3), AssessmentSubscoreData))

        # Size and diversification
        self.assertTrue(isinstance(self.subscores.get(subfactor_id=4), AssessmentSubscoreData))

        # Financial risk assessment
        self.assertTrue(isinstance(self.subscores.get(subfactor_id=27), AssessmentSubscoreData))
        self.assertTrue(isinstance(self.subscores.get(subfactor_id=28), AssessmentSubscoreData))

        # Liquidity
        self.assertTrue(isinstance(self.subscores.get(subfactor_id=6), AssessmentSubscoreData))

        # ESG
        self.assertTrue(isinstance(self.subscores.get(subfactor_id=7), AssessmentSubscoreData))

        # Peer comparison
        self.assertTrue(isinstance(self.subscores.get(subfactor_id=8), AssessmentSubscoreData))

        # Ownership support
        self.assertTrue(isinstance(self.subscores.get(subfactor_id=9), AssessmentSubscoreData))


    def test_corporate_re_subscores(self):
        """ This is to test a corporate real estate issuer."""

        self.re_subscores = AssessmentSubscoreData.objects.filter(
            assessment=self.corporate_re_rating_assessment_obj)

        # Operating environment
        self.assertTrue(isinstance(self.re_subscores.get(subfactor_id=1), AssessmentSubscoreData))

        # Market position, size and diversification
        self.assertTrue(isinstance(self.re_subscores.get(subfactor_id=10), AssessmentSubscoreData))

        # Portfolio assessment
        self.assertTrue(isinstance(self.re_subscores.get(subfactor_id=11), AssessmentSubscoreData))

        # Operating efficiency
        self.assertTrue(isinstance(self.re_subscores.get(subfactor_id=3), AssessmentSubscoreData))

        # Financial risk assessment
        self.assertTrue(isinstance(self.re_subscores.get(subfactor_id=27), AssessmentSubscoreData))
        self.assertTrue(isinstance(self.re_subscores.get(subfactor_id=28), AssessmentSubscoreData))

        # Liquidity
        self.assertTrue(isinstance(self.re_subscores.get(subfactor_id=6), AssessmentSubscoreData))

        # ESG
        self.assertTrue(isinstance(self.re_subscores.get(subfactor_id=7), AssessmentSubscoreData))

        # Peer comparison
        self.assertTrue(isinstance(self.re_subscores.get(subfactor_id=8), AssessmentSubscoreData))

        # Ownership support
        self.assertTrue(isinstance(self.re_subscores.get(subfactor_id=9), AssessmentSubscoreData))

    def test_financial_subscores(self):
        """ This is to test a financial issuer."""

        self.fin_subscores = AssessmentSubscoreData.objects.filter(
            assessment=self.financial_rating_assessment_obj)

        # National factors
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=12), AssessmentSubscoreData))

        # Regional, cross border, sector
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=13), AssessmentSubscoreData))

        # Capital
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=14), AssessmentSubscoreData))

        # Funding and liquidity
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=15), AssessmentSubscoreData))

        # Risk governance
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=16), AssessmentSubscoreData))

        # Credit risk
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=17), AssessmentSubscoreData))

        # Market risk
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=18), AssessmentSubscoreData))

        # Other risks
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=19), AssessmentSubscoreData))

        # Market position
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=20), AssessmentSubscoreData))

        # Earnings
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=21), AssessmentSubscoreData))

        # Loss performance
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=22), AssessmentSubscoreData))

        # Transitions
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=23), AssessmentSubscoreData))

        # Borderline assessments
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=24), AssessmentSubscoreData))

        # Material credit enhancement
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=25), AssessmentSubscoreData))

        # Rating caps
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=26), AssessmentSubscoreData))

        # Peer comparison
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=8), AssessmentSubscoreData))

        # Ownership support
        self.assertTrue(isinstance(self.fin_subscores.get(subfactor_id=9), AssessmentSubscoreData))
