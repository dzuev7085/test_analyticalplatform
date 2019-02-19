from django.db import models
from issuer.models import Issuer
from django.db.models.signals import post_save
from django.dispatch import receiver


class Classification(models.Model):
    """Model for various identifiers."""

    def __str__(self):
        """Return a human readable representation of each record."""
        return 'Classifications for {}'.format(
            self.issuer.legal_name)

    @property
    def internal_peer(self):
        """NCR definition of peer group."""

        if self.peer_free_text:
            return self.peer_free_text
        else:
            return self.issuer.gics_sub_industry

    issuer = models.OneToOneField(
        Issuer,
        on_delete=models.PROTECT,
    )

    peer_free_text = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )


@receiver(post_save, sender=Issuer)
def issuer_setup_classification(sender, instance, created, **kwargs):
    """Makes sure there is an instance whenever someone
    saves the corporate model."""

    p, _ = Classification.objects.get_or_create(issuer=instance)
