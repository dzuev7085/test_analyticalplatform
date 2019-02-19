"""List all campaigns."""
from django.conf import settings as djangoSettings
from mailchimp3 import MailChimp
from dateutil import parser


def list_campaigns(filter=None):
    """This function creates a campaign in MailChimp through their API.
    :param attribute filter: an issuer internal indentifier.
    :returns: Campaign object or list of campaigns."""

    client = MailChimp(
        mc_user=djangoSettings.MC_USER,
        mc_api=djangoSettings.MC_API_KEY,
    )

    data = client.campaigns.all(get_all=True)['campaigns']

    # A filter value has been sent, only return relevant rows
    if filter:

        output = []

        for r in data:

            row = {}

            if str(filter) in r['settings']['title']:

                row['settings'] = r['settings']
                row['report_summary'] = r['report_summary']
                row['report_summary']['emails_sent'] = r['emails_sent']
                row['report_summary']['send_time'] = parser.parse(
                    r['send_time'])

                output.append(row)

        return output

    else:
        return data
