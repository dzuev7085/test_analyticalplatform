"""This module create tasks that can be fired of using Celery."""
from celery import shared_task
from celery.utils.log import get_task_logger

from integrations.sveriges_riksbank.utils.fx import load_fx

logger = get_task_logger(__name__)


@shared_task()
def run_load_rates():
    """Function to load rates from Sveriges Riksbank."""

    load_fx()

    logger.info('Loaded FX-rates from Riksbank')
