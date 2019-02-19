"""This model adds support for storing basic CRA info."""
from django.db import models

from .xml_file import XMLFile
from .reporting_type_info import ReportingTypeInfo


class ProcessQuerySet(models.QuerySet):
    """Process filters."""

    def last_valid_record(self):
        """Get last successful record sent to ESMA."""
        return self.filter(xml_file__status_code=1).order_by('-id')


class ProcessManager(models.Manager):
    """Process manager class."""

    def get_queryset(self):
        """Basic query set. Always filter out those that have been deleted."""
        return ProcessQuerySet(self.model, using=self._db)  # Important!

    def last_valid_record(self):
        """Get all records that should be sent to ESMA"""
        return self.get_queryset().last_valid_record()


class CRAInfo(models.Model):
    """CRAInfo Model."""

    # Important for the script that sends data to ESMA.
    ordering = ['id']

    objects = ProcessManager()

    def __str__(self):
        return '{} | {}'.format(
            self.reporting_type_info,
            self.cra_info_code
        )

    xml_file = models.ForeignKey(
        XMLFile,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    reporting_type_info = models.ForeignKey(
        ReportingTypeInfo,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    insertion_date = models.DateField(
        auto_now_add=True,
    )

    cra_info_code = models.CharField(
        max_length=10,
        blank=False,
        null=False,
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
