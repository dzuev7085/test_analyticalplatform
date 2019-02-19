#!/usr/bin/python
"""This module allows manually downloading data from Riksbanken."""
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

from integrations.norges_bank.tasks import run_load_fx  # noqa: E402

run_load_fx.delay()
