from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect

import os

def switch_user(request):
    """Allow to switch between different user roles
    in dev/UAT environments."""

    # This must only work in DEV and UAT for security reasons
    if os.environ['ENVIRONMENT_MODE'] in ['UAT', 'DEV']:

        user = authenticate(username=request.GET['username'],
                            password='abc123')
        login(request, user)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
