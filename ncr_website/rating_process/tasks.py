"""Tasks for rating process."""

from celery import shared_task
from celery.utils.log import get_task_logger
from rating_process.models.decision_attributes import DecisionAttributes
from rating_process.models.rating_decision_issue import RatingDecisionIssue
from rating_process.models.rating_decision_issue_link_attribute import (
    IssueDecisionAttribute
)
from .models.issue_decision import IssueDecision
from issue.models import Issue

logger = get_task_logger(__name__)


@shared_task
def refresh_decision_attributes(rating_decision):
    """Refresh the properties of a RatingDecision. Not implemented as a signal
    as the order of execution seems random with signals and certain values need
    to have been saved before we run this function."""

    # Use get or create for backwards compatibility
    decision_attributes, created = DecisionAttributes.objects.get_or_create(
        rating_decision=rating_decision)

    # Is the rating decision just created linked to a previous rating?
    previous_decision_obj = rating_decision.previous_rating

    # This is a brand new rating, determine if preliminary or new
    if previous_decision_obj is None:

        if rating_decision.is_preliminary:
            decision_attributes.is_new_preliminary = True

        elif rating_decision.event_type.id == 1:
            decision_attributes.is_new = True

    else:

        if rating_decision.decided_lt < previous_decision_obj.decided_lt:
            decision_attributes.is_lt_upgrade = True
        elif rating_decision.decided_lt > previous_decision_obj.decided_lt:
            decision_attributes.is_lt_downgrade = True
        elif rating_decision.decided_lt == previous_decision_obj.decided_lt:
            decision_attributes.is_lt_affirmation = True

        if rating_decision.decided_st < previous_decision_obj.decided_st:
            decision_attributes.is_st_upgrade = True
        elif rating_decision.decided_st > previous_decision_obj.decided_st:
            decision_attributes.is_st_downgrade = True
        elif rating_decision.decided_st == previous_decision_obj.decided_st:
            decision_attributes.is_st_affirmation = True

        if rating_decision.decided_lt_outlook in [4, 5, 6]:
            decision_attributes.is_watch = True

        elif abs(rating_decision.decided_lt_outlook -
                 previous_decision_obj.decided_lt_outlook) != 0:

            decision_attributes.is_outlook_change = True

        if rating_decision.decided_lt == 20:
            decision_attributes.is_default = True

        if rating_decision.decided_lt == 21:
            decision_attributes.is_selective_default = True

        if rating_decision.decided_lt == 200:
            decision_attributes.is_withdrawal = True

    # Save our changes
    decision_attributes.save()


@shared_task
def refresh_issue_decision_attributes(issue_rating_decision,
                                      is_between_committees=False,):
    """Set the attributes of a issue rating decision

    This function takes a decision on the issue level."""

    # Use get or create for backwards compatibility
    decision_attributes, created = \
        IssueDecisionAttribute.objects.get_or_create(
            rating_decision_issue=issue_rating_decision)

    # Is the rating decision just created linked to a previous rating?
    previous_decision_obj = issue_rating_decision.previous_rating

    # This is a brand new rating, determine if preliminary or new
    if previous_decision_obj is None:

        # TODO: does this work for all use cases?
        # we should verify this when the first preliminary issue
        # rating pops up
        if issue_rating_decision.is_preliminary:
            decision_attributes.is_new_preliminary = True
        else:
            decision_attributes.is_new = True

    else:

        # Reset all values
        decision_attributes.is_lt_upgrade = False
        decision_attributes.is_lt_downgrade = False
        decision_attributes.is_lt_affirmation = False
        decision_attributes.is_default = False
        decision_attributes.is_selective_default = False
        decision_attributes.is_withdrawal = False
        decision_attributes.is_matured = False
        decision_attributes.is_between_committees = False

        # Only set withdrawn and, if applicable, matured when
        # rating is set to 'NR'
        if issue_rating_decision.decided_lt == 200:
            decision_attributes.is_withdrawal = True

        else:

            if issue_rating_decision.decided_lt < \
                    previous_decision_obj.decided_lt:
                    decision_attributes.is_lt_upgrade = True
            elif issue_rating_decision.decided_lt > \
                    previous_decision_obj.decided_lt:
                    decision_attributes.is_lt_downgrade = True
            elif issue_rating_decision.decided_lt == \
                    previous_decision_obj.decided_lt:
                    decision_attributes.is_lt_affirmation = True

        if issue_rating_decision.decided_lt == 20:
            decision_attributes.is_default = True

        # Issue has matured
        if issue_rating_decision.issue.is_matured:
            decision_attributes.is_matured = True

            # The message sent to ESMA a withdrawal message, so mark the
            # attribute for this
            decision_attributes.is_withdrawal = True

        if issue_rating_decision.decided_lt == 21:
            decision_attributes.is_selective_default = True

    # Flag to mark that a decision was made between two committees
    if is_between_committees:
        decision_attributes.is_between_committees = True

    # Save our changes
    decision_attributes.save()


@shared_task
def update_issue_rating(rating_decision_obj):
    """This task assigns ratings to specific issues for an issuer.
    In this function, we've already made the just made decision
    the one that is current. Hence picking previous_rating."""

    # Loop through each seniority level for the specific decision
    for issue_seniority_lvl in RatingDecisionIssue.objects.filter(
            rating_decision=rating_decision_obj,):

        for issue in Issue.objects.filter(
            issuer=rating_decision_obj.issuer,
            seniority=issue_seniority_lvl.seniority,
                is_matured=False,):

            # Create a link object per issue
            d = IssueDecision.objects.create(
                rating_decision_issue=issue_seniority_lvl,
                issue=issue,
                is_current=True,
                decided_lt=issue_seniority_lvl.decided_lt,
                date_time_published=rating_decision_obj.
                date_time_published,
                date_time_committee=rating_decision_obj.
                date_time_committee,
                date_time_communicated_issuer=rating_decision_obj.
                date_time_communicated_issuer,
                chair=rating_decision_obj.chair,
                rationale='Automatic insert based on rating decision.',
                process_step=10,
            )

            # Has to be invoked like this rather than signal
            # as the order of signalled cannot be easily controlled
            refresh_issue_decision_attributes(d)
