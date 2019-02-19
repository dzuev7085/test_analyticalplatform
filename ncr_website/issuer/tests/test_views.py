import glob
import os
from django.urls import reverse
from django.test import TestCase
from django.conf import settings

GLOBAL_FIXTURES = glob.glob(settings.BASE_DIR + "/config/fixtures/*.json")
TEST_FIXTURES = glob.glob(settings.BASE_DIR + "/a_helper/test_fixtures/*.json")
FIXTURES = sorted(GLOBAL_FIXTURES) + sorted(TEST_FIXTURES)
FIXTURE_LIST = []

for f in FIXTURES:
    FIXTURE_LIST.append(os.path.abspath(f))


class UserProfileTest(TestCase):

    fixtures = FIXTURE_LIST

    def all_views(self):
        """Make sure the dashboard view loads properly."""
        self.client.login(username='analyst1', password='abc123')  # defined in fixture or with factory in setUp()

        response = self.client.get(
            reverse('issuer_view'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('issuers_insider_create'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('issuers_insider_delete'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('company_all'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('company_all_financial_corporate'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('company_all_financial_corporate'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('issuer_pending_engagement_list'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('issuer_pending_analyst_appointment_list'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('issuer_pending_engagement_letter_update'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('issuer_pending_analyst_appointment_update'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('issuer_primary_analyst_update'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('issuer_client_services_update'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('issuer_gics_update'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('issuer_description_update'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('issuer_short_name_update'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('issuer_update_field'))
        self.assertEqual(response.status_code, 200)
