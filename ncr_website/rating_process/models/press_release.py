"""Store press release data for a rating decision."""

from django.db import models
from tinymce import HTMLField

from .rating_decision import RatingDecision

from django.db.models.signals import post_save
from django.dispatch import receiver


class PressRelease(models.Model):
    """PressReleaseModelClass."""

    def __str__(self):
        return '{} | {}'.format(
            self.rating_decision,
            self.header
        )

    # Link back to the RatingDecision
    rating_decision = models.ForeignKey(
        RatingDecision,
        on_delete=models.PROTECT
    )

    @property
    def is_valid(self):
        """Set a property when all fields have been filled in."""
        if self.header and self.pre_amble and self.body:
            return True

    header = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="A short but informative head line."
    )

    pre_amble = HTMLField(
        blank=True,
        null=True,
        help_text="An introduction to the body. This is often the only part "
                  "included by media so keep the text crispy."
    )

    body = HTMLField(
        blank=True,
        null=True,
        help_text="The rest of the press release."
    )


@receiver(post_save, sender=RatingDecision)
def create_press_release(sender, instance, created, **kwargs):
    """Create a press release record for public ratings."""

    if created:
        if instance.rating_type.id == 1:
            PressRelease.objects.create(
                rating_decision=instance
            )
