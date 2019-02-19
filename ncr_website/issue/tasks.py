"""Daily tasks related to rating decisions."""
from celery import shared_task
from celery.utils.log import get_task_logger
from issue.models import Issue
from rating_process.models.issue_decision import IssueDecision
from django.utils import timezone
from datetime import timedelta
from rating_process.tasks import refresh_issue_decision_attributes
from rating_process.const import (
    ISSUE_WR_DECISION_HEADER,
    ISSUE_WR_DECISION_BODY,
)
from a_helper.mail.tasks import send_email

logger = get_task_logger(__name__)


@shared_task
def mature_debt():
    """Task to flag all bonds having passed maturity as matured.
    Also creates a rating decision for each matured bond"""

    logger.info("Flagging bonds as matured.")

    for i in Issue.objects.matures_today():

        # Step 1, flag the bond as matured
        i.is_matured = True
        i.save()

        try:
            # See if there is an existing rating decision for this issue

            # Current rating
            ci = IssueDecision.objects.get(
                issue=i,
                is_current=True,
            )

            # Set current rating decision to not current
            ci.is_current = False
            ci.save()

            # Create a decision with rating 'NR' which means withdrawn
            # rating
            d = IssueDecision.objects.create(
                previous_rating=ci,

                rating_decision_issue=ci.rating_decision_issue,
                issue=i,

                is_current=True,
                decided_lt=200,

                date_time_committee=timezone.now(),
                date_time_communicated_issuer=timezone.now() + timedelta(
                    minutes=1),
                date_time_published=timezone.now() + timedelta(
                    minutes=2),

                # Default the decision to the same people who made the initial
                # decision
                # TODO: consider how to handle this in the long run
                # it might be that a person has left the company
                chair=ci.chair,
                proposed_by=ci.proposed_by,

                rationale='Automatic system insert due to matured issue.',

                process_step=10,
            )

            # Has to be invoked like this rather than signal
            # as the order of signalled cannot be easily controlled
            refresh_issue_decision_attributes(d)

            # Send an email to issuer with the decision
            to_list = [
                i.issuer.analyst.primary_analyst.email,
            ]

            cc_list = [
                i.issuer.analyst.primary_analyst.email,
                i.issuer.analyst.secondary_analyst.email,
                i.issuer.relationship_manager.email,
            ]

            header = ISSUE_WR_DECISION_HEADER.format(i.isin)
            body = ISSUE_WR_DECISION_BODY.format(i.isin)

            # Send notification
            send_email.delay(
                header=header,
                body=body,
                to=to_list,
                cc=cc_list,
            )

        except IssueDecision.DoesNotExist:

            # This issue has not been rated, do nothing
            pass
