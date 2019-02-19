"""This model adds support for storing rating scales."""
from django.db import models

from .xml_file import XMLFile
from .reporting_type_info import ReportingTypeInfo
from a_helper.static_database_table.const import RATING_SCOPE_EXPLANATION


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


class RatingScale(models.Model):
    """RatingScale Model."""

    # Important for the script that sends data to ESMA.
    ordering = ['id']

    objects = ProcessManager()

    def __str__(self):
        """Represent the class."""
        return '{}'.format(self.description)

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

    rating_scale_code = models.CharField(
        max_length=10,
        blank=False,
        null=False,
    )

    start_date = models.DateField(
        null=False,
        blank=False
    )

    end_date = models.DateField(
        null=False,
        blank=False
    )

    description = models.TextField(
        max_length=500,
        null=True,
        blank=True
    )


class RatingScope(models.Model):
    """RatingScope Model."""

    ordering = ['id']

    def __str__(self):
        """Represent the class."""
        return '{} | {}'.format(self.rating_scale,
                                RATING_SCOPE_EXPLANATION[self.time_horizon])

    rating_scale = models.ForeignKey(
        RatingScale,
        on_delete=models.PROTECT
    )

    rating_scope_code = models.CharField(
        max_length=10,
        blank=False,
        null=False,
    )

    time_horizon = models.IntegerField(
        choices=((1, 'L'),
                 (2, 'S')),
        null=False,
        blank=False
    )

    rating_type = models.IntegerField(
        choices=((1, 'C'),
                 (2, 'S'),
                 (3, 'T'),
                 (4, 'O')),
        null=False,
        blank=False
    )

    rating_scale_scope = models.IntegerField(
        choices=((1, 'PR'),
                 (2, 'FR'),
                 (3, 'BT')),
        null=False,
        blank=False
    )

    relevant_for_cerep_flag = models.BooleanField(
        default=True,
        blank=False,
        null=False
    )

    start_date = models.DateField(
        null=False,
        blank=False
    )

    end_date = models.DateField(
        null=False,
        blank=False
    )


class RatingCategory(models.Model):
    """RatingCategory Model."""

    def __str__(self):
        """Represent the class."""
        return '{} | {}'.format(self.rating_scale,
                                self.label)

    rating_scale = models.ForeignKey(
        RatingScale,
        on_delete=models.PROTECT
    )

    rating_category_code = models.CharField(
        max_length=10,
        blank=False,
        null=False,
    )

    value = models.IntegerField(
        null=False,
        blank=False
    )

    label = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )

    description = models.TextField(
        max_length=500,
        null=True,
        blank=True
    )


class RatingNotch(models.Model):
    """RatingNotch Model."""

    def __str__(self):
        """Represent the class."""
        return '{} | {} ({})'.format(self.rating_category,
                                     self.label,
                                     self.value)

    rating_category = models.ForeignKey(
        RatingCategory,
        on_delete=models.PROTECT
    )

    rating_notch_code = models.CharField(
        max_length=10,
        blank=False,
        null=False,
    )

    value = models.IntegerField(
        null=False,
        blank=False
    )

    label = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )

    description = models.TextField(
        max_length=500,
        null=True,
        blank=True
    )
