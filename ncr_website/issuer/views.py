# DJANGO CORE
from django.urls import reverse_lazy
from django.views.generic import ListView
from pygleif import GLEIF
from django.utils import timezone

from a_helper.modal_helper.views import AjaxCreateView, AjaxUpdateView

from . import forms
from .models import Analyst, Event, Issuer, OnboardingProcess
import os

from gui.templatetags.template_tags import has_group

from a_helper.mail.tasks import send_email

from rating_process.const import (
    ENGAGEMENT_LETTER_HEADER,
    ENGAGEMENT_LETTER_BODY
)
from pyfindata import (
    AnalyzeCompany,
    ResultStatement
)
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from django.contrib.auth.models import User

from datalake import DB_CONNECTION
from issuer.models.address import Address
from issuer.models.classification import Classification


class IssuerCreateView(SuccessMessageMixin, AjaxCreateView):  # pylint: disable=too-many-ancestors # noqa: E501
    """IssuerCreateView class."""

    form_class = forms.AddIssuerForm
    success_url = reverse_lazy('company_all')
    success_message = "Setting up of %(legal_name)s was sucessful"

    def get_success_message(self, cleaned_data):
        """Custom get_success_message method."""

        return self.success_message % dict(
            cleaned_data,
            legal_name=self.object.legal_name,
        )

    def form_valid(self, form):
        """Custom form_valid method."""

        obj = form.save(commit=False)

        gleif_data = GLEIF(obj.lei)

        # If the person setting up is a commercial, take that person
        # else, do nothing
        group_list = self.request.user.groups.all().values('name')
        user_groups = []
        for group in group_list:
            user_groups.append(group['name'])

        if 'Commercial' in user_groups:
            obj.relationship_manager = self.request.user
        else:
            pass

        obj.legal_name = gleif_data.entity.legal_name
        obj.short_name = gleif_data.entity.legal_name

        # We need the object instance to save the event, hence saving here
        obj.save()

        # Log the event
        Event.objects.create(
            issuer=obj,
            event_type_id=1,
            triggered_by_user=self.request.user
        )

        return super(IssuerCreateView, self).form_valid(form)


class AllCompanies(ListView):
    """List all issuers."""

    model = Issuer
    template_name = 'issuer/list_all.html'

    def get_queryset(self, **kwargs):
        """Custom get_queryset method."""

        return Issuer.objects.list_all()


class AllCompaniesRating(ListView):
    """List all issuers."""

    model = Issuer
    template_name = 'issuer/list_all.html'

    def get_queryset(self, **kwargs):
        """Custom get_queryset method."""

        return Issuer.objects.list_all_rating()


class AllCompaniesFinancials(ListView):
    """List all issuers."""

    model = Issuer
    template_name = 'issuer/list_all_financial.html'

    def get_queryset(self, **kwargs):
        """Custom get_queryset method."""

        return Issuer.objects.all().filter(
            issuer_type__id__in=[1, 3]).order_by(
            'gics_sub_industry', 'legal_name').\
            select_related('gics_sub_industry').select_related(
            'classification')

    def get_context_data(self, **kwargs):
        """Custom get_context_data method."""

        # Call the base implementation first to get the context
        data = super().get_context_data(**kwargs)

        lei_codes = []
        for c in self.object_list:
            lei_codes.append(c.lei)

        INPUT = ResultStatement(DB_CONNECTION,
                                lei_codes,
                                '2005-12-31',
                                '2018-12-31')
        data_dict = {}
        for lei in INPUT.output:
            DATA = AnalyzeCompany(INPUT.output[lei])

            # We're only interested in the last available period
            data_dict[lei] = DATA.financial_data.period[
                len(DATA.financial_data.period)-1
            ]

        data['financials'] = data_dict

        # Create any data and add it to the context
        return data


# Primary analyst has been updated
# pylint: disable=too-many-ancestors
class PrimaryAnalystUpdateView(AjaxUpdateView):

    model = Analyst
    form_class = forms.EditAnalystForm
    pk_url_kwarg = 'analyst_pk'

    def form_valid(self, form):
        obj = form.save(commit=False)

        # We need the object instance to save the event, hence saving here
        obj.save()

        # Log the event
        issuer_obj = Issuer.objects.get(id=obj.issuer_id)
        Event.objects.create(
            issuer=issuer_obj,
            event_type_id=17,  # Analyst changed event
            triggered_by_user=self.request.user
        )

        return super(PrimaryAnalystUpdateView, self).form_valid(form)


