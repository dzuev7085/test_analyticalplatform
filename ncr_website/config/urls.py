from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path


urlpatterns = [
    url(r'^admin/statuscheck/', include('celerybeat_status.urls')),

    url(r'^tinymce/', include('tinymce.urls')),

    url(r'^$', LoginView.as_view(template_name='login.html'), name='login'),

    url(r'^admin/', admin.site.urls),

    url(r'^logout/$', LogoutView.as_view(next_page='/')),

    url(r'', include('upload.urls')),
    url(r'', include('issuer.urls')),
    url(r'', include('issue.urls')),
    url(r'', include('document_export.urls')),
    url(r'', include('rating_process.urls')),
    url(r'', include('editor.urls')),
    url(r'', include('sector_overview.urls')),
    url(r'', include('methodology.urls')),
    url(r'', include('user_profile.urls')),
    url(r'', include('financial_data.urls')),
    url(r'', include('credit_assessment.urls')),

    url(r'', include('a_helper.dev_uat_tools.urls')),

]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
