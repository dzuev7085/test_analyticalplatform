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

from integrations.database.datalake.tasks import (
    populate_data_task
)


populate_data_task()
