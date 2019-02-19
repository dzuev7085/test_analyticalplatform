from django.conf.urls import url

from .views import user_dashboard, change_password

urlpatterns = [
    url(r'^user/dashboard/$', user_dashboard, name='dashboard'),

    url(r'^user/password/$', change_password, name='change_password')

]
