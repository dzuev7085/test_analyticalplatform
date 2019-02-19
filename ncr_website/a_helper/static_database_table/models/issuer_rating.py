"""This model adds support for storing the different types of ratings."""
from django.db import models


class IssuerRating(models.Model):
    """RatingScale Model."""

    ordering = ['id']

    def __str__(self):
        """Represent the class."""
        return '{}'.format(self.description)

    name = models.CharField(
        max_length=90,
        null=False,
        blank=False
    )

    description = models.TextField(
        max_length=500,
        null=False,
        blank=False
    )

    standard = models.IntegerField(
        choices=((1, 'IR'),  # IR – Main issuer rating
                 (2, 'DT'),  # DT - Debt rating
                 (3, 'OT')),  # OT - Other
        null=False,
        blank=False
    )

    start_date = models.DateField(
        null=False,
        blank=False
    )

    end_date = models.DateField(
        null=False,
        blank=False
    )
