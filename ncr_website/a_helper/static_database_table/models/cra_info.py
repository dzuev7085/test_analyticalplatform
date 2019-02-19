"""Store static data about Nordic Credit Rating AS.
Data is sent to, among others, ESMA."""
from django.db import models


class CRAInfo(models.Model):
    """CRAInfo class."""

    def __str__(self):
        """Return a human readable representation of each record."""
        return '{}'.format(
            self.cra_name
        )

    cra_name = models.CharField(
        max_length=90,
        null=False,
        blank=False
    )

    cra_description = models.TextField(
        max_length=500,
        null=False,
        blank=False
    )

    cra_methodology = models.TextField(
        max_length=4000,
        null=False,
        blank=False
    )

    cra_methodology_webpage_link = models.TextField(
        max_length=300,
        null=False,
        blank=False
    )

    solicited_unsolicited_rating_policy_description = models.TextField(
        max_length=500,
        null=False,
        blank=False
    )

    subsidiary_rating_policy = models.TextField(
        max_length=500,
        null=False,
        blank=False
    )

    global_reporting_scope_flag = models.IntegerField(
        null=False,
        blank=False,
        choices=(
            (1, 'Y'),
            (2, 'N'))
    )

    definition_default = models.TextField(
        max_length=2000,
        null=False,
        blank=False
    )

    cra_website_link = models.TextField(
        max_length=40,
        null=False,
        blank=False
    )
