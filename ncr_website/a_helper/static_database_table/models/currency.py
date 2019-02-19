"""
This model contains a static list of all the world's currencies.
"""
from django.db import models


class Currency(models.Model):
    """Lookup table to retrieve the sector of a GICS sub-industry code."""

    def __str__(self):
        """Return a human readable representation of each record."""
        return '%s (%s)' % (
            self.name,
            self.currency_code_alpha_3
        )

    name = models.CharField(
        max_length=100,
        null=False,
        blank=False
    )

    currency_code_alpha_3 = models.CharField(
        max_length=3,
        null=False,
        blank=False
    )

    currency_code_alpha_3_currency_code = models.IntegerField(
        null=True,
        blank=True
    )
