from django.db import models
from pycreditrating import RATING_LONG_TERM_REVERSE_TUPLE

from issue.models import Seniority

from .rating_decision import RatingDecision

from simple_history.models import HistoricalRecords


class ProcessQuerySet(models.QuerySet):
    """Process filters for issue rating decision."""

    pass


class ProcessManager(models.Manager):
    """Process manager for issue rating decision."""

    def get_queryset(self):
        """Basic query set."""
        return ProcessQuerySet(self.model, using=self._db)  # Important!


class RatingDecisionIssue(models.Model):
    """Rating decisions for issues.

    TODO: rename to RatingDecisionIssueSenority."""

    # Add version history to the model
    history = HistoricalRecords()

    objects = ProcessManager()

    def __str__(self):
        return '%s\'s issues on seniority level ' \
               '\'%s\': proposed to \'%s\' and decided for \'%s\'' % (
                   self.rating_decision.issuer,
                   str(self.seniority).lower(),
                   self.get_proposed_lt_display(),
                   self.get_decided_lt_display())

    # Link back to the RatingDecision
    rating_decision = models.ForeignKey(
        RatingDecision,
        on_delete=models.PROTECT,
    )

    seniority = models.ForeignKey(
        Seniority,
        related_name='rating_decision_issue_seniority_link',
        null=False,
        blank=False,
        on_delete=models.PROTECT
    )

    # What long-term rating does the analyst propose?
    proposed_lt = models.IntegerField(
        choices=RATING_LONG_TERM_REVERSE_TUPLE,
        null=True,
        blank=True
    )

    # What long-term rating did the rating committee decide?
    decided_lt = models.IntegerField(
        choices=RATING_LONG_TERM_REVERSE_TUPLE,
        null=True,
        blank=True
    )
