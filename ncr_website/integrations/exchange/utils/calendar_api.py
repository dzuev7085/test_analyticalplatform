"""Module to connect to Outlook and use its calendar features."""
import os

from dateutil import parser
from django.conf import settings
from exchangelib import (
    DELEGATE,
    Account,
    Credentials,
    EWSDateTime,
    EWSTimeZone,
    Configuration,
    CalendarItem,
    ExtendedProperty,
)
from exchangelib.items import (
    SEND_TO_ALL_AND_SAVE_COPY,
    SEND_ONLY_TO_CHANGED,
)


class CalendarItemID(ExtendedProperty):
    distinguished_property_set_id = 'PublicStrings'
    property_name = 'NCR Calendar ID'
    property_type = 'Integer'


# Create a custom calendar property to make searching for items easier
CalendarItem.register('ncr_calendar_item_id',
                      CalendarItemID)


class CalendarAPI:
    """API to create and edit invitations."""

    def __init__(self):
        """Init class."""
        self.account = self.connect()

        self._calendar_time = None
        self._tz = None

    def connect(self):

        credentials = Credentials(settings.EMAIL_HOST_USER,
                                  settings.EMAIL_HOST_PASSWORD)

        config = Configuration(server='outlook.office365.com',
                               credentials=credentials)

        return Account(primary_smtp_address=settings.EMAIL_HOST_USER,
                       config=config,
                       autodiscover=False,
                       access_type=DELEGATE)

    @property
    def header_prefix(self):

        if os.environ['ENVIRONMENT_MODE'] in ['UAT', 'DEV']:
            header_prefix = '*** TEST SYSTEM (env {}), NO REAL DATA *** | '. \
                format(os.environ['ENVIRONMENT_MODE'])
        else:
            header_prefix = ''

        return header_prefix

    def calendar_item(self, calendar_item_id):
        """Get a calendar item object."""

        return self.account.calendar.get(
            ncr_calendar_item_id=calendar_item_id)

    def get_or_create(self,
                      ncr_calendar_id,
                      start_time=None,
                      end_time=None):

        try:
            calendar_item = self.calendar_item(ncr_calendar_id)

        except Exception:
            # Raises exchangelib.queryset.DoesNotExist

            calendar_item = self.create_invitation(
                ncr_calendar_item_id=id,
                start_time=start_time,
                end_time=end_time)

        return calendar_item

    def update_invitation(self,
                          ncr_calendar_id,
                          start_time=None,
                          end_time=None,
                          header=None,
                          body=None, ):

        calendar_item = self.calendar_item(
            ncr_calendar_id)

        if start_time:
            calendar_item.start = self.get_calendar_time(start_time)

        if end_time:
            calendar_item.end = self.get_calendar_time(end_time)

        if header:
            calendar_item.subject = self.header_prefix + header

        if body:
            calendar_item.body = body

        calendar_item.save(
            send_meeting_invitations=SEND_TO_ALL_AND_SAVE_COPY)

        return calendar_item

    def add_attendee(self, ncr_calendar_id, attendee_email):
        calendar_item = self.calendar_item(ncr_calendar_id)

        _current_attendees = self.get_attendees(ncr_calendar_id)
        _current_attendees.append(attendee_email)

        calendar_item.required_attendees = _current_attendees

        calendar_item.save(
            send_meeting_invitations=SEND_ONLY_TO_CHANGED)

    def remove_attendee(self, ncr_calendar_id, attendee_email):
        calendar_item = self.calendar_item(ncr_calendar_id)

        _current_attendees = self.get_attendees(ncr_calendar_id)

        try:
            _current_attendees.remove(attendee_email)

            calendar_item.required_attendees = _current_attendees

            calendar_item.save(
                send_meeting_invitations=SEND_ONLY_TO_CHANGED)

        except ValueError:
            pass

    def get_calendar_time(self, date_time):
        """Return a string date and time in Exchangelib format."""

        # Set timezone
        self._tz = EWSTimeZone.timezone('Europe/Stockholm')
        self._calendar_time = parser.parse(date_time)

        return self._tz.localize(
            EWSDateTime(
                self._calendar_time.year,
                self._calendar_time.month,
                self._calendar_time.day,
                self._calendar_time.hour,
                self._calendar_time.minute
            )
        )

    def get_attendees(self, ncr_calendar_id):
        """Get a list of required attendees."""

        _ATTENDEE_LIST = []

        calendar_item = self.calendar_item(ncr_calendar_id)

        for a in calendar_item.required_attendees:
            _ATTENDEE_LIST.append(a.mailbox.email_address)

        return _ATTENDEE_LIST

    def create_invitation(self,
                          ncr_calendar_item_id,
                          attendee,
                          header,
                          body,
                          start_time=None,
                          end_time=None, ):
        """Create an outlook invitation."""

        # create a meeting request and send it out
        calendar_item = CalendarItem(
            account=self.account,
            folder=self.account.calendar,

            is_online_meeting=True,
            ncr_calendar_item_id=ncr_calendar_item_id,

            reminder_minutes_before_start=15,
            reminder_is_set=True,

            subject=self.header_prefix + header,
            body=body,

            required_attendees=[attendee],
        )

        if start_time:
            calendar_item.start = self.get_calendar_time(start_time)

        if end_time:
            calendar_item.start = self.get_calendar_time(end_time)

        calendar_item.save(
            send_meeting_invitations=SEND_TO_ALL_AND_SAVE_COPY)

        return calendar_item
