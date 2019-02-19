from django.conf.urls import url

from .views import (
    FinancialItemEditView,
    DisplayPeerChart,
    return_chart_data_csv
)

urlpatterns = [

    # Edit an item on financial statement
    url(r'^issuers/financials/edit/'
        r'(?P<target_item>.*)/'
        r'(?P<issuer_id>\d+)/'
        r'(?P<report_date_type>.*)/'
        r'(?P<currency>.*)/'
        r'(?P<statement_type>.*)/'
        r'(?P<data_source>.*)/'
        r'(?P<date>\d{4}-\d{2}-\d{2})/$',
        FinancialItemEditView.as_view(),
        name="issuer_financials_edit"),

    url(r'^backend/chart/data/(?P<item>.*)/$',
        return_chart_data_csv,
        name="chart_test_data"),

    url(r'^backend/chart/(?P<item>.*)/'
        r'(?P<readable_name>.*)/'
        r'(?P<format_as>.*)/'
        r'(?P<issuer_id>\d+)/'
        r'(?P<chart_type>.*)/$',
        DisplayPeerChart.as_view(),
        name="peer_chart"),

]
