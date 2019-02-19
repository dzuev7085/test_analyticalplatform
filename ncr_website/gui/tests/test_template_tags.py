"""Test template for tags."""
import glob
import os

from django.test import TestCase
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

from ..templatetags.template_tags import current_rating, previous_rating
from rating_process.models.rating_decision import RatingDecision

from issuer.models import Issuer

GLOBAL_FIXTURES = glob.glob(settings.BASE_DIR + "/config/fixtures/*.json")
TEST_FIXTURES = glob.glob(settings.BASE_DIR + "/a_helper/test_fixtures/*.json")
FIXTURES = sorted(GLOBAL_FIXTURES) + sorted(TEST_FIXTURES)
FIXTURE_LIST = []

for f in FIXTURES:
    FIXTURE_LIST.append(os.path.abspath(f))


class TemplateTagTest(TestCase):

    fixtures = FIXTURE_LIST

    @classmethod
    def setUpTestData(cls):
        """setUpTestData"""

        cls.issuer = Issuer.objects.create(
            lei='549300GKFG0RYRRQ1414',
            relationship_manager_id=1,
            issuer_type_id=1,
            gics_sub_industry_id=1,
            legal_name='DNB Bank ASA')

        cls.private_issuer = Issuer.objects.create(
            lei='549300DYLI4PHWZGEZ72',
            relationship_manager_id=1,
            issuer_type_id=1,
            gics_sub_industry_id=1,
            legal_name='SpareBank 1 BV')

    def setUp(self):
        """SetUp."""
        self.issuer.refresh_from_db()
        self.private_issuer.refresh_from_db()

    def test_current_rating(self):
        """Test the function current_rating."""

        current_rating_decision = current_rating(self.issuer)

        # Make sure the rating decision is false to start with
        self.assertEqual(current_rating_decision, False)

        rating_decision_1 = RatingDecision.objects.create(
            initiated_by_id=1,

            issuer=self.issuer,

            event_type_id=1,
            rating_type_id=1,

            event='A new bond issue.',

            date_time_committee=timezone.now() - timedelta(days=10),
            date_time_committee_confirmed=True,
            date_time_published=timezone.now() - timedelta(days=10),

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

        # Manually override a few values
        rating_decision_1.is_current=True
        rating_decision_1.decided_lt=4
        rating_decision_1.save()

        current_rating_decision = current_rating(self.issuer)

        self.assertEqual(current_rating_decision.esma_rating_identifier, rating_decision_1.pk)
        self.assertEqual(current_rating_decision.event, 'A new bond issue.')
        self.assertEqual(current_rating_decision.decided_lt, 4)
        self.assertEqual(current_rating_decision.previous_rating, None)
        self.assertEqual(current_rating_decision.is_current, True)

        rating_decision_2 = RatingDecision.objects.create(
            initiated_by_id=1,

            issuer=self.issuer,

            event_type_id=1,
            rating_type_id=1,

            event='Aanother new bond issue.',

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

        # We're creating a new object so the one
        # we created is not current anymore
        rating_decision_1.is_current=False
        rating_decision_1.save()
        self.assertEqual(rating_decision_1.is_current, False)

        # Manually save these values
        rating_decision_2.is_current=True
        rating_decision_2.decided_lt = 8
        rating_decision_2.save()

        current_rating_decision_2 = current_rating(issuer=self.issuer)

        self.assertEqual(current_rating_decision_2 .esma_rating_identifier, rating_decision_1.pk)
        self.assertEqual(current_rating_decision_2.event, 'Aanother new bond issue.')
        self.assertEqual(current_rating_decision_2.decided_lt, 8)
        self.assertEqual(current_rating_decision_2.is_current, True)
        self.assertEqual(current_rating_decision_2.previous_rating, rating_decision_1)
        self.assertEqual(current_rating_decision_2.previous_rating.is_current, False)

    def test_bloomberg_current_rating(self):
        """Test the function current_rating when the issuer is private."""

        current_rating_decision = current_rating(self.private_issuer, True)

        # Make sure the rating decision is false to start with
        self.assertEqual(current_rating_decision, False)

        # Create a confidential rating
        rating_decision_1 = RatingDecision.objects.create(
            initiated_by_id=1,

            issuer=self.private_issuer,

            event_type_id=1,
            rating_type_id=3,

            event='A new secret bond issue.',

            date_time_committee=timezone.now() - timedelta(days=10),
            date_time_committee_confirmed=True,
            date_time_published=timezone.now() - timedelta(days=10),

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

        # Manual override
        rating_decision_1.is_current=True
        rating_decision_1.decided_lt = 4
        rating_decision_1.save()

        current_rating_decision = current_rating(self.private_issuer, True)

        # Make sure the current rating is still false when we are comparing data
        # for Bloomberg
        self.assertEqual(current_rating_decision, False)

        # Create a public rating
        rating_decision_2 = RatingDecision.objects.create(
            initiated_by_id=1,

            issuer=self.private_issuer,

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

        # We're creating a new object so the one
        # we created is not current anymore
        rating_decision_1.is_current=False
        rating_decision_1.save()
        self.assertEqual(rating_decision_1.is_current, False)

        previous_rating_decision = previous_rating(self.private_issuer,
                                                   is_bloomberg=True)

        # Manual override
        rating_decision_2.decided_lt = 8
        rating_decision_2.is_current=True
        rating_decision_2.save()

        current_rating_decision_2 = current_rating(self.private_issuer, True)

        # The previous rating is secret and should be false
        # The current rating is in the public domain and should
        # return an object.
        self.assertEqual(previous_rating_decision, False)
        self.assertEqual(current_rating_decision_2.event, 'A public bond issue.')
        self.assertEqual(current_rating_decision_2.previous_rating.is_current, False)
