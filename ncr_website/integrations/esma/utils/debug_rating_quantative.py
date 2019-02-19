"""Run the util functions in this folder stand-alone."""
import os
import sys
import environ
import django

ROOT_DIR = str(environ.Path(__file__) - 4)
sys.path.insert(0, ROOT_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.base'

django.setup()

from integrations.esma.models.xml_file import XMLFile  # noqa: E402

from integrations.esma.tasks import (  # noqa: E402
    update_quantatative_rating_info
)

if os.environ['ENVIRONMENT_MODE'] == 'DEV':
    # Debug / reset only
    XMLFile.objects.filter(file_type=2,).update(status_code=0,)

    # Update quantative rating info
    update_quantatative_rating_info.delay()
