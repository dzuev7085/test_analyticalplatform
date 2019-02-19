from django.contrib.auth.models import User
from django.db import models
from issuer.models import Issuer
from rating_process.models.rating_decision import RatingDecision
from . import InsiderList


class InsiderLog(models.Model):
    """Log insiders.."""

    def __str__(self):
        """Return a human readable representation of each record."""
        return 'Insider person for {}'.format(
            self.issuer.legal_name)

    issuer = models.ForeignKey(
        Issuer,
        on_delete=models.PROTECT,
        null=False,
        blank=False
    )

    rating_decision = models.ForeignKey(
        RatingDecision,
        on_delete=models.PROTECT,
        null=False,
        blank=False
    )

    ncr_employee = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    insider = models.ForeignKey(
        InsiderList,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    date_creation = models.DateTimeField(
        auto_now_add=True,
    )

    date_added = models.DateTimeField(
        db_index=True,
        null=False,
        blank=False
    )

    date_removed = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )

    addition_reason = models.CharField(
        db_index=True,
        max_length=255,
        blank=False,
        null=False,
    )

    removal_reason = models.CharField(
        db_index=True,
        max_length=255,
        blank=False,
        null=False,
    )
