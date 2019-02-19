"""Helper functions for the AWS S3 integration."""

import boto3
from botocore.config import Config

from config.settings.base import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, \
    AWS_STORAGE_BUCKET_NAME


def generate_presigned_url(file_path):
    """Create a pre-signed URL to download from AWS S3."""

    session = boto3.session.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name='eu-central-1')
    s3Client = session.client('s3', config=Config(signature_version='s3v4'))

    # Create a URL valid for 30 seconds.
    return s3Client.generate_presigned_url('get_object',
                                           Params={
                                               'Bucket':
                                                   AWS_STORAGE_BUCKET_NAME,
                                               'Key':
                                                   file_path},
                                           ExpiresIn=30)


def download_file(file_path, file_destination):
    """Download a file from AWS S3 into the current working folder."""

    session = boto3.session.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name='eu-central-1')
    s3Client = session.client('s3', config=Config(signature_version='s3v4'))

    return s3Client.download_file(AWS_STORAGE_BUCKET_NAME,
                                  file_path,
                                  file_destination)
