import os
import sys

import django
import environ

ROOT_DIR = str(environ.Path(__file__) - 4)
sys.path.insert(0, ROOT_DIR)

# SETUP
# ------------------------------------------------------------------------------
# Load .env variables into OS Environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.base'
django.setup()

from integrations.exchange.utils.calendar_api import (  # noqa: E403
    CalendarAPI
)

# CalendarAPI().create_invitation(
#    start_time='2018-11-30 13:00',
#    end_time='2018-11-30 14:00',
# )

calendar_api = CalendarAPI()

id = calendar_api.get_or_create(
    ncr_calendar_id=3,
    start_time='2018-11-30 13:00',
    end_time='2018-11-30 14:00',
)

z = calendar_api.update_invitation(ncr_calendar_id=3,
                                   header='This is a committee meeting',
                                   body='Starting from now we are meeting',
                                   start_time='2018-11-30 13:00',
                                   end_time='2018-11-30 14:00',
                                   )
j = calendar_api.get_attendees(3)
print(j)

# o = calendar_api.remove_attendee(3, 'patrik@gammelgravlingen.com')

# print(o)
