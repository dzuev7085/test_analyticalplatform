from config.settings import __version__
from django.conf import settings as djangoSettings


def environment_settings(request):
    """Create fixed data structures to pass to template
    data could equally come from database queries
    web services or social APIs
    :param request:
    :return: dict
    """

    group_list = request.user.groups.all().values('name')

    user_groups = []
    for group in group_list:
        user_groups.append(group['name'])

    # Returns an error if not logged in
    try:
        FULL_NAME = request.user.get_full_name()
    except AttributeError:
        FULL_NAME = None

    items = {
        'environment': djangoSettings.ENVIRONMENT_MODE,
        'version': {
            'code': __version__
        },
        'auth': {
            'username': request.user,
            'full_name': FULL_NAME,
            'groups': user_groups
        }
    }

    return {'global_variables': items}
