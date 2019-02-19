from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from celery import shared_task
from celery.utils.log import get_task_logger

from dateutil import parser

from exchangelib import (
    DELEGATE,
    Account,
    Credentials,
    EWSDateTime,
    EWSTimeZone,
    Configuration,
    CalendarItem
)
from exchangelib.items import SEND_TO_ALL_AND_SAVE_COPY

import os

logger = get_task_logger(__name__)


@shared_task(autoretry_for=(Exception,),
             default_retry_delay=30,
             max_retries=10)
def send_email(header=None, body=None, to=None, from_sender=None, cc=None,
               attachments=None):
    """Send an email using the Intility mail servers."""

    logger.info("Trying to send email")

    args = {}

    # The EmailMessage expects a list
    if not type(to) == list:
        to = [to]

    # The EmailMessage expects a list
    if cc is not None:
        if not type(cc) == list:
            cc = [cc]

        args['cc'] = cc

    # Todo: contact Intillity about this
    if from_sender is None:
        from_sender = 'Nordic Credit Rating <no-reply@nordiccreditrating.com>'

    if os.environ['ENVIRONMENT_MODE'] in ['UAT', 'DEV']:
        header_prefix = '*** TEST SYSTEM (env {}), NO REAL DATA *** | '.\
            format(os.environ['ENVIRONMENT_MODE'])
    else:
        header_prefix = ''

    args['subject'] = header_prefix + header
    args['body'] = strip_tags(body)
    args['from_email'] = from_sender
    args['to'] = to

    email = EmailMultiAlternatives(**args)
    email.attach_alternative(body, "text/html")

    if attachments is not None:
        for attachment in attachments:
            email.attach_file(attachment)

    email.send()
    logger.info("   Finished mailing process")


@shared_task(default_retry_delay=30, max_retries=10)
def send_outlook_invitation(header="Invitation",
                            body="Please come to my meeting",
                            attendee=None,
                            start_time=None,
                            end_time=None):
    """Sends an outlook invitation."""

    logger.info("Sent outlook invitation")

    tz = EWSTimeZone.timezone('Europe/Stockholm')
    start_time = parser.parse(start_time)
    end_time = parser.parse(end_time)

    credentials = Credentials(settings.EMAIL_HOST_USER,
                              settings.EMAIL_HOST_PASSWORD)
    config = Configuration(server='outlook.office365.com',
                           credentials=credentials)
    account = Account(primary_smtp_address=settings.EMAIL_HOST_USER,
                      config=config,
                      autodiscover=False,
                      access_type=DELEGATE)

    if os.environ['ENVIRONMENT_MODE'] in ['UAT', 'DEV']:
        header_prefix = '*** TEST SYSTEM (env {}), NO REAL DATA *** | '.\
            format(os.environ['ENVIRONMENT_MODE'])
    else:
        header_prefix = ''

    # create a meeting request and send it out
    calendar_item = CalendarItem(
        account=account,
        folder=account.calendar,
        start=tz.localize(EWSDateTime(start_time.year,
                                      start_time.month,
                                      start_time.day,
                                      start_time.hour + 1,
                                      start_time.minute)),
        end=tz.localize(EWSDateTime(end_time.year,
                                    end_time.month,
                                    end_time.day,
                                    end_time.hour + 2,
                                    end_time.minute)),
        subject=header_prefix + header,
        body=body,
        required_attendees=[attendee]
    )

    calendar_item.save(
        send_meeting_invitations=SEND_TO_ALL_AND_SAVE_COPY)

    logger.info("Sent calendar invitation")
