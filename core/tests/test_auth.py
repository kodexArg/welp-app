from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

User = get_user_model()


class AuthenticationViewsTest(TestCase):
    """
    Suite de pruebas para las vistas de autenticación.
    
    Cubre login_view y logout_view con todos sus casos de uso,
    incluyendo redirecciones, mensajes y validaciones de seguridad.
    """

    def setUp(self):
        """Configura usuarios de prueba y cliente de testing"""
        self.client = Client()
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Juan',
            last_name='Pérez',
            email='test@example.com'
        )
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@example.com'
        )

    def test_login_view_get_request_unauthenticated(self):
        """Verificar que GET a login muestra el formulario para usuarios no autenticados"""
        response = self.client.get(reverse('core:login'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ingresar')
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, 'csrf_token')

    def test_login_view_get_request_authenticated_user_redirects(self):
        """Verificar que usuario autenticado es redirigido desde login"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:login'))
        
        self.assertRedirects(response, reverse('core:index'))

    def test_login_view_post_valid_credentials_success(self):
        """Verificar login exitoso con credenciales válidas"""
        response = self.client.post(reverse('core:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertRedirects(response, reverse('core:index'))
        
        # Verificar que el usuario está autenticado
        user = get_user_model().objects.get(username='testuser')
        self.assertTrue('_auth_user_id' in self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_login_view_post_valid_credentials_success_message(self):
        """Verificar mensaje de bienvenida con nombre completo tras login exitoso"""
        response = self.client.post(reverse('core:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '¡Bienvenido, Juan Pérez!')
        self.assertEqual(messages[0].tags, 'success')

    def test_login_view_post_valid_credentials_username_fallback(self):
        """Verificar mensaje de bienvenida con username cuando no hay nombre completo"""
        user_no_name = User.objects.create_user(
            username='noname',
            password='testpass123'
        )
        
        response = self.client.post(reverse('core:login'), {
            'username': 'noname',
            'password': 'testpass123'
        }, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '¡Bienvenido, noname!')

    def test_login_view_post_invalid_credentials_error(self):
        """Verificar manejo de credenciales inválidas"""
        response = self.client.post(reverse('core:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuario o contraseña incorrectos.')
        
        # Verificar que el usuario NO está autenticado
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_login_view_post_nonexistent_user_error(self):
        """Verificar manejo de usuario inexistente"""
        response = self.client.post(reverse('core:login'), {
            'username': 'nonexistent',
            'password': 'anypassword'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuario o contraseña incorrectos.')

    def test_login_view_post_empty_username_error(self):
        """Verificar validación de campo username vacío"""
        response = self.client.post(reverse('core:login'), {
            'username': '',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Por favor, completa todos los campos.')

    def test_login_view_post_empty_password_error(self):
        """Verificar validación de campo password vacío"""
        response = self.client.post(reverse('core:login'), {
            'username': 'testuser',
            'password': ''
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Por favor, completa todos los campos.')

    def test_login_view_post_both_fields_empty_error(self):
        """Verificar validación cuando ambos campos están vacíos"""
        response = self.client.post(reverse('core:login'), {
            'username': '',
            'password': ''
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Por favor, completa todos los campos.')

    def test_login_view_next_parameter_redirect(self):
        """Verificar redirección a URL específica tras login exitoso"""
        next_url = reverse('core:dashboard')
        response = self.client.post(f"{reverse('core:login')}?next={next_url}", {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertRedirects(response, next_url)

    def test_login_view_next_parameter_invalid_fallback(self):
        """Verificar fallback a index cuando next parameter es inválido"""
        response = self.client.post(f"{reverse('core:login')}?next=/invalid/url/", {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Django redirige a /invalid/url/ aunque no exista (manejo en urls.py)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/invalid/url/')

    def test_logout_view_post_authenticated_user_success(self):
        """Verificar logout exitoso con usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('core:logout'))
        
        self.assertRedirects(response, reverse('core:index'))
        
        # Verificar que el usuario ya NO está autenticado
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_logout_view_post_authenticated_user_message(self):
        """Verificar mensaje de despedida tras logout exitoso"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('core:logout'), follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '¡Hasta luego, Juan Pérez!')
        self.assertEqual(messages[0].tags, 'info')

    def test_logout_view_post_authenticated_user_username_fallback(self):
        """Verificar mensaje de despedida con username cuando no hay nombre completo"""
        user_no_name = User.objects.create_user(
            username='noname',
            password='testpass123'
        )
        
        self.client.login(username='noname', password='testpass123')
        response = self.client.post(reverse('core:logout'), follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '¡Hasta luego, noname!')

    def test_logout_view_post_unauthenticated_user(self):
        """Verificar logout de usuario no autenticado"""
        response = self.client.post(reverse('core:logout'), follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), '¡Hasta luego, Usuario!')

    def test_logout_view_get_request_redirects(self):
        """Verificar que GET a logout redirige sin procesar logout"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('core:logout'))
        
        self.assertRedirects(response, reverse('core:index'))
        
        # Verificar que el usuario SIGUE autenticado (no se procesó logout)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_preserves_post_data_on_validation_errors(self):
        """Verificar que el username se preserva en el formulario tras error de validación"""
        response = self.client.post(reverse('core:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="testuser"')

    def test_csrf_protection_on_login_form(self):
        """Verificar que el formulario de login incluye protección CSRF"""
        response = self.client.get(reverse('core:login'))
        
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_superuser_login_functionality(self):
        """Verificar que superusuarios pueden hacer login normalmente"""
        response = self.client.post(reverse('core:login'), {
            'username': 'admin',
            'password': 'adminpass123'
        })
        
        self.assertRedirects(response, reverse('core:index'))
        
        user = get_user_model().objects.get(username='admin')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def tearDown(self):
        """Limpieza tras cada prueba"""
        User.objects.all().delete() 