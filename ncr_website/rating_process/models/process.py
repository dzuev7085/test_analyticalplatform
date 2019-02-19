"""This module contains a model that models the rating job process. Currently,
only post-rating decision steps are modelled but the model could be extended.
"""
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .rating_decision import RatingDecision

from simple_history.models import HistoricalRecords


class Process(models.Model):
    """Model to represent the process that follows upon a rating decision
    that has been approved by the chair."""

    # Add version history to the model
    history = HistoricalRecords()

    def __str__(self):
        return 'Process for %s' % (self.rating_decision)

    # Link back to the RatingDecision
    rating_decision = models.ForeignKey(
        RatingDecision,
        on_delete=models.PROTECT,
    )

    # When did we start the process?
    process_started = models.DateTimeField(
        auto_now_add=True,
    )

    setup_done = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )

    pre_committee_done = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )

    analytical_phase_done = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )

    post_committee_done = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )

    editor_review_done = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )

    issuer_confirmation_done = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )

    final_sign_off_analyst_done = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )

    final_sign_off_chair_done = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )

    process_ended = models.DateTimeField(
        db_index=True,
        null=True,
        blank=True
    )


@receiver(post_save, sender=RatingDecision)
def create_process_object(sender, instance, created, **kwargs):
    """Create a process object whenever a rating decision
    object has been created."""

    if created:

        Process.objects.create(rating_decision=instance)
