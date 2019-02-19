from django.conf.urls import url
from .views import switch_user


urlpatterns = [

    # Download encrypted file from S3
    url(r'^dev_uat/switch_user/$',
        switch_user,
        name="dev_uat_switch_user"),

]
