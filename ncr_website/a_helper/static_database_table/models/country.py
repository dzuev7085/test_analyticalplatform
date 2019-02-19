"""
This model contains a static list of all the world's countries including
in what region the country is located.
"""
from django.db import models


class CountryRegion(models.Model):
    """Lookup table to retrieve the sector of a GICS sub-industry code."""

    def __str__(self):
        """Return a human readable representation of each record."""
        return '%s (%s)' % (
            self.name,
            self.iso_31661_alpha_2
        )

    name = models.CharField(
        max_length=100,
        null=False,
        blank=False
    )

    iso_31661_alpha_2 = models.CharField(
        db_index=True,
        max_length=2,
        null=False,
        blank=False
    )

    iso_31661_alpha_3 = models.CharField(
        max_length=3,
        null=False,
        blank=False
    )

    iso_31661_alpha_3_country_code = models.IntegerField(
        null=False,
        blank=False
    )

    iso_3166_2 = models.CharField(
        max_length=13,
        null=False,
        blank=False
    )

    region = models.CharField(
        max_length=8,
        null=True,
        blank=True
    )

    sub_region = models.CharField(
        max_length=31,
        null=True,
        blank=True
    )

    intermediate_region = models.CharField(
        max_length=31,
        null=True,
        blank=True
    )

    region_code = models.IntegerField(
        null=True,
        blank=True
    )

    sub_region_code = models.IntegerField(
        null=True,
        blank=True
    )

    intermediate_region_code = models.IntegerField(
        null=True,
        blank=True
    )
