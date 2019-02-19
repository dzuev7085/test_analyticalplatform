"""Store information about a rating decision. After reading an article on
database performance, I went for this method instead of storing storing bits
in a integer field.

This a record of this model is created by the function
refresh_decision_attributes in the very last step of the rating process."""
from django.db import models

from .rating_decision import RatingDecision


class DecisionAttributes(models.Model):
    """Model to represent the process that follows upon a rating decision
    that has been approved by the chair."""

    class Meta:
        """Meta class."""
        ordering = ['rating_decision__issuer__issuer_name_override',
                    '-rating_decision__date_time_published', ]

    def __str__(self):
        return "{}".format(self.rating_decision)

    rating_decision = models.OneToOneField(
        RatingDecision,
        on_delete=models.PROTECT,
    )

    # The rating is preliminary at this stage
    # TODO: move the RatingDecision flag to here
    is_new_preliminary = models.BooleanField(
        default=False,
    )

    # This is the first time we assign a rating,
    # including assigning a preliminary rating
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

    is_st_upgrade = models.BooleanField(
        default=False,
    )

    is_st_downgrade = models.BooleanField(
        default=False,
    )

    is_st_affirmation = models.BooleanField(
        default=False,
    )

    is_outlook_change = models.BooleanField(
        default=False,
    )

    is_watch = models.BooleanField(
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
