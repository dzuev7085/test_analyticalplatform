from logging import getLogger

from django import http
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import DeleteView, RedirectView

from a_helper.modal_helper.views import AjaxUpdateView, AjaxCreateView
from integrations.s3.utils.helpers import generate_presigned_url
from config.settings.base import AWS_ANALYTICAL_MEDIA_LOCATION
from upload.models import SecurityClass

from .forms import (
    EditAnalyticalDocumentForm,
    EditAnalyticalDocumentManagementMeetingForm,
    RatingDecisionAddDocument
)
from .models import AnalyticalDocument

logger = getLogger('django.request')


# pylint: disable=too-many-ancestors
class IssuerDocumentAnalyticalDeleteView(DeleteView):
    """Delete the file row from the database and from S3."""
    model = AnalyticalDocument
    pk_url_kwarg = 'file_id'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponseRedirect(
            reverse_lazy('issuer_view',
                         kwargs={'pk': self.object.issuer.id}) +
            '#documents')


class SecretFileView(RedirectView):  # pylint: disable=too-many-ancestors
    permanent = False

    def get_redirect_url(self, **kwargs):

        return generate_presigned_url(kwargs['filepath'])

    def get(self, request, *args, **kwargs):
        m = get_object_or_404(AnalyticalDocument, pk=kwargs['file_id'])

        if m.upload:
            filepath = AWS_ANALYTICAL_MEDIA_LOCATION + '/' + str(m.upload)
            url = self.get_redirect_url(filepath=filepath)

            # The below is taken straight from RedirectView.
            if url:
                if self.permanent:
                    return http.HttpResponsePermanentRedirect(url)
                else:
                    return http.HttpResponseRedirect(url)
            else:
                logger.warning(
                    'Gone: %s',
                    self.request.path,
                    extra={'status_code': 410, 'request': self.request})
                return http.HttpResponseGone()
        else:
            raise http.Http404


# pylint: disable=too-many-ancestors
class IssuerDocumentAnalyticalEditView(AjaxUpdateView):

    model = AnalyticalDocument
    pk_url_kwarg = 'file_id'

    def get_form_class(self):
        if self.kwargs['document_type_id'] == '8':
            return EditAnalyticalDocumentManagementMeetingForm
        else:
            return EditAnalyticalDocumentForm

    def form_valid(self, form):
        obj = form.save(commit=False)

        # We need the object instance to save the event, hence saving here
        obj.save()

        return super(IssuerDocumentAnalyticalEditView, self).form_valid(form)


# pylint: disable=too-many-ancestors
class RatingDecisionDocument(AjaxCreateView):
    """RatingDecisionDocument class."""

    model = AnalyticalDocument
    pk_url_kwarg = 'file_id'
    form_class = RatingDecisionAddDocument

    def get_form_kwargs(self):
        """Pass kwargs to form set."""
        kwargs = super(RatingDecisionDocument, self).get_form_kwargs()

        # update the kwargs for the form init method with yours
        kwargs.update(self.kwargs)  # self.kwargs contains all url conf params

        return kwargs

    def form_valid(self, form):
        """Process step if form is valid."""

        document_form = form.save(commit=False)

        security_class = SecurityClass.objects.get(
            pk=form.cleaned_data['security_class_id'])

        document_form.uploaded_by = self.request.user
        document_form.security_class = security_class

        AnalyticalDocument.objects.filter(
            rating_decision__id=document_form.rating_decision_id,
            document_type__id=document_form.document_type_id).delete()

        # We're doing an upload and replace, so delete old document
        # and then upload new one.
        document_form.save()

        return super(RatingDecisionDocument, self).form_valid(form)
