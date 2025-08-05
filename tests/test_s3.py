import boto3
from django.test import TestCase
from django.conf import settings
from uuid import uuid4

class S3ReadWriteTest(TestCase):
    """Prueba básica de escritura y lectura en S3."""

    def test_s3_write_and_read(self):
        s3 = boto3.client(
            's3',
            region_name=settings.AWS_S3_REGION_NAME,
        )
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        key = f'test/{uuid4()}.txt'
        content = b'prueba-s3'

        s3.put_object(Bucket=bucket, Key=key, Body=content)

        obj = s3.get_object(Bucket=bucket, Key=key)
        data = obj['Body'].read()
        self.assertEqual(data, content)

        s3.delete_object(Bucket=bucket, Key=key) 