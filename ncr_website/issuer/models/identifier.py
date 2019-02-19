from django.db import models
from issuer.models import Issuer
from django.db.models.signals import post_save
from django.dispatch import receiver


class Identifier(models.Model):
    """Model for various identifiers."""

    def __str__(self):
        """Return a human readable representation of each record."""
        return 'Identifiers for {}'.format(
            self.issuer.legal_name)

    issuer = models.OneToOneField(
        Issuer,
        on_delete=models.PROTECT,
    )

    lei = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )

    corporate_registration_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )


@receiver(post_save, sender=Issuer)
def issuer_setup_identifier(sender, instance, created, **kwargs):
    """Makes sure there is an instance whenever someone
    saves the corporate model."""

    p, _ = Identifier.objects.get_or_create(issuer=instance,
                                            lei=instance.lei)
