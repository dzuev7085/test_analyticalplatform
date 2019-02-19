"""This model links the Issue model with the IssueSeniority model."""
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from pycreditrating import RATING_LONG_TERM_REVERSE_TUPLE
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from .rating_decision_issue import RatingDecisionIssue
from issue.models import Issue
from simple_history.models import HistoricalRecords
from django.utils import timezone
from datetime import timedelta
from integrations.esma.const import LOOKBACK
from rating_process.const import PROCESS_STEPS


class ProcessQuerySet(models.QuerySet):
    """Process filters."""

    # Current ratings
    def valid_decisions(self):
        """Return all published ratings."""

        return self.filter(date_time_published__isnull=False,
                           date_time_deleted__isnull=True).order_by(
                               '-date_time_approval')

    def esma(self):
        """Return rating decisions that are to be reported to ESMA."""

        # At the moment, only send public ratings
        return self.valid_decisions().filter(
            rating_decision_issue__rating_decision__rating_type__id__in=[1],
            date_time_published__gte=timezone.now() - timedelta(
                days=LOOKBACK)).order_by('date_time_published')


class ProcessManager(models.Manager):
    """ProcessManager class."""

    def get_queryset(self):
        """Basic query set. Always filter out those that have been deleted."""
        return ProcessQuerySet(self.model, using=self._db)  # Important!

    def valid_decisions(self):
        """Show the last and currently valid rating decision."""
        return self.get_queryset().valid_decisions()

    def esma(self):
        """Return rating decisions that are to be reported to ESMA."""

        return self.get_queryset().esma()


class IssueDecision(models.Model):
    """Rating decisions for specific issues."""

    # Add version history to the model
    history = HistoricalRecords()
    objects = ProcessManager()

    def __str__(self):
        try:
            representation = '{} | {} | {} | published on: '.format(
                self.pk,
                self.rating_decision_issue,
                self.issue,
                self.date_time_published.strftime('%Y-%m-%d %H:%M')
            )
        except Exception:
            representation = 'na'

        return representation

    # Link back to the RatingDecision
    rating_decision_issue = models.ForeignKey(
        RatingDecisionIssue,
        on_delete=models.PROTECT,
    )

    # Link back to the RatingDecision
    issue = models.ForeignKey(
        Issue,
        on_delete=models.PROTECT,
    )

    # Links bank to the previous rating (if any)
    previous_rating = models.ForeignKey(
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

    # Is this a preliminary rating?
    is_preliminary = models.BooleanField(
        default=False
    )

    is_current = models.BooleanField(
        db_index=True,
        default=True,
    )

    # proposed by
    proposed_by = models.ForeignKey(
        User,
        related_name='issue_decision_proposed_by',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    # approved by
    chair = models.ForeignKey(
        User,
        related_name='issue_decision_approved_by',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    # On what date and time was the committee held
    date_time_committee = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )

    # On what date and time was the rating published
    date_time_published = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )

    # On what date and time was the preliminary rating
    # communicated to the issuer
    # Required by ESMA
    date_time_communicated_issuer = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )

    date_time_deleted = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )

    # When was the rating decision initiated?
    date_time_creation = models.DateTimeField(
        db_index=True,
        auto_now_add=True,
    )

    decided_lt = models.IntegerField(
        choices=RATING_LONG_TERM_REVERSE_TUPLE,
        null=True,
        blank=True
    )

    rationale = HTMLField(
        null=True,
        blank=True,
    )


@receiver(post_save, sender=IssueDecision)
def issue_decision_setup(sender, instance, created, **kwargs):
    """Adds a reference to the last valid decision upon creation."""

    if created:
        try:

            # When we store an object, it's set to is_current
            previous_decision_obj = IssueDecision.objects.exclude(
                pk=instance.id).get(
                issue=instance.issue,
                is_current=True,
            )

            # Todo: this will not work if a user creates an issue inbetween
            # of regular rating decisions
            previous_decision_obj.is_current = False
            previous_decision_obj.save()

            instance.previous_rating = previous_decision_obj

        except IssueDecision.DoesNotExist:

            pass

        instance.save()
