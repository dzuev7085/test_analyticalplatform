from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from issuer.models import Issuer
from a_helper.static_database_table.models.country import CountryRegion
from pygleif import GLEIF


class Address(models.Model):
    """Store address to the company."""

    def __str__(self):
        """Return a human readable representation of each record."""
        return 'Address for {}'.format(
            self.issuer.legal_name)

    issuer = models.OneToOneField(
        Issuer,
        on_delete=models.PROTECT,
        null=False,
        blank=False
    )

    country = models.ForeignKey(
        CountryRegion,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )


@receiver(post_save, sender=Issuer)
def issuer_setup_address(sender, instance, created, **kwargs):
    """Makes sure there is an instance whenever someone
    saves the corporate model."""

    p, _ = Address.objects.get_or_create(issuer=instance)

    try:
        gleif_data = GLEIF(instance.lei)

        country_obj = CountryRegion.objects.get(
            iso_31661_alpha_2=gleif_data.entity.legal_address.country)

        p.country = country_obj
        p.save()

    except Exception:
        pass
