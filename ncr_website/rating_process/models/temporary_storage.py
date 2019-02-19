from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver

from .rating_decision import RatingDecision


class Tmp(models.Model):

    def __str__(self):
        return "Tmp for %s" % self.rating_decision

    # Link back to the RatingDecision
    rating_decision = models.ForeignKey(
        RatingDecision,
        on_delete=models.PROTECT
    )

    editor_admin_control_link = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    issuer_admin_control_link = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )


@receiver(post_save, sender=RatingDecision)
def create_tmp_object(sender, instance, created, **kwargs):
    """Create a process object whenever a rating decision
    object has been created."""

    if created:
        Tmp.objects.create(rating_decision=instance)
