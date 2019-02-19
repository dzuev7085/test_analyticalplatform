from django.conf.urls import url

from .views import (
    list_assessment,
    AssessmentUpdateView,
    AssessmentCreateView,
    EditSubfactorPeerView,
    AssessmentCreateUpdateView,
    export_users_csv,
)

urlpatterns = [
    url(r'^issuer/assessment/corporate/all/(?P<type>\d+)/$',
        list_assessment,
        name='issuer_assessment_corporate_all'),

    url(r'^issuer/assessment/corporate/dl/$',
        export_users_csv,
        name='issuer_assessment_corporate_dl'),

    url(r'^issuer/assessment/corporate/add/$',
        AssessmentCreateView.as_view(),
        name='issuer_assessment_corporate_add'),

    url(r'^issuer/assessment/corporate/add/update/(?P<issuer_pk>\d+)/$',
        AssessmentCreateUpdateView.as_view(),
        name='issuer_assessment_corporate_add_update'),

    url(r'^issuer/assessment/update/(?P<assessment_pk>\d+)/$',
        AssessmentUpdateView.as_view(),
        name='issuer_assessment_update'),

    url(r'^issuer/assessment/update/peer/(?P<subfactor_id>\d+)/$',
        EditSubfactorPeerView.as_view(),
        name='issuer_assessment_peer_update'),

]
