"""This module runs the Bloomberg integration standalone"""
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

from integrations.bloomberg.tasks import send_to_bloomberg  # noqa: E402

send_to_bloomberg.delay()
