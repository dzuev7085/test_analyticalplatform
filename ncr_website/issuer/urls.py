from django.conf.urls import url

from rating.views import (
    IssuerInsiderCreateView,
    IssuerInsiderDeleteView,
    IssuerInsiderUpdateView,
    analyse_issuer,
)

from . import views

urlpatterns = [
    url(r'^issuer/(?P<pk>\d+)/$',
        analyse_issuer, name='issuer_view'),

    # Add a new issuer to the database
    url(r'^issuers/create$',
        views.IssuerCreateView.as_view(),
        name="issuers_create"),

    # Add a new issuer to the database
    url(r'^issuers/insider/add/(?P<issuer_pk>\d+)/$',
        IssuerInsiderCreateView.as_view(),
        name="issuers_insider_create"),

    # Delete an insider from the database
    url(r'^issuers/insider/delete/(?P<insider_id>\d+)/$',
        IssuerInsiderDeleteView.as_view(),
        name="issuers_insider_delete"),

    # Add a new issuer to the database
    url(r'^issuers/insider/edit/(?P<insider_id>\d+)/$',
        IssuerInsiderUpdateView.as_view(),
        name="issuers_insider_update"),

    # List all issuers
    url(r'^issuers/all/$',
        views.AllCompanies.as_view(),
        name="company_all"),

    # List all issuers with a rating
    url(r'^issuers/all/rated$',
        views.AllCompaniesRating.as_view(),
        name="company_all_rating"),

    # List all issuers but with financial data
    url(r'^issuers/all/financial$',
        views.AllCompaniesFinancials.as_view(),
        name="company_all_financial_corporate"),

    # Send data to update analysts
    url(r'^issuers/issuer_primary_analyst/update/(?P<analyst_pk>\d+)/$',
        views.PrimaryAnalystUpdateView.as_view(),
        name="issuer_primary_analyst_update"),

    # Send data to update client services
    url(r'^issuers/issuer_client_services/update/(?P<issuer_pk>\d+)/$',
        views.ClientServicesUpdateView.as_view(),
        name="issuer_client_services_update"),

    # Send data to update GICS code
    url(r'^issuers/issuer_gics_code/update/(?P<issuer_pk>\d+)/$',
        views.GICSSubIndustryUpdateView.as_view(),
        name="issuer_gics_update"),

    # Send data to update issuer_description
    url(r'^issuers/issuer_description/update/(?P<issuer_pk>\d+)/$',
        views.DescriptionUpdateView.as_view(),
        name="issuer_description_update"),

    # Send data to update issuer_description
    url(r'^issuers/shortname/update/(?P<issuer_pk>\d+)/$',
        views.ShortnameUpdateView.as_view(),
        name="issuer_short_name_update"),

    # Send data to update issuer_description
    url(r'^issuers/legal_name/update/(?P<issuer_pk>\d+)/$',
        views.LegalnameUpdateView.as_view(),
        name="issuer_legal_name_update"),

    # Send data to update issuer_description
    url(r'^issuers/parent_company/update/(?P<issuer_pk>\d+)/$',
        views.ParentUpdateView.as_view(),
        name="issuer_parent_company_update"),

    # Send data to update issuer_description
    url(r'^issuers/country/update/(?P<address_id>\d+)/$',
        views.CountryUpdateView.as_view(),
        name="issuer_country_update"),

    # Send data to update issuer_description
    url(r'^issuers/peer_free_text/update/(?P<classification_id>\d+)/$',
        views.NCRPeerUpdateView.as_view(),
        name="issuer_peer_free_text_update"),

    # Send data to update attribute of rating component
    url(r'^issuer/update/(?P<issuer_pk>(\d+))/'
        '(?P<field>.*)/$',
        views.IssuerUpdateView.as_view(),
        name='issuer_update_field'),

    # Send data to update attribute of rating component
    url(r'^issuer/onboarding/(?P<issuer_pk>(\d+))/$',
        views.OnboardingUpdateView.as_view(),
        name='issuer_onboarding'),

]
