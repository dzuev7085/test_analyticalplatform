"""Tasks related to sending data to Bloomberg."""
from celery import shared_task
from celery.utils.log import get_task_logger

from a_helper.mail.tasks import send_email
from integrations.bloomberg.utils import run_script

logger = get_task_logger(__name__)


@shared_task
def send_to_bloomberg():
    """Send data to Bloomberg."""

    logger.info("Checking for updates relevant for Bloomberg.")

    # run_script returns False if there is no data
    file_name = run_script()

    if file_name:
        send_email(header='Daily Bloomberg report',
                   body='The attached file contains all the public '
                        'rating decisions made today.',
                   to='sg06@nordiccreditrating.com',
                   attachments=[file_name])
