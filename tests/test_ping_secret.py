import boto3
from django.test import TestCase
from django.conf import settings

class PingSecretTest(TestCase):
    """Prueba de lectura del secret PING."""

    def test_ping_secret(self):
        client = boto3.client('secretsmanager', region_name=settings.AWS_S3_REGION_NAME)
        secret_name = "pingping/secret-VcQsw5"
        response = client.get_secret_value(SecretId=secret_name)
        value = response['SecretString']
        self.assertEqual(value.strip().lower(), "pong") 