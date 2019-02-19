"""This module create tasks that can be fired of using Celery."""
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task()
def run_load_fx():
    """Function to load rates from Norges Bank."""

    from integrations.norges_bank.utils.fx import load_fx

    load_fx()

    logger.info('Loaded FX-rates from Norges Bank')
