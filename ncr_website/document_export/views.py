from .util import (
    committee_pack,
    external_report,
    issuer_insider_list
)
from document_export.reports.traffic import traffic_report

from rating_process.models.view_log import ViewLog


def new_pdf_view(request, rating_decision_id):
    """View committee pack."""

    ViewLog.objects.create(rating_decision_id=rating_decision_id,
                           downloaded_by=request.user)

    return committee_pack(rating_decision_id, request)


def view_external_report(request, id):
    """Show external report"""

    return external_report(request, id)


def view_issuer_insider_list(request, id):
    """Show insider list report."""

    return issuer_insider_list(request, id)


def view_traffic_report(request, issuer_pk):
    """Show issuer traffic report."""

    return traffic_report(request, issuer_pk)
