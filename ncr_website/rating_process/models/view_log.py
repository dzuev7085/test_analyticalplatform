"""This module contains a model that models the rating job process. Currently,
only post-rating decision steps are modelled but the model could be extended.
"""
from django.db import models
from django.contrib.auth.models import User

from .rating_decision import RatingDecision


class ViewLog(models.Model):
    """Model to represent the process that follows upon a rating decision
    that has been approved by the chair."""

    def __str__(self):
        return 'Committee pack for %s was downloaded by %s on %s' % (
            self.rating_decision.issuer,
            self.downloaded_by,
            self.date_time_downloaded.strftime('%Y-%m-%d %H:%M'))

    # Link back to the RatingDecision
    rating_decision = models.ForeignKey(
        RatingDecision,
        on_delete=models.PROTECT,
    )

    downloaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=False,
        blank=False
    )

    # When did we start the process?
    date_time_downloaded = models.DateTimeField(
        auto_now_add=True,
    )
