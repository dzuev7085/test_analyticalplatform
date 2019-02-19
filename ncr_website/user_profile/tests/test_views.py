import glob
import os
from django.urls import reverse
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

GLOBAL_FIXTURES = glob.glob(settings.BASE_DIR + "/config/fixtures/*.json")
TEST_FIXTURES = glob.glob(settings.BASE_DIR + "/a_helper/test_fixtures/*.json")
FIXTURES = sorted(GLOBAL_FIXTURES) + sorted(TEST_FIXTURES)
FIXTURE_LIST = []

for f in FIXTURES:
    FIXTURE_LIST.append(os.path.abspath(f))


class UserProfileTest(TestCase):

    fixtures = FIXTURE_LIST

    def test_dashboard_view(self):
        """Make sure the dashboard view loads properly."""
        self.client.login(username='analyst1', password='abc123')

        response = self.client.get(
            reverse('dashboard'))

        self.assertEqual(response.status_code, 200)

    def test_change_password_view(self):
        """Make sure the change password view loads properly."""
        self.client.login(username='analyst1', password='abc123')

        response = self.client.get(
            reverse('change_password'))

        self.assertEqual(response.status_code, 200)

    def test_login(self):
        """Make sure the change password view loads properly."""

        response = self.client.get(
            reverse('login'))

        self.assertEqual(response.status_code, 200)

    def test_password_change_success(self):

        self.user = User.objects.get(pk=1)

        self.client.force_login(self.user)

        response = self.client.post(reverse('change_password'),
                                    {'old_password': "abc123",
                                     'new_password1': "123abc",
                                     'new_password2': "123abc"},
                                    follow=True)

        # THe form redirects when successful
        self.assertEqual(response.status_code, 200)

        messages = list(response.context['messages'])

        # Test messages
        self.assertEqual(str(messages[0]), 'Your password was successfully updated!')

    def test_password_change_fail(self):

        self.user = User.objects.get(pk=1)

        self.client.force_login(self.user)

        response = self.client.post(reverse('change_password'),
                                    {'old_password': "abc123",
                                     'new_password1': "123abc",
                                     'new_password2': "123ab"},
                                    follow=True)

        # THe form redirects when successful
        self.assertEqual(response.status_code, 200)

        messages = list(response.context['messages'])

        # Test messages
        self.assertEqual(str(messages[0]), 'Please correct the error below.')
