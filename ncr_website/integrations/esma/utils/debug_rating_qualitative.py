"""Send files to ESMA.

Architecture:
- Create file pointer
- Generate diff against last successful upload
  > Point diff to file pointer
- Create XML-file
- Save XML-file to pointer
- Upload to ESMA
- Wait 5 sec
- Look for file at ESMA and download
- Mail XML-file
- Flag file pointer as success or fail
"""
import os
import sys
import environ
import django

ROOT_DIR = str(environ.Path(__file__) - 4)
sys.path.insert(0, ROOT_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.base'

django.setup()

from integrations.esma.tasks import (  # noqa: E402
    update_qualitative_rating_info
)

from integrations.esma.models.xml_file import XMLFile  # noqa: E402

if os.environ['ENVIRONMENT_MODE'] == 'DEV':
    # Debug / reset only
    XMLFile.objects.update(status_code=0,)

    # Run update qualitative
    update_qualitative_rating_info.delay()
