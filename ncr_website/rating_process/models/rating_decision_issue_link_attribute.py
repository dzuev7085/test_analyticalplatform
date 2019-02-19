"""This model links the Issue model with the IssueSeniority model."""
from django.db import models


class IssueDecisionAttribute(models.Model):
    """Rating decisions for specific issues."""

    def __str__(self):
        return '{} | {}'.format(
            self.pk,
            self.rating_decision_issue,
        )

    # Link back to the RatingDecision
    rating_decision_issue = models.OneToOneField(
        'IssueDecision',
        on_delete=models.PROTECT,
    )

    # The rating is preliminary at this stage
    is_new_preliminary = models.BooleanField(
        default=False,
    )

    # This is the first time we assign a rating,
    is_new = models.BooleanField(
        default=False,
    )

    is_lt_upgrade = models.BooleanField(
        default=False,
    )

    is_lt_downgrade = models.BooleanField(
        default=False,
    )

    is_lt_affirmation = models.BooleanField(
        default=False,
    )

    is_suspension = models.BooleanField(
        default=False,
    )

    is_withdrawal = models.BooleanField(
        default=False,
    )

    is_default = models.BooleanField(
        default=False,
    )

    is_selective_default = models.BooleanField(
        default=False,
    )

    is_matured = models.BooleanField(
        default=False,
    )

    # Set this to true if a decision has been made outside of regular
    # committee dates
    is_between_committees = models.BooleanField(
        default=False,
    )
