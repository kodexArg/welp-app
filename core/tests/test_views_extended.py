from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from unittest.mock import patch, MagicMock

User = get_user_model()


class HomeViewsTest(TestCase):
    """
    Suite de pruebas para vistas del módulo home.
    
    Cubre la vista index con información del sistema y diferentes
    configuraciones de entorno (local vs producción).
    """

    def setUp(self):
        """Configuración inicial para tests de home"""
        self.client = Client()
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_index_view_anonymous_user(self):
        """Verificar vista index para usuario no autenticado"""
        response = self.client.get(reverse('core:index'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bienvenido')
        self.assertContains(response, 'Iniciar Sesión')
        
        # Verificar información del sistema
        self.assertContains(response, 'Django')
        self.assertContains(response, 'Python')

    def test_index_view_authenticated_user(self):
        """Verificar vista index para usuario autenticado"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:index'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'WelpDesk')
        self.assertContains(response, 'Welp Payflow')

    def test_index_view_system_information(self):
        """Verificar información del sistema en vista index"""
        response = self.client.get(reverse('core:index'))
        
        # Verificar contexto incluye información técnica
        self.assertIn('django_version', response.context)
        self.assertIn('python_version', response.context)
        self.assertIn('environment', response.context)
        self.assertIn('storage_backend', response.context)
        self.assertIn('aws_region', response.context)

    def test_index_view_environment_detection(self):
        """Verificar detección correcta del entorno"""
        response = self.client.get(reverse('core:index'))
        
        # En tests, debería detectar como desarrollo
        self.assertContains(response, 'Desarrollo')

    def test_index_view_storage_backend_local(self):
        """Verificar detección de backend de almacenamiento local"""
        with self.settings(IS_LOCAL=True):
            response = self.client.get(reverse('core:index'))
            
            self.assertEqual(response.context['storage_backend'], 'Local')

    def test_index_view_storage_backend_s3(self):
        """Verificar detección de backend de almacenamiento S3"""
        with self.settings(IS_LOCAL=False):
            response = self.client.get(reverse('core:index'))
            
            self.assertEqual(response.context['storage_backend'], 'S3')

    def test_index_view_cdn_enabled_detection(self):
        """Verificar detección de CDN habilitado"""
        with self.settings(AWS_S3_CUSTOM_DOMAIN='cdn.example.com'):
            response = self.client.get(reverse('core:index'))
            
            self.assertTrue(response.context['cdn_enabled'])

    def test_index_view_htmx_detection(self):
        """Verificar detección de HTMX en request"""
        # Simular request con HTMX
        response = self.client.get(reverse('core:index'), HTTP_HX_REQUEST='true')
        
        # El contexto debe incluir información sobre HTMX
        self.assertIn('htmx_enabled', response.context)


class DashboardViewsTest(TestCase):
    """
    Suite de pruebas para vistas del dashboard de usuario.
    
    Cubre autenticación requerida y contenido personalizado
    del dashboard según el tipo de usuario.
    """

    def setUp(self):
        """Configuración inicial para tests de dashboard"""
        self.client = Client()
        self.regular_user = User.objects.create_user(
            username='regular',
            password='testpass123',
            first_name='Juan',
            last_name='Pérez'
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            password='testpass123',
            is_staff=True
        )

    def test_dashboard_view_requires_authentication(self):
        """Verificar que dashboard requiere autenticación"""
        response = self.client.get(reverse('core:dashboard'))
        
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_dashboard_view_authenticated_access(self):
        """Verificar acceso al dashboard con usuario autenticado"""
        self.client.login(username='regular', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mi Perfil')
        self.assertContains(response, 'regular')

    def test_dashboard_view_user_context(self):
        """Verificar contexto de usuario en dashboard"""
        self.client.login(username='regular', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        
        self.assertEqual(response.context['user'], self.regular_user)
        self.assertContains(response, 'Juan Pérez')

    def test_dashboard_view_staff_permissions(self):
        """Verificar permisos de staff en dashboard"""
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Staff')

    def test_dashboard_view_user_information_display(self):
        """Verificar información de usuario mostrada en dashboard"""
        self.client.login(username='regular', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        
        # Verificar campos específicos
        self.assertContains(response, 'regular')  # Username
        self.assertContains(response, 'Fecha de registro')
        self.assertContains(response, 'Último acceso')

    def test_dashboard_view_template_used(self):
        """Verificar template correcto usado en dashboard"""
        self.client.login(username='regular', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        
        self.assertTemplateUsed(response, 'core/dashboard.html')


class DevelopmentViewsTest(TestCase):
    """
    Suite de pruebas para vistas del módulo de desarrollo.
    
    Cubre todas las vistas de documentación técnica y herramientas
    de desarrollo disponibles en el sistema.
    """

    def setUp(self):
        """Configuración inicial para tests de desarrollo"""
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staff',
            password='testpass123',
            is_staff=True
        )

    def test_dev_main_view_access(self):
        """Verificar acceso a vista principal de desarrollo"""
        response = self.client.get(reverse('core:dev'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dev.html')

    def test_dev_udns_view_access(self):
        """Verificar acceso a vista de UDNs"""
        response = self.client.get(reverse('core:dev_udns'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dev/udns.html')
        self.assertContains(response, 'UDNs')

    def test_dev_sectors_view_access(self):
        """Verificar acceso a vista de sectores"""
        response = self.client.get(reverse('core:dev_sectors'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dev/sectors.html')
        self.assertContains(response, 'Sectores')

    def test_dev_categories_view_access(self):
        """Verificar acceso a vista de categorías"""
        response = self.client.get(reverse('core:dev_categories'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dev/categories.html')
        self.assertContains(response, 'Categorías')

    def test_dev_hierarchy_view_access(self):
        """Verificar acceso a vista de jerarquía"""
        response = self.client.get(reverse('core:dev_hierarchy'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dev/hierarchy.html')

    def test_dev_purchase_workflow_view_access(self):
        """Verificar acceso a vista de workflow de compras"""
        response = self.client.get(reverse('core:dev_purchase_workflow'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dev/purchase-workflow.html')

    def test_dev_views_contain_expected_content(self):
        """Verificar que vistas de desarrollo contienen contenido específico"""
        # Test UDNs
        response = self.client.get(reverse('core:dev_udns'))
        self.assertContains(response, 'Km 1151')
        self.assertContains(response, 'Las Bóvedas')

        # Test Sectores
        response = self.client.get(reverse('core:dev_sectors'))
        self.assertContains(response, 'Full')
        self.assertContains(response, 'Playa')
        self.assertContains(response, 'Administración')

        # Test Categorías
        response = self.client.get(reverse('core:dev_categories'))
        self.assertContains(response, 'DEBO')
        self.assertContains(response, 'YPF')
        self.assertContains(response, 'Soporte IT')

    def test_dev_views_accessibility(self):
        """Verificar accesibilidad básica de vistas de desarrollo"""
        dev_urls = [
            'core:dev',
            'core:dev_udns',
            'core:dev_sectors',
            'core:dev_categories',
            'core:dev_hierarchy',
            'core:dev_purchase_workflow'
        ]
        
        for url_name in dev_urls:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 200)
            # Verificar que no hay errores críticos de template
            self.assertNotContains(response, 'TemplateDoesNotExist')


class ViewsIntegrationTest(TestCase):
    """
    Suite de pruebas de integración para flujos completos entre vistas.
    
    Verifica navegación entre diferentes secciones del sistema
    y coherencia en el contexto compartido.
    """

    def setUp(self):
        """Configuración para tests de integración"""
        self.client = Client()
        self.test_user = User.objects.create_user(
            username='integration_user',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_navigation_flow_unauthenticated(self):
        """Verificar flujo de navegación para usuario no autenticado"""
        # Inicio -> Login
        response = self.client.get(reverse('core:index'))
        self.assertContains(response, 'Iniciar Sesión')
        
        # Login -> Dashboard (tras autenticación)
        response = self.client.post(reverse('core:login'), {
            'username': 'integration_user',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('core:index'))

    def test_navigation_flow_authenticated(self):
        """Verificar flujo de navegación para usuario autenticado"""
        self.client.login(username='integration_user', password='testpass123')
        
        # Index -> Dashboard
        response = self.client.get(reverse('core:index'))
        self.assertContains(response, 'integration_user')
        
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')

    def test_breadcrumb_consistency(self):
        """Verificar consistencia en navegación y breadcrumbs"""
        # Todas las vistas deben tener estructura básica
        urls_to_test = [
            'core:index',
            'core:dev',
            'core:dev_udns',
        ]
        
        for url_name in urls_to_test:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 200)
            # Verificar elementos básicos de navegación
            self.assertContains(response, 'Welp')  # Brand

    def test_system_information_consistency(self):
        """Verificar consistencia de información del sistema entre vistas"""
        response = self.client.get(reverse('core:index'))
        
        # La información del sistema debe estar disponible
        context = response.context
        self.assertIsNotNone(context.get('django_version'))
        self.assertIsNotNone(context.get('python_version'))
        self.assertIsNotNone(context.get('environment'))

    def tearDown(self):
        """Limpieza tras cada test de integración"""
        User.objects.all().delete() 