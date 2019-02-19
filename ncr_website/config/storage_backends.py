from storages.backends.s3boto3 import S3Boto3Storage

from config.settings.base import (
    AWS_ANALYTICAL_MEDIA_LOCATION,
    AWS_COMMERCIAL_MEDIA_LOCATION,
    AWS_ESMA_FILE_LOCATION
)


class AnalyticalMediaStorage(S3Boto3Storage):
    location = AWS_ANALYTICAL_MEDIA_LOCATION
    default_acl = 'private'
    file_overwrite = False
#    custom_domain = False


class ESMAMediaStorage(S3Boto3Storage):
    location = AWS_ESMA_FILE_LOCATION
    default_acl = 'private'
    file_overwrite = False
#    custom_domain = False


class CommercialMediaStorage(S3Boto3Storage):
    """Store files related to the commercial side of the business.
    Currently not in use."""
    location = AWS_COMMERCIAL_MEDIA_LOCATION
#    default_acl = 'commercial'
    file_overwrite = False
#    custom_domain = False
