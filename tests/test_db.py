from django.test import TestCase
from django.db import connection

class DatabaseConnectionTest(TestCase):
    """Prueba básica de conexión a la base de datos."""

    def test_database_connection(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
            self.assertEqual(result[0], 1) 