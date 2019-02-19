"""This module tests the feedback sent by ESMA."""
from integrations.esma.utils.hash_functions import (
    create_hash,
    create_hash_string,
)
from django.test import TestCase
import datetime


class HashFunctionUtilTest(TestCase):

    def test_create_hash(self):
        d = create_hash('NCR')

        self.assertEqual(d, 'babc0a1cd42ed467344558e26edeaa97')

    def test_create_hash_string(self):
        d = create_hash_string('rlist',
                               1)

        expected = (datetime.datetime.now().strftime('%Y-%m-%d') + 'rlist1' )

        self.assertEqual(d, expected)
