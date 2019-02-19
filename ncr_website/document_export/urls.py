from django.conf.urls import url

from .views import (
    new_pdf_view,
    view_external_report,
    view_issuer_insider_list,
    view_traffic_report,
)

urlpatterns = [

    url(r'^issuer/rating_job/committee_package/'
        r'(?P<rating_decision_id>(\d+))/$',
        new_pdf_view,
        name='issuer_rating_job_committee_package'),

    url(r'^issuer/report/external/(?P<id>\d+)/$',
        view_external_report, name='issuer_report_external'),

    url(r'^issuer/report/insider/(?P<id>\d+)/$',
        view_issuer_insider_list, name='issuer_insider_list'),

    url(r'^issuer/report/traffic/(?P<issuer_pk>\d+)/$',
        view_traffic_report, name='issuer_traffic_report'),

]
