from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch

class CoreViewsTests(TestCase):
    """Suite de pruebas para las vistas de la aplicación core.
    
    Esta suite verifica la funcionalidad de las vistas de la aplicación core,
    incluyendo el endpoint hello world y el endpoint de verificación de salud de la base de datos.
    """

    def setUp(self):
        """Configura el cliente de prueba para cada test."""
        self.client = Client()

    def test_hello_world(self):
        """Verifica que el endpoint hello world devuelve un código de estado 200 y contiene el texto esperado."""
        response = self.client.get(reverse('core:hello_world'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Hola Mundo")

    def test_health_check(self):
        """Verifica que el endpoint de verificación de salud devuelve 200 y el mensaje correcto."""
        response = self.client.get(reverse('core:health'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok', 'message': 'Verificación de estado exitosa'})

    def test_db_health_check_success(self):
        """Verifica que el endpoint de verificación de salud de la base de datos devuelve 200 cuando la base de datos es accesible."""
        response = self.client.get(reverse('core:db_health_check'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok', 'message': 'Conexión a la base de datos exitosa'})

    def test_db_health_check_failure(self):
        """Verifica que el endpoint de verificación de salud de la base de datos devuelve 500 cuando la base de datos es inaccesible."""
        with patch('django.db.connection.cursor') as mock_cursor:
            mock_cursor.side_effect = Exception("Simulated DB failure")
            response = self.client.get(reverse('core:db_health_check'))
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json(), {'status': 'error', 'message': 'Error en la conexión a la base de datos'})

    def tearDown(self):
        """Limpia después de cada prueba."""
        pass