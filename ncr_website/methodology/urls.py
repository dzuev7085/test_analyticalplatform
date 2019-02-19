from django.conf.urls import url

from .views import (
    MethodologyCreateView,
    MethodologyDetail,
    MethodologyDetailDelete,
    MethodologyList,
    SecretFileView
)

urlpatterns = [

    # Add a new issuer to the database
    url(r'^methodologies/list/$',
        MethodologyList.as_view(),
        name="methodologies_list"),

    # Add a new issuer to the database
    url(r'^methodologies/create/(?P<category_id>\d+)/$',
        MethodologyCreateView.as_view(),
        name="methodologies_create"),

    # View details about a category
    url(r'^methodologies/category/detail/(?P<category_id>\d+)/$',
        MethodologyDetail.as_view(),
        name="methodologies_detail"),

    # Download encrypted file from S3
    url(r'^methodologies/download/(?P<file_id>\d+)/$',
        SecretFileView.as_view(),
        name="methodologies_download"),

    #
    url(r'^methodologies/delete/(?P<file_id>\d+)/$',
        MethodologyDetailDelete.as_view(),
        name="methodologies_delete"),

]
