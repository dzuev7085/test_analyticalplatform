from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from credit_assessment.models.assessment import AssessmentJob
from rating_process.models.internal_score_data import (
    InternalScoreDataSubfactor,
    NOTCH_CHOICES
)
from pycreditrating import BASE_SCORE


class AssessmentSubscoreData(models.Model):
    """Describe the attributes of a risk subfactor score"""

    def __str__(self):
        return 'Data for {} | {} | {} | {} | Weight: {}'.format(
            self.assessment,
            self.subfactor,
            self.get_decided_score_display(),
            self.get_decided_notch_adjustment_display(),
            self.weight,
        )

    class Meta:
        """Meta class."""
        ordering = ['assessment__issuer',
                    'assessment',
                    'subfactor__factor',
                    'subfactor']

    assessment = models.ForeignKey(
        AssessmentJob,
        on_delete=models.PROTECT,
    )

    subfactor = models.ForeignKey(
        InternalScoreDataSubfactor,
        on_delete=models.PROTECT
    )

    weight = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        null=True,
        blank=True,
    )

    weight_edit_allowed = models.BooleanField(default=False)

    decided_score = models.IntegerField(
        choices=BASE_SCORE,
        validators=[MinValueValidator(1), MaxValueValidator(14)],
        null=True,
        blank=True,
        default=None,
    )

    decided_notch_adjustment = models.IntegerField(
        choices=NOTCH_CHOICES,
        validators=[MinValueValidator(-10), MaxValueValidator(10)],
        null=True,
        blank=True,
        default=None,
    )
