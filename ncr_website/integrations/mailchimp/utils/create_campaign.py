import os
from django.conf import settings as djangoSettings
from mailchimp3 import MailChimp
from gui.templatetags.template_tags import format_reference_number
from django.utils.html import strip_tags


def create_campaign(**kwargs):
    """This function creates a campaign in MailChimp through their API."""

    client = MailChimp(
        mc_user=djangoSettings.MC_USER,
        mc_api=djangoSettings.MC_API_KEY,
    )

    # Set properties for campaign
    rating_job_id = kwargs['rating_job_id']
    header = kwargs['header']
    body = kwargs['body']
    campaign_title = format_reference_number(
        number=rating_job_id,
        object_type='rating_decision',) + ' - ' + header
    template_id = kwargs['template_id']
    issuer_type_id = kwargs['issuer_type_id']

    list_id = '801d23f631'  # Web site signup
    folder_id = '7024652103'  # Rating
    saved_segment_id = None

    if issuer_type_id == 1:
        # Corporate
        saved_segment_id = 29557

    elif issuer_type_id == 2:
        # Financial

        saved_segment_id = 29565

    elif issuer_type_id == 3:
        # Real estate

        saved_segment_id = 29569

    # Override these settings in test environment
    if os.environ['ENVIRONMENT_MODE'] != 'PROD':
        folder_id = '53b0a3465b'
        list_id = '42a98c90a0'
        saved_segment_id = 29573

    data = {
        'recipients': {
            'list_id': list_id,
            'segment_opts': {
                'saved_segment_id': saved_segment_id,
            }
        },
        'settings':
            {
                'title': campaign_title,
                'from_name': 'Nordic Credit Rating',
                'reply_to': 'post@nordiccreditrating.com',
                'template_id': template_id,

                # Mail headline
                # No more than 150 chars according to specs
                'subject_line': header[0:150],

                # No more than 150 chars according to specs
                'preview_text': strip_tags(body[0:150]),

                'folder_id': folder_id,
            },
        'type': 'regular',
    }

    return client.campaigns.create(data)
