"""This model adds support for storing rating scales."""
from django.db import models
from ..const import RATING_SCOPE_EXPLANATION
from gui.templatetags.template_tags import format_reference_number


class RatingScale(models.Model):
    """RatingScale Model."""

    ordering = ['id']

    def __str__(self):
        """Represent the class."""
        return '{}'.format(self.description)

    @property
    def rating_scale_code(self):
        return format_reference_number(number=self.pk,
                                       object_type='rating_scale')

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

    time_horizon = models.IntegerField(
        choices=((1, 'L'),
                 (2, 'S')),
        null=False,
        blank=False
    )

    """
    C - corporate ratings
    S - Sovereign and public finance ratings
    T - Structured finance ratings
    O – Other financial instruments
    """
    rating_type = models.IntegerField(
        choices=((1, 'C'),
                 (2, 'S'),
                 (3, 'T'),
                 (4, 'O')),
        null=False,
        blank=False
    )

    """
    PR - rating scale is used for issuing preliminary ratings only
    FR - rating scale is used for issuing final ratings only
    BT - rating scale is used for issuing preliminary and final ratings
    """
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
