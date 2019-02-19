"""This module tests the feedback sent by ESMA."""
from integrations.esma.utils.mapping_functions import get_outlook_trend
from django.test import TestCase


class MockRatingDecision:
    """Mock a RatingDecision model"""

    @property
    def decided_lt_outlook(self):
        """A representation of the outlook property."""

        return 2


class MappingFunctionUtilTest(TestCase):

    def test_get_outlook_trend(self):

        rd = MockRatingDecision()
        d = get_outlook_trend(rd)

        self.assertEqual(d, 4)
