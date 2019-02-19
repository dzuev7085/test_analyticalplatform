"""Test util functions."""
from user_profile.utils import get_full_name
import unittest


class MockUser:
    """Mock user."""

    @property
    def first_name(self):
        return 'Patrik'

    @property
    def last_name(self):
        return 'Lindgren'


class TestUtils(unittest.TestCase):

    def test_get_full_name(self):

        user = MockUser()

        self.assertEqual(get_full_name(user), 'Patrik Lindgren')
