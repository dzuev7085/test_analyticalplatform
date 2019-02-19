# Python
import os

from django.contrib.auth.models import User
# Django
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# Config
from config.storage_backends import AnalyticalMediaStorage
# Issuer
from issuer.models import Issuer
# Rating decision
from rating_process.models.rating_decision import RatingDecision


def get_upload_to(instance, filename):
    """Store each file in a subfolder of the lei-code of the issuer."""

    if instance.rating_decision:
        return 'issuers/%s/rating_decision/%s/%s'\
               % (
                   instance.issuer.lei,
                   instance.rating_decision.id,
                   filename)
    else:
        return 'issuers/%s/%s' % (instance.issuer.lei, filename)


class SecurityClass(models.Model):

    def __str__(self):
        return '%s' % self.name

    name = models.CharField(
        max_length=100,
        blank=False,
        null=False
    )


class DocumentType(models.Model):

    def __str__(self):
        return '%s' % self.name

    name = models.CharField(
        max_length=100,
        blank=False,
        null=False
    )


class AnalyticalDocument(models.Model):

    ordering = ['issuer', 'uploaded_at']

    def __str__(self):
        if self.rating_decision:
            return '%s | rating decision | %s | %s' % (
                self.issuer,
                self.document_type,
                self.filename
            )
        else:
            try:
                return '%s uploaded on: %s | %s' % (
                    self.issuer,
                    self.uploaded_at.strftime('%Y-%m-%d'),
                    self.filename
                )
            except:  # noqa: E722
                return '%s' % (
                    self.filename
                )

    @property
    def filename(self):
        return os.path.basename(self.upload.name)

    issuer = models.ForeignKey(Issuer,
                               on_delete=models.PROTECT,
                               related_name='upload_analytical_document')

    rating_decision = models.ForeignKey(RatingDecision,
                                        on_delete=models.PROTECT,
                                        blank=True,
                                        null=True)

    uploaded_by = models.ForeignKey(User,
                                    on_delete=models.PROTECT,
                                    related_name='upload_analytical_'
                                                 'document_user')

    # Date for meeting or for eg quarterly report
    date_value = models.DateTimeField(
        blank=True,
        null=True
    )

    uploaded_at = models.DateTimeField(
        db_index=True,
        auto_now_add=True
    )

    upload = models.FileField(
        storage=AnalyticalMediaStorage(),
        upload_to=get_upload_to
    )

    security_class = models.ForeignKey(
        SecurityClass,
        on_delete=models.PROTECT,
        default=4,
        related_name='upload_analytical_document_security_class'
    )

    document_type = models.ForeignKey(DocumentType,
                                      on_delete=models.PROTECT,
                                      related_name='upload_analytical_'
                                                   'document_document_type')


@receiver(pre_delete, sender=AnalyticalDocument)
def remove_file_from_s3(sender, instance,  **kwargs):
    instance.upload.delete(save=False)
