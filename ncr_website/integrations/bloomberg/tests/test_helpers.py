"""This module tests the helper functions for Bloomberg."""
import os
from datetime import datetime

from django.test import TestCase

from integrations.bloomberg.utils.helpers import (
    return_outlook,
    bloomberg_file_name,
)


class MockRatingDecision:
    """Mock a RatingDecision model"""

    @property
    def decided_lt_outlook(self):
        """A representation of the outlook property."""

        return 2


class HelperFunctionUtilTest(TestCase):

    def test_return_outlook(self):
        rd = MockRatingDecision()
        d = return_outlook(rd)

        self.assertEqual(d, 'STABLE')

    def test_file_name(self):
        f = bloomberg_file_name()

        e = 'Bloomberg_{}_{}.xlsx'.format(
            os.environ['ENVIRONMENT_MODE'],
            datetime.now().strftime('%Y-%m-%d')
        )

        self.assertEqual(f, e)
