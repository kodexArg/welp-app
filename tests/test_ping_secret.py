import os
import json
from django.test import TestCase

class PingSecretTest(TestCase):
    """Prueba de lectura del secret PING."""

    def test_ping_secret(self):
        ping_value = os.environ.get('PING')
        self.assertIsNotNone(ping_value, "Variable de entorno PING no encontrada")
        

        try:
            ping_json = json.loads(ping_value)
            if isinstance(ping_json, dict):
                # Buscar la clave en diferentes formatos (case-insensitive)
                ping_key = None
                for key in ping_json.keys():
                    if key.lower() == 'ping':
                        ping_key = key
                        break
                
                if ping_key:
                    self.assertEqual(ping_json[ping_key].strip().lower(), "pong")
                else:
                    self.fail(f"Clave 'ping' no encontrada en JSON: {ping_json}")
            else:
                self.fail(f"Formato JSON no es diccionario: {ping_json}")
        except json.JSONDecodeError:
            # Si no es JSON, verificar como string
            self.assertEqual(ping_value.strip().lower(), "pong") 