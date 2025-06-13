from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):
    """Suite de pruebas para los modelos de la aplicación core.
    
    Esta suite verifica la funcionalidad de los modelos de la aplicación core,
    incluyendo el modelo de usuario y cualquier modelo personalizado.
    """

    def setUp(self):
        """Configura el entorno de prueba para cada test."""
        super().setUp()

    def test_create_user(self):
        """Verifica que se puede crear un usuario."""
        User = get_user_model()
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Verifica que se puede crear un superusuario."""
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertEqual(admin_user.username, 'admin')
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_user_str_representation(self):
        """Verifica la representación en cadena de texto de un usuario."""
        User = get_user_model()
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(str(user), 'testuser')

    def tearDown(self):
        """Limpia después de cada prueba."""
        super().tearDown() 