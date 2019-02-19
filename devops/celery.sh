#!/bin/sh
cd ./../ncr_website && celery -A config worker -l info -B --scheduler django_celery_beat.schedulers:DatabaseScheduler & cd ./../ncr_website && flower -A config --port=5555 ; fg
