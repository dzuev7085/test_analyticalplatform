"""Model to link assessment with issuer.

Query to reset pk counter
SELECT setval('credit_assessment_assessmentjob_id_seq',
(SELECT MAX(id) FROM credit_assessment_assessmentjob)+1);

SELECT setval('issuer_issuer_id_seq',
(SELECT MAX(id) FROM issuer_issuer)+1);
"""
from django.db import models
from issuer.models import Issuer
from django.contrib.auth.models import User
from datetime import timedelta
from tinymce.models import HTMLField
from pycreditrating import ASSESSMENT_LONG_TERM_REVERSE_TUPLE
from rating_process.const import PROCESS_STEPS
from django.utils import timezone


class ProcessQuerySet(models.QuerySet):
    """ProcessQuerySet class."""


class ProcessManager(models.Manager):
    """Process manager class."""

    def get_queryset(self):
        """Basic query set. Always filter out those that have been deleted."""
        return ProcessQuerySet(self.model, using=self._db)  # Important!


class AssessmentJob(models.Model):
    """Model for a credit assessment."""

    objects = ProcessManager()

    def __str__(self):
        if self.is_current:

            return '{} | current ({})'.format(
                self.issuer,
                self.pk
            )

        elif self.date_time_approval:

            return '{} ({})'.format(
                self.issuer,
                self.pk
            )

        else:

            return '{} | in progress ({})'.format(
                self.issuer,
                self.pk
            )

    class Meta:
        """Meta class."""
        ordering = ['issuer',
                    'date_time_creation']

    @property
    def assessment(self):
        """This property should be used in the GUI and elsewhere to clearly
        denote that this is merely an assessment."""

        return self.get_assessment_lt_display().lower()

    @property
    def is_lapsed(self):
        """Flag if the assessment's validity has lapsed (>90 days old)."""

        if self.date_time_approval:
            if self.date_time_approval + timedelta(days=90) > timezone.now():
                return False
            else:
                return True
        else:
            return False

    issuer = models.ForeignKey(
        Issuer,
        on_delete=models.PROTECT,
    )

    previous_assessment = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    """Returns what stage of the process we are in. Order is
    important in if clause. Later steps in process higher up
    in if-clause.
    """
    process_step = models.IntegerField(
        choices=PROCESS_STEPS,
        db_index=True,
        blank=False,
        null=False,
        default=1,
    )

    is_current = models.BooleanField(
        db_index=True,
        default=False,
    )

    initiated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="assessment_initiated_by",
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="assessment_approved_by",
        null=True,
        blank=True
    )

    date_time_deleted = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )

    date_time_creation = models.DateTimeField(
        db_index=True,
        auto_now_add=True,
    )

    date_time_approval = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )

    assessment_lt = models.IntegerField(
        choices=ASSESSMENT_LONG_TERM_REVERSE_TUPLE,
        null=True,
        blank=True
    )

    comment = HTMLField(
        null=True,
        blank=True,
    )
