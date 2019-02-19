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
tz = EWSTimeZone.timezone('Europe/Stockholm')

EMAIL_HOST="smtp.office365.com"
EMAIL_HOST_USER="sg-noreply@nordiccreditrating.com"
EMAIL_HOST_PASSWORD="Above32PlasticLoss"


credentials = Credentials(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
config = Configuration(server='outlook.office365.com', credentials=credentials)
account = Account(primary_smtp_address=EMAIL_HOST_USER, config=config, autodiscover=False, access_type=DELEGATE)

# create a meeting request and send it out
calendar_item = CalendarItem(
    account=account,
    folder=account.calendar,
    start=tz.localize(EWSDateTime(2018, 8, 22, 13, 30)),
    end=tz.localize(EWSDateTime(2018, 8, 22, 14, 30)),
    subject="Greetings from the rating platform",
    body="Please come to my meeting, it will be supergöy!",
    required_attendees=['sg06@nordiccreditrating.com',
                        'mille.fjeldstad@nordiccreditrating.com']
)
calendar_item.save(send_meeting_invitations=SEND_TO_ALL_AND_SAVE_COPY)
