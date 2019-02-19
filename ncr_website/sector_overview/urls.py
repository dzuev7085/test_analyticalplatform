from django.conf.urls import url

from .views import view_subscore_list

urlpatterns = [
    url(r'^sector_overview/(?P<issuer_type_pk>\d+)/$',
        view_subscore_list, name='sector_overview'),

]
