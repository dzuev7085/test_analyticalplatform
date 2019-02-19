"""This module create tasks that can be fired of using Celery."""
from celery import shared_task
from celery.utils.log import get_task_logger
from integrations.mailchimp.utils.create_campaign import create_campaign
from rating_process.models.rating_decision import RatingDecision
from rating_process.models.press_release import PressRelease

logger = get_task_logger(__name__)


@shared_task(autoretry_for=(Exception,),
             default_retry_delay=30,
             max_retries=10)
def run_create_campaign(rating_decision_pk=None):
    """Function to set off a task to create a campaign."""

    rating_decision_obj = RatingDecision.objects.get(pk=rating_decision_pk)
    press_release_obj = PressRelease.objects.get(
        rating_decision=rating_decision_obj)

    create_campaign(
        rating_job_id=rating_decision_pk,
        header=press_release_obj.header,
        body=press_release_obj.pre_amble,
        template_id=52657,
        issuer_type_id=rating_decision_obj.issuer.issuer_type.pk,
    )

    logger.info('MailChimp campaign created')
