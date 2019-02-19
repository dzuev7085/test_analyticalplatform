"""Model to replicate dtypes:ComplexReportingTypeInfoType.
<xs:element name="ReportingType" type="dtypes:RestrictiveReportingTypeType"/> # noqa: E501
<xs:element name="ChangeReason" type="dtypes:ChangeReasonType" minOccurs="0" maxOccurs="1"/>
<xs:element name="ReportingReason" type="dtypes:StringRestricted300Type" minOccurs="0" maxOccurs="1"/>
<xs:element name="UpdateDate" type="xs:date" minOccurs="0" maxOccurs="1"/>"""

from django.db import models


class ReportingTypeInfo(models.Model):
    """ReportingTypeInfo class."""

    def __str__(self):
        return '{} {} {} {}'.format(
            self.get_reporting_type_display(),
            self.get_change_reason_display(),
            self.reporting_reason,
            self.update_date
        )

    reporting_type = models.IntegerField(
        blank=False,
        null=False,
        choices=((1, 'NEW'), (2, 'CHG')),
    )

    change_reason = models.IntegerField(
        blank=True,
        null=True,
        choices=((1, 'C'), (2, 'U')),
    )

    reporting_reason = models.TextField(
        max_length='300',
        blank=True,
        null=True,
    )

    hash = models.CharField(
        db_index=True,
        max_length=32,
        blank=True,
        null=True,
    )

    update_date = models.DateTimeField(
        auto_now_add=True,
    )
