"""This model adds support for storing seniority levels."""
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


class IssuerRating(models.Model):
    """DebtClassification Model."""

    # Important for the script that sends data to ESMA.
    ordering = ['id']

    objects = ProcessManager()

    def __str__(self):
        return '{} | {}'.format(
            self.reporting_type_info,
            self.rating_type_code
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

    rating_type_code = models.CharField(
        max_length=10,
        blank=False,
        null=False,
    )

    rating_type_name = models.CharField(
        max_length=90,
        null=False,
        blank=False
    )

    rating_type_description = models.TextField(
        max_length=500,
        null=False,
        blank=False
    )

    rating_type_standard = models.IntegerField(
        choices=((1, 'IR'),  # IR – Main issuer rating
                 (2, 'DT'),  # DT - Debt rating
                 (3, 'OT')),  # OT - Other
        null=False,
        blank=False
    )

    rating_type_start_date = models.DateField(
        null=False,
        blank=False
    )

    rating_type_end_date = models.DateField(
        null=False,
        blank=False
    )
