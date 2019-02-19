# Django
# Python
import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# Config
from config.storage_backends import AnalyticalMediaStorage


def get_upload_to(instance, filename):
    """Store each file in a based on category."""

    return 'documents/methodology/%s/%s.pdf' % (
        str(instance.category).lower(),
        instance.date_decision.strftime('%Y%m%d')
    )


class MethodologyCategory(models.Model):

    def __str__(self):
        return '%s' % (
            self.name,
        )

    name = models.CharField(
        max_length=100,
        null=False,
        blank=False
    )


class Methodology(models.Model):

    def __str__(self):
        if not self.date_deleted:

            # The try/except is for when saving the model and the uploaded_by
            # hasn't been set yet.
            try:
                return '%s uploaded by %s on %s' % (
                    self.category,
                    self.uploaded_by.get_full_name(),
                    self.date_decision.strftime('%Y-%m-%d')
                )
            except:  # noqa E722
                return '1'
        else:
            return 'Deleted on %s' % self.date_deleted.strftime("%Y-%m-%d")

    class Meta:
        ordering = ('category', '-date_decision',)

    @property
    def filename(self):
        return os.path.basename(self.upload.name)

    created_at = models.DateTimeField(auto_now_add=True)

    category = models.ForeignKey(
        MethodologyCategory,
        on_delete=models.PROTECT,
        related_name="methodology_methodology_category",
        null=False,
        blank=False
    )

    date_decision = models.DateTimeField(
        blank=False,
        null=False
    )

    date_deleted = models.DateTimeField(
        blank=True,
        null=True
    )

    uploaded_by = models.ForeignKey(User,
                                    related_name='methodology_'
                                                 'methodology_user',
                                    on_delete=models.PROTECT,
                                    blank=True,
                                    null=True)

    upload = models.FileField(
        storage=AnalyticalMediaStorage(),
        upload_to=get_upload_to
    )


@receiver(pre_delete, sender=Methodology)
def remove_file_from_s3(sender, instance, **kwargs):
    """Delete physical file from AWS S3 upon delete."""

    instance.upload.delete(save=False)
