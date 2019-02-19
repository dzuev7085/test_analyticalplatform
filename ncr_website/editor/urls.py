from django.conf.urls import url

from . import views

urlpatterns = [

    # List all issuers where analysis is ongoing
    url(r'^editor/detail/(?P<pk>\d+)/$',
        views.EditorDetailView.as_view(),
        name="editor_detail"),

]
