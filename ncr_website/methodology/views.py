# Django
# Python
from logging import getLogger

from django import http
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import DeleteView, DetailView, ListView, RedirectView

# Helpers
from a_helper.modal_helper.views import AjaxCreateView
from integrations.s3.utils.helpers import generate_presigned_url
from config.settings.base import AWS_ANALYTICAL_MEDIA_LOCATION
# Rating
from gui.templatetags.template_tags import has_group

from .forms import MethodologyForm
# This model
from .models import Methodology, MethodologyCategory

logger = getLogger('django.request')


class MethodologyList(ListView):  # pylint: disable=too-many-ancestors

    model = Methodology
    queryset = Methodology.objects.order_by(
        'category__name', '-date_decision').filter(
            date_deleted__isnull=True).distinct('category__name')

    template_name = 'misc/methodology/methodology_list.html'


class MethodologyDetail(DetailView):  # pylint: disable=too-many-ancestors

    model = MethodologyCategory
    pk_url_kwarg = 'category_id'

    template_name = 'misc/methodology/methodology_category_view.html'

    def get_context_data(self, **kwargs):

        # Call the base implementation first to get the context
        data = super().get_context_data(**kwargs)

        data['history'] = Methodology.objects.filter(
            date_deleted__isnull=True,
            category=self.kwargs['category_id'])

        if has_group(self.request.user, 'Chief rating officer'):
            data['allow_edit'] = True

        data['form'] = True

        # Create any data and add it to the context
        return data


# pylint: disable=too-many-ancestors
class MethodologyCreateView(AjaxCreateView):

    form_class = MethodologyForm

    def get_form_kwargs(self):

        kwargs = super(MethodologyCreateView, self).get_form_kwargs()
        kwargs.update(self.kwargs)  # self.kwargs contains all url conf params
        kwargs.update({'category_id': self.kwargs['category_id']})

        return kwargs

    def form_valid(self, form):
        obj = form.save(commit=False)

        obj.category = form.cleaned_data['category']
        obj.uploaded_by = self.request.user

        # We need the object instance to save the event, hence saving here
        obj.save()

        return super(MethodologyCreateView, self).form_valid(form)


# pylint: disable=too-many-ancestors
class MethodologyDetailDelete(DeleteView):

    model = Methodology
    pk_url_kwarg = 'file_id'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.date_deleted = timezone.now()
        self.object.save()

        return http.HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class SecretFileView(RedirectView):  # pylint: disable=too-many-ancestors
    permanent = False

    def get_redirect_url(self, **kwargs):

        return generate_presigned_url(kwargs['filepath'])

    def get(self, request, *args, **kwargs):
        m = get_object_or_404(Methodology, pk=kwargs['file_id'])

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
                logger.warning('Gone: %s',
                               self.request.path,
                               extra={'status_code': 410,
                                      'request': self.request})
                return http.HttpResponseGone()
        else:
            raise http.Http404
