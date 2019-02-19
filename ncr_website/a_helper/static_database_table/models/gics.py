"""
These models are used to store meta data linked to an issuer. Such data
includes, but is not limited to, GICS codes and lookup tables for
country codes.

"""
from django.db import models


class GICSSector(models.Model):
    """Lookup table to retrieve the sector of a GICS sub-industry code."""

    class Meta:
        """Meta class."""
        ordering = ['code']

    def __str__(self):
        """Return a human readable representation of each record."""
        return '%s: %s' % (
            self.code,
            self.name
        )

    code = models.IntegerField(
        db_index=True,
        null=False,
        blank=False
    )

    name = models.CharField(
        max_length=100,
        null=False,
        blank=False
    )

    valid_from = models.DateField(
        null=False,
        blank=False
    )
    valid_to = models.DateField(
        null=True,
        blank=True
    )


class GICSIndustryGroup(models.Model):
    """Lookup table to retrieve the industry group of a GICS
    sub-industry code."""

    class Meta:
        """Meta class."""
        ordering = ['code']

    def __str__(self):
        """Return a human readable representation of each record."""
        return '%s: %s' % (
            self.code,
            self.name
        )

    sector = models.ForeignKey(
        GICSSector,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    code = models.IntegerField(
        null=False,
        blank=False
    )

    name = models.CharField(
        max_length=100,
        null=False,
        blank=False
    )

    valid_from = models.DateField(
        null=False,
        blank=False
    )
    valid_to = models.DateField(
        null=True,
        blank=True
    )


class GICSIndustry(models.Model):
    """Lookup table to retrieve the industry of a GICS sub-industry code."""

    class Meta:
        """Meta class."""
        ordering = ['code']

    def __str__(self):
        """Return a human readable representation of each record."""
        return '%s: %s' % (
            self.code,
            self.name
        )

    industry_group = models.ForeignKey(
        GICSIndustryGroup,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    code = models.IntegerField(
        null=False,
        blank=False
    )

    name = models.CharField(
        max_length=100,
        null=False,
        blank=False
    )

    valid_from = models.DateField(
        null=False,
        blank=False
    )

    valid_to = models.DateField(
        null=True,
        blank=True
    )


class GICSSubIndustry(models.Model):
    """Lookup table to retrieve the industry of a GICS sub-industry code.
    The ID here will be a foreign key in the issuer table."""

    class Meta:
        """Meta class."""
        ordering = ['code']

    def __str__(self):
        """Return a human readable representation of each record."""
        return '%s: %s' % (
            self.code,
            self.name
        )

    industry = models.ForeignKey(
        GICSIndustry,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    code = models.IntegerField(
        null=False,
        blank=False
    )

    name = models.CharField(
        max_length=100,
        null=False,
        blank=False
    )

    description = models.CharField(
        max_length=999,
        null=False,
        blank=False
    )

    valid_from = models.DateField(
        null=False,
        blank=False
    )
    valid_to = models.DateField(
        null=True,
        blank=True
    )
