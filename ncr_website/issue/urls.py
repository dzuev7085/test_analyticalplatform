from django.conf.urls import url

from .views import IssueCreateView, IssueUpdateView, StamdataLoadView

urlpatterns = [

    # Edit issue data
    url(r'^issuers/issue/edit/(?P<issue_pk>\d+)/$',
        IssueUpdateView.as_view(),
        name="issuer_issue_edit"),

    # Add issue data
    url(r'^issuers/issue/add/(?P<issuer_pk>\d+)/$',
        IssueCreateView.as_view(),
        name="issuer_issue_add"),

    # Load data from stamdata
    url(r'^issuers/issue/stamdataload/(?P<issuer_pk>\d+)/$',
        StamdataLoadView.as_view(),
        name="issuer_issue_stamdataload"),

]
