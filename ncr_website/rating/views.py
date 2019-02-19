from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import render
from django.utils import timezone

from a_helper.modal_helper.views import (
    AjaxCreateView,
    AjaxDeleteView,
    AjaxUpdateView
)
from issuer.forms import IssuerInsiderForm
from issuer.models import Event, InsiderList, Issuer
from rating.util.generate_context import return_company_context
from upload.forms import AnalyticalDocumentForm


@login_required(login_url='/login/')
def analyse_issuer(request, pk):
    """Generate the page that contains information about an
    issuer and rating decisions."""

    context = return_company_context(request, pk)

    #####################################################
    # File upload
    # Must be initialized after rating decision
    #####################################################
    if request.method == "POST":

        issuer_obj = Issuer.objects.get(pk=pk)

        # Uploaded document
        if 'save-document' in request.POST:

            analytical_document_upload_form = AnalyticalDocumentForm(
                request.POST,
                request.FILES)

            if analytical_document_upload_form.is_valid():

                new_instance = analytical_document_upload_form.save(
                    commit=False)

                new_instance.uploaded_by = request.user
                new_instance.issuer = issuer_obj

                # 8 is based on the pk set in the loaded fixtures
                if new_instance.document_type.id == 8:
                    new_instance.date_value = timezone.now()

                new_instance.save()

        # Reload page
        return HttpResponseRedirect(
            reverse_lazy('issuer_view',
                         kwargs={'pk': issuer_obj.id}) +
            '#documents')

    return render(
        request,
        'issuer/index.html',
        context
    )


# pylint: disable=too-many-ancestors
class IssuerInsiderCreateView(AjaxCreateView):
    """IssuerInsiderCreateView class."""

    form_class = IssuerInsiderForm
    success_url = reverse_lazy('issuer_view')

    def get_form_kwargs(self):
        """get_form_kwargs method."""
        kwargs = super(IssuerInsiderCreateView, self).get_form_kwargs()
        # update the kwargs for the form init method with yours
        kwargs.update(self.kwargs)  # self.kwargs contains all url conf params

        return kwargs

    def form_valid(self, form):
        """form_valid method."""

        obj = form.save(commit=False)

        issuer_obj = form.cleaned_data['issuer']
        obj.issuer = issuer_obj

        # Log the event
        issuer_obj = Issuer.objects.get(id=obj.issuer_id)
        Event.objects.create(
            issuer=issuer_obj,
            event_type_id=20,  # Added insider person
            triggered_by_user=self.request.user
        )

        return super(IssuerInsiderCreateView, self).form_valid(form)


# pylint: disable=too-many-ancestors
class IssuerInsiderUpdateView(AjaxUpdateView):
    """IssuerInsiderUpdateView class."""

    model = InsiderList
    form_class = IssuerInsiderForm
    pk_url_kwarg = 'insider_id'

    def form_valid(self, form):
        """form_valid method."""
        obj = form.save(commit=False)

        # We need the object instance to save the event, hence saving here
        obj.save()

        # Log the event
        issuer_obj = Issuer.objects.get(id=obj.issuer_id)
        Event.objects.create(
            issuer=issuer_obj,
            event_type_id=21,  # Secondary analyst changed event
            triggered_by_user=self.request.user
        )

        return super(IssuerInsiderUpdateView, self).form_valid(form)


# pylint: disable=too-many-ancestors
class IssuerInsiderDeleteView(AjaxDeleteView):
    """IssuerInsiderDeleteView class."""
    model = InsiderList
    pk_url_kwarg = 'insider_id'
