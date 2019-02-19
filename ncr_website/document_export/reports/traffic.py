import datetime
import os
import tempfile

from django.conf import settings as djangoSettings
from django.http import HttpResponse
from django.template.loader import get_template

from integrations.google.analytics.utils.charts.pageviews_users import \
    pageviews_users
from integrations.google.analytics.utils.charts.world_map import world_map
from integrations.google.analytics.utils.create_csv import create_csv
from integrations.mailchimp.utils.list_campaigns import list_campaigns
from integrations.pdfreactor.utils.helper_function import html_file_2_pdf
from issuer.models import Issuer


def traffic_report(request, issuer_pk):
    """Generate an external report."""

    template_file = 'issuer/reports/traffic.html'

    issuer_obj = Issuer.objects.get(pk=issuer_pk)

    campaigns = list_campaigns(filter=issuer_obj.internal_identifier)

    df = create_csv(issuer_obj)

    # Replace all Jinja2 variables with relevant data
    context = {
        'environment': djangoSettings.ENVIRONMENT_MODE,
        'style': {
            'top_color': '#37474F'
        },
        'content': {
            'top_header': 'traffic report',
            'report_date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'report_title': 'Traffic report for ' + issuer_obj.legal_name,
            'issuer': {
                'data': issuer_obj,
            },
            'campaigns': campaigns,
            'charts': {
                'world_map': world_map(df, return_base64=True),
                'pageviews_users': pageviews_users(df, return_base64=True),
            }
        }
    }

    # Return formatted as html
    rendered_html = get_template(template_file).render(context)

    f = tempfile.NamedTemporaryFile(mode='w+t',
                                    suffix='.html')
    f.write(rendered_html)
    f.read()

    # Generate a unique file name
    target_file = 'Web traffic report for {}, extracted on {} at {}.pdf'.\
        format(
            issuer_obj.legal_name,
            datetime.datetime.today().strftime('%Y-%m-%d'),
            datetime.datetime.today().strftime('%H%M'), )
    html_file_2_pdf(f.name, target_file)

    from document_export.util import compress_pdf
    # Make pdf file much smaller
    compress_pdf(target_file)

    response = HttpResponse(content=open(target_file, 'rb'))
    response['Content-Type'] = 'application/pdf'
    response['Content-Disposition'] = 'inline; filename="%s"' % target_file

    os.unlink(target_file)

    return response
