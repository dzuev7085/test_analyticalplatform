import os
import sys
import environ
import django

ROOT_DIR = str(environ.Path(__file__) - 4)
sys.path.insert(0, ROOT_DIR)

# SETUP
# ------------------------------------------------------------------------------
# Load .env variables into OS Environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.base'
django.setup()

from django.conf import settings as djangoSettings  # noqa: E402
from integrations.google.utils.connect import (  # noqa: E402
    return_response,
    get_service,
)
from integrations.utils.pandas import print_df  # noqa: E402
from integrations.google.analytics.utils.queries import (  # noqa: E402
    UNIQUE_PAGEVIEWS,
    # UNIQUE_EVENTS,
    # TOTAL_USERS,
)
COLUMN_NAMES = ['region', 'country', 'country_iso_code', 'date', 'path',
                'city', 'value', 'type']

# Define the auth scopes to request.
scope = 'https://www.googleapis.com/auth/analytics.readonly'
key_file_location = str(djangoSettings.ROOT_DIR + '.google_auth.json')

s = get_service(
    api_name='analytics',
    api_version='v4',
    scopes=[scope],
    key_file_location=key_file_location)


d = return_response(s, UNIQUE_PAGEVIEWS)
d['type'] = 'unique_pageviews'
d.columns = COLUMN_NAMES

print_df(d)
