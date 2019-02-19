import os
import django
import environ
import sys

ROOT_DIR = str(environ.Path(__file__) - 4)
sys.path.insert(0, ROOT_DIR)

# SETUP
# ------------------------------------------------------------------------------
# Load .env variables into OS Environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.base'
django.setup()

from a_helper.mail.tasks import send_email


send_email(header='Test mail',
           body='<b>This</b> is an email',
           to='patrik.lindgren@nordiccreditrating.com',
           from_sender=None,
           cc=None,)
