from django.db import models
from pycreditrating import ASSESSMENT_LONG_TERM_REVERSE_TUPLE
from issue.models import Seniority
from credit_assessment.models.assessment import AssessmentJob


class SeniorityLevelAssessment(models.Model):
    """Assessments per seniority level."""

    class Meta:
        """Meta class."""
        ordering = ['assessment__issuer',
                    'assessment__date_time_creation',
                    'seniority']

    def __str__(self):
        return '{} | {} | {}'.format(
            self.assessment,
            self.seniority,
            self.get_decided_lt_display()
        )

    # Link back to the RatingDecision
    assessment = models.ForeignKey(
        AssessmentJob,
        on_delete=models.PROTECT,
    )

    seniority = models.ForeignKey(
        Seniority,
        null=False,
        blank=False,
        on_delete=models.PROTECT
    )

    decided_lt = models.IntegerField(
        choices=ASSESSMENT_LONG_TERM_REVERSE_TUPLE,
        null=True,
        blank=True
    )