# pylint: disable=too-many-ancestors
class ClientServicesUpdateView(AjaxUpdateView):

    model = Issuer
    form_class = forms.EditClientServicesForm
    pk_url_kwarg = 'issuer_pk'

    def form_valid(self, form):
        obj = form.save(commit=False)

        # We need the object instance to save the event, hence saving here
        obj.save()

        # Log the event
        issuer_obj = Issuer.objects.get(id=obj.id)
        Event.objects.create(
            issuer=issuer_obj,
            event_type_id=19,  # Client services changed event
            triggered_by_user=self.request.user
        )

        return super(ClientServicesUpdateView, self).form_valid(form)


# pylint: disable=too-many-ancestors
class GICSSubIndustryUpdateView(AjaxUpdateView):

    model = Issuer
    form_class = forms.EditGICSSubIndustry
    pk_url_kwarg = 'issuer_pk'

    def form_valid(self, form):
        obj = form.save(commit=False)

        # We need the object instance to save the event, hence saving here
        obj.save()

        # Log the event
        issuer_obj = Issuer.objects.get(id=obj.id)
        Event.objects.create(
            issuer=issuer_obj,
            event_type_id=23,  # Change GICS code
            triggered_by_user=self.request.user
        )

        return super(GICSSubIndustryUpdateView, self).form_valid(form)


# pylint: disable=too-many-ancestors
class DescriptionUpdateView(AjaxUpdateView):

    model = Issuer
    form_class = forms.EditDescription
    pk_url_kwarg = 'issuer_pk'

    def form_valid(self, form):

        obj = form.save(commit=False)

        # We need the object instance to save the event, hence saving here
        obj.save()

        return super(DescriptionUpdateView, self).form_valid(form)


# pylint: disable=too-many-ancestors
class ShortnameUpdateView(AjaxUpdateView):
    """ShortnameUpdateView view."""

    model = Issuer
    form_class = forms.EditShortName
    pk_url_kwarg = 'issuer_pk'


# pylint: disable=too-many-ancestors
class LegalnameUpdateView(AjaxUpdateView):
    """ShortnameUpdateView view."""

    model = Issuer
    form_class = forms.EditLegalName
    pk_url_kwarg = 'issuer_pk'


# pylint: disable=too-many-ancestors
class CountryUpdateView(AjaxUpdateView):
    """ShortnameUpdateView view."""

    model = Address
    form_class = forms.EditCountry
    pk_url_kwarg = 'address_id'


# pylint: disable=too-many-ancestors
class NCRPeerUpdateView(AjaxUpdateView):
    """ShortnameUpdateView view."""

    model = Classification
    form_class = forms.EditNCRPeer
    pk_url_kwarg = 'classification_id'


# pylint: disable=too-many-ancestors
class ParentUpdateView(AjaxUpdateView):
    """ShortnameUpdateView view."""

    model = Issuer
    form_class = forms.EditParent
    pk_url_kwarg = 'issuer_pk'


# pylint: disable=too-many-ancestors
class IssuerUpdateView(AjaxUpdateView):

    model = Issuer
    form_class = forms.EditIssuerForm
    pk_url_kwarg = 'issuer_pk'

    def get_form_kwargs(self):

        kwargs = super(IssuerUpdateView, self).get_form_kwargs()
        kwargs.update(self.kwargs)  # self.kwargs contains all url conf params
        kwargs.update({'field': self.kwargs['field']})

        return kwargs

    def form_valid(self, form):

        issuer_id = form.cleaned_data['issuer_pk']
        issuer_obj = Issuer.objects.get(id=issuer_id)

        obj = form.save(commit=False)

        obj.id = issuer_obj.id
        obj.save()

        return super(IssuerUpdateView, self).form_valid(form)


