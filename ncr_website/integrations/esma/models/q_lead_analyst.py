"""Model to replicate ComplexLeadAnalystType.
<xs:element name="ReportingTypeInfo" type="dtypes:ComplexReportingTypeInfoType" minOccurs="1" maxOccurs="1"/> # noqa: E501
<xs:element name="LeadAnalystCode" type="dtypes:StringRestricted40Type" minOccurs="1" maxOccurs="1"/>
<xs:element name="LeadAnalystName" type="dtypes:StringRestricted90Type" minOccurs="1" maxOccurs="1"/>
<xs:element name="LeadAnalystStartDate" type="xs:date" minOccurs="1" maxOccurs="1"/>
<xs:element name="LeadAnalystEndDate" type="xs:date" minOccurs="1" maxOccurs="1"/>
"""

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


class LeadAnalyst(models.Model):
    """Model to represent the process that follows upon a rating decision
    that has been approved by the chair."""

    # Important for the script that sends data to ESMA.
    ordering = ['id']

    objects = ProcessManager()

    def __str__(self):
        return '{} | {}'.format(
            self.reporting_type_info,
            self.lead_analyst_code
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

    lead_analyst_code = models.CharField(
        max_length=40,
        blank=False,
        null=False
    )

    lead_analyst_name = models.CharField(
        max_length=90,
        blank=False,
        null=False
    )

    lead_analyst_start_date = models.DateField(
        blank=False,
        null=False
    )

    lead_analyst_end_date = models.DateField(
        blank=False,
        null=False
    )

    insertion_date = models.DateField(
        auto_now_add=True,
    )
