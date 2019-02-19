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

from integrations.google.analytics.utils.charts.pageviews_users \
    import (  # noqa: E402
    pageviews_users
)
from integrations.google.analytics.utils.create_csv import (  # noqa: E402
    create_csv
)


df = create_csv()

d = pageviews_users(df)

with open("test.html", "w") as text_file:
    text_file.write(d)