# pylint: disable=too-many-ancestors
class OnboardingUpdateView(AjaxUpdateView):
    """OnboardingUpdate view class."""

    model = Issuer
    form_class = forms.OnboardingForm
    pk_url_kwarg = 'issuer_pk'

    def get_form_kwargs(self):
        """Custom get_form_kwargs."""

        kwargs = super(OnboardingUpdateView, self).get_form_kwargs()
        kwargs.update({'issuer_pk': self.kwargs['issuer_pk']})
        kwargs.update({'user': self.request.user})

        return kwargs

    def form_valid(self, form):
        """Custom form_valid method."""

        issuer_pk = int(form.cleaned_data['issuer_pk'])

        issuer_obj = Issuer.objects.get(id=issuer_pk)

        onboarding_obj = OnboardingProcess.objects.get(
            issuer_id=issuer_pk)

        analyst_obj = Analyst.objects.get(
            issuer_id=issuer_pk)

        # These fields can only be edited by commercial
        if has_group(self.request.user, 'Commercial'):
            # Tick that engagement letter has been signed
            if 'lt_rating' in form.cleaned_data['requested_rating']:
                onboarding_obj.issuer_long_term = True

            # Issuer has requested a short-term rating
            if 'st_rating' in form.cleaned_data['requested_rating']:
                onboarding_obj.issuer_short_term = True

            # Issuer has requested a long-term rating
            if 'instrument_rating' in form.cleaned_data['requested_rating']:
                onboarding_obj.instrument_rating = True

            # Engagement letter has been signed
            if form.cleaned_data['engagement_letter_signed']:

                onboarding_obj.engagement_letter_signed = True
                onboarding_obj.date_time_engagement_letter_signed = \
                    timezone.now()

                # Log that the engagement letter has been signed
                Event.objects.create(
                    issuer=issuer_obj,
                    event_type_id=2,  # Engagement letter signed
                    triggered_by_user=self.request.user
                )

                # Send an email to the Chief Rating Officer to inform about
                # the rating assignment.
                to_list = []
                cro = list(User.objects.filter(
                    groups__name__in=['Chief rating officer']))
                for item in cro:
                    to_list.append(item.email)

                # send email to head of ratings
                cc = [issuer_obj.relationship_manager.email]

                # We want to notify Compliance in production
                if os.environ['ENVIRONMENT_MODE'] == 'PROD':
                    cc.append('compliance@nordiccreditrating.com')

                send_email.delay(
                    header=ENGAGEMENT_LETTER_HEADER % issuer_obj,
                    body=ENGAGEMENT_LETTER_BODY,
                    to=to_list,
                    from_sender=None,
                    cc=cc)

                messages.add_message(
                    self.request,
                    messages.INFO,
                    'An email was sent to the CRO to continue onboarding.')

            # Target delivery date has been set
            if form.cleaned_data['target_delivery_date'] is not None:
                onboarding_obj.target_delivery_date = form.cleaned_data[
                    'target_delivery_date']

        # These fields can only be edited by CRO
        if has_group(self.request.user, 'Chief rating officer'):
            # Set primary analyst
            if form.cleaned_data['primary_analyst']:
                analyst_obj.primary_analyst = form.cleaned_data[
                    'primary_analyst']

                # We have to save here for the mail below to work
                analyst_obj.save()

            if form.cleaned_data['secondary_analyst']:
                analyst_obj.secondary_analyst = form.cleaned_data[
                    'secondary_analyst']

                # We have to save here for the mail below to work
                analyst_obj.save()

            if form.cleaned_data['primary_analyst'] and \
                    form.cleaned_data['secondary_analyst']:
                onboarding_obj.date_time_onboarding_completed = timezone.now()

                analyst_obj = Analyst.objects.get(issuer=issuer_obj)

                # Send an email to notify the analysts that
                # onboarding is complete
                to_list = [analyst_obj.primary_analyst.email,
                           analyst_obj.secondary_analyst.email]
                send_email.delay(
                    header='As a part of onboarding, you have been '
                           'appointed as analysts of {}'.format(
                            issuer_obj.legal_name),
                    body='Log into the analytical platform to '
                         'start the rating job.',
                    to=to_list,
                    from_sender=None,)

                # Log that the engagement letter has been signed
                Event.objects.create(
                    issuer=issuer_obj,
                    event_type_id=26,  # Onboarding complete
                    triggered_by_user=self.request.user
                )

            messages.add_message(self.request,
                                 messages.INFO,
                                 'Onboarding of {} was completed.'.format(
                                     issuer_obj.legal_name))

        # Finally, save changes
        onboarding_obj.save()
        analyst_obj.save()

        return super(OnboardingUpdateView, self).form_valid(form)
