"""Model to serve as a base for XML files sent to ESMA."""
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Max
from tinymce import HTMLField

from config.storage_backends import ESMAMediaStorage


def get_upload_to(self, filename):
    """Store each file in a subfolder of qualitative or quantative files."""

    return ('{}/{}/{}/{}/{}'.format(
        self.get_file_type_display(),
        self.file_created.year,
        self.file_created.month,
        self.file_created.day,
        filename))


class XMLFile(models.Model):
    """Identifier for the XML-file sent to ESMA."""

    ordering = ['id']

    def __str__(self):
        """Give a representation in the GUI."""

        # Return some extra information to help debug reporting gto ESMA
        extra_list = []
        try:
            extra_list.append(self.qtratingcreatedata.qtratingaction.
                              get_action_type_display())
        except Exception:
            pass

        try:
            extra_list.append(self.qtratingcreatedata.qtratingaction.
                              qtratinginfo.get_industry_display())
        except Exception:
            pass

        try:
            extra_list.append(self.qtratingcreatedata.qtratingaction.
                              qtratinginfo.get_rated_object_display())
        except Exception:
            pass

        try:
            extra_list.append(self.qtratingcreatedata.qtratingaction.
                              qtratinginfo.get_time_horizon_display())
        except Exception:
            pass

        try:
            extra_list.append(self.qtratingcreatedata.qtratingaction.
                              qtratinginfo.qtinstrumentinfo.isin_code)
        except Exception:
            pass

        extra = ", ".join(extra_list)

        return '{} | {}_{}_{} | {} | {}'.format(
            self.file_created.strftime('%Y-%m-%d %H:%M:%S'),
            self.get_file_type_display(),
            self.sequence_number,
            self.file_created.year,
            self.get_status_code_display(),
            extra
        )

    file_created = models.DateTimeField(
        auto_now_add=True,
    )

    status_code = models.IntegerField(
        blank=True,
        null=True,
        choices=((0, 'fail'), (1, 'success')),
    )

    """
    File Type this is a 6-character field. It identifies the type
    of information contained in the file depending on the type of
    file. For the files sent by the CRAs to RADAR:
    - DATQXX signifies qualitative data files
    - DATRXX signifies quantitative data files"""
    file_type = models.IntegerField(
        blank=False,
        null=False,
        choices=((1, 'DATQXX'), (2, 'DATRXX')),
    )

    """
    Sequence Number is a unique sequence number on 6 digits field.
    This number is incremented each time an entity sends a file.
    This sequence number does not depend on the file type, recipient
    or any other characteristic. It can start again at 000000 after 999999.
    If the same file is sent again, a new sequence number is provided. This
    number identifies uniquely a single file. Should a problem occur in the
    sending of a file, the sequence number will help identifying a unique file.
    """
    sequence_number = models.IntegerField(
        blank=True,
        null=True,
        editable=False
    )

    # Document is stored in AWS S3
    # The stored document is in .zip-format
    document_location = models.FileField(
        storage=ESMAMediaStorage(),
        upload_to=get_upload_to,
        blank=True,
        null=True
    )

    response_file = models.FileField(
        storage=ESMAMediaStorage(),
        upload_to=get_upload_to,
        blank=True,
        null=True
    )

    comment = HTMLField(
        null=True,
        blank=True,
    )


@receiver(post_save, sender=XMLFile)
def create_xml_file(sender, instance, created, **kwargs):
    """Signal function."""

    if created:

        """Set a valid sequence number for the file.
        See requirement in model for more information."""
        try:
            # Index = 0 is the file reference we just created
            # Use the second last one
            current_value = XMLFile.objects.all().aggregate(
                Max('sequence_number'))['sequence_number__max']

        except IndexError:
            # No records have been created yet
            current_value = 0

        try:
            if current_value >= 999999:
                instance.sequence_number = 0
            else:
                instance.sequence_number = current_value+1
        except TypeError:
            instance.sequence_number = 0

        instance.save()
