#!/bin/sh
# Script to run the Django server

# Running Django's test suite in parallel-mode seems to break coverage
cd ../ && ncr_website/manage.py runserver 0.0.0.0:8000
