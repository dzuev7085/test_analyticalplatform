from django.conf.urls import url

from . import views

urlpatterns = [

    # Download encrypted file from S3
    url(r'^issuers/documents/download/(?P<file_id>\d+)/$',
        views.SecretFileView.as_view(),
        name="issuer_document_analytical_download"),

    # Delete document physically and virtually
    url(r'^issuers/documents/delete/(?P<file_id>\d+)/$',
        views.IssuerDocumentAnalyticalDeleteView.as_view(),
        name="issuer_document_analytical_delete"),

    # Edit document properties
    url(r'^issuers/documents/edit/(?P<file_id>\d+)/'
        r'(?P<document_type_id>\d+)/$',
        views.IssuerDocumentAnalyticalEditView.as_view(),
        name="issuer_document_analytical_edit"),

]
