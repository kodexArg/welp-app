import os
import json
from django.test import TestCase

class PingSecretTest(TestCase):
    """Prueba de lectura del secret PING."""

    def test_ping_secret(self):
        ping_value = os.environ.get('PING')
        self.assertIsNotNone(ping_value, "Variable de entorno PING no encontrada")
        
        # Verificar si es JSON
        try:
            ping_json = json.loads(ping_value)
            if isinstance(ping_json, dict) and 'ping' in ping_json:
                self.assertEqual(ping_json['ping'].strip().lower(), "pong")
            else:
                self.fail(f"Formato JSON inválido: {ping_json}")
        except json.JSONDecodeError:
            # Si no es JSON, verificar como string
            self.assertEqual(ping_value.strip().lower(), "pong") 