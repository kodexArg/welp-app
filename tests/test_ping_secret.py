import os
from django.test import TestCase

class PingSecretTest(TestCase):
    """Prueba de lectura del secret PING."""

    def test_ping_secret(self):
        ping_value = os.environ.get('PING')
        self.assertIsNotNone(ping_value, "Variable de entorno PING no encontrada")
        self.assertEqual(ping_value.strip().lower(), "pong") 