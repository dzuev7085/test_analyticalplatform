from django.db import models
from credit_assessment.models.assessment import AssessmentJob


class HighestLowest(models.Model):
    """Assessments per seniority level."""

    class Meta:
        """Meta class."""
        ordering = ['assessment__issuer',
                    'assessment__date_time_creation',
                    'pk']

    def __str__(self):
        return '{}'.format(
            self.assessment,
        )

    assessment = models.OneToOneField(
        AssessmentJob,
        on_delete=models.PROTECT,
    )

    is_aaa = models.BooleanField(
        default=False,
    )

    is_aa_plus = models.BooleanField(
        default=False,
    )

    is_ccc = models.BooleanField(
        default=False,
    )

    is_cc = models.BooleanField(
        default=False,
    )

    is_c = models.BooleanField(
        default=False,
    )
