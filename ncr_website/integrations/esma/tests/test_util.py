"""Test util functions."""
import glob
import os

from django.test import TestCase
from django.conf import settings

from integrations.esma.models.xml_file import XMLFile
from integrations.esma.utils.create_dicts import return_lead_analyst_list
from integrations.esma.utils.populate_lead_analyst import (
    populate_lead_analyst
)
from integrations.esma.const import (
    FILE_TYPE_LOOKUP,
    FILE_TYPE_RATING_QUALITATIVE
)

GLOBAL_FIXTURES = glob.glob(settings.BASE_DIR + "/config/fixtures/*.json")
TEST_FIXTURES = glob.glob(settings.BASE_DIR + "/a_helper/test_fixtures/*.json")
APP_FIXTURES = glob.glob(settings.BASE_DIR + "/integrations/esma/test_fixtures/*.json")
FIXTURES = sorted(GLOBAL_FIXTURES) + sorted(TEST_FIXTURES) + sorted(APP_FIXTURES)
FIXTURE_LIST = []

for f in FIXTURES:
    FIXTURE_LIST.append(os.path.abspath(f))

class RatingDecisionTest(TestCase):

    fixtures = FIXTURE_LIST

    def test_create_dict_lead_analyst(self):
        """Test that a dict is properly created."""

        xml_file = XMLFile.objects.create(
            file_type=FILE_TYPE_LOOKUP[FILE_TYPE_RATING_QUALITATIVE]
        )
        """Create records from source model."""
        populate_lead_analyst(xml_file)

        """Create dict."""
        LEAD_ANALYST_LIST = return_lead_analyst_list(xml_file)

        self.assertEqual(
            LEAD_ANALYST_LIST[0]['lead_analyst'][
                'lead_analyst_start_date'], '2018-05-10')
