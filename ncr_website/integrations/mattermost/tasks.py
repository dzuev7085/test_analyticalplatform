"""This module create tasks that can be fired of using Celery."""
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings as djangoSettings

from integrations.mattermost.utils.post_message import post_message

logger = get_task_logger(__name__)


@shared_task(autoretry_for=(Exception,),
             default_retry_delay=30,
             max_retries=10)
def run_post_message(channel, text):
    """Function to set off a task to create a campaign."""

    post_message(djangoSettings.MATTERMOST_WEBHOOK,
                 channel,
                 text)

    logger.info('Posted message to Mattermost')
