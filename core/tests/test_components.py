from django.test import TestCase
from django.template import Template, Context
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class ComponentRenderingTest(TestCase):
    """
    Suite de pruebas para renderizado específico de componentes HTML.
    
    Verifica que cada componente renderice correctamente con la estructura
    HTML esperada, clases CSS apropiadas y contenido dinámico.
    """

    def setUp(self):
        """Configuración inicial para tests de componentes"""
        self.test_user = User.objects.create_user(
            username='testuser',
            first_name='Ana',
            last_name='López'
        )

    def test_brand_logo_renders_with_text(self):
        """Verificar que brand-logo renderiza con texto por defecto"""
        template = Template('{% load core_tags %}{% brand_logo show_text=True %}')
        context = Context({})
        
        rendered = template.render(context)
        
        # Verificar estructura básica
        self.assertIn('brand-logo', rendered)
        self.assertIn('fa fa-headset', rendered)
        self.assertIn('Welp', rendered)
        self.assertIn('App', rendered)  # Default brand text
        self.assertIn(reverse('core:index'), rendered)  # Home URL

    def test_brand_logo_renders_without_text(self):
        """Verificar que brand-logo renderiza sin texto cuando show_text=False"""
        template = Template('{% load core_tags %}{% brand_logo show_text=False %}')
        context = Context({})
        
        rendered = template.render(context)
        
        # Verificar que no hay texto visible
        self.assertNotIn('hidden min-[30rem]:inline', rendered)
        self.assertIn('fa fa-headset', rendered)

    def test_brand_logo_desk_namespace(self):
        """Verificar brand-logo con namespace de desk"""
        template = Template('{% load core_tags %}{% brand_logo current_namespace="welp_desk:index" %}')
        context = Context({})
        
        rendered = template.render(context)
        
        self.assertIn('Desk', rendered)

    def test_brand_logo_payflow_namespace(self):
        """Verificar brand-logo con namespace de payflow"""
        template = Template('{% load core_tags %}{% brand_logo current_namespace="welp_payflow:home" %}')
        context = Context({})
        
        rendered = template.render(context)
        
        self.assertIn('Payflow', rendered)

    def test_brand_logo_includes_animations(self):
        """Verificar que brand-logo incluye CSS de animaciones"""
        template = Template('{% load core_tags %}{% brand_logo %}')
        context = Context({})
        
        rendered = template.render(context)
        
        # Verificar presencia de CSS de animación
        self.assertIn('@keyframes brief-glow', rendered)
        self.assertIn('icon-glow', rendered)
        self.assertIn('prefers-reduced-motion', rendered)

    def test_brand_logo_includes_javascript(self):
        """Verificar que brand-logo incluye JavaScript interactivo"""
        template = Template('{% load core_tags %}{% brand_logo %}')
        context = Context({})
        
        rendered = template.render(context)
        
        # Verificar JavaScript
        self.assertIn('DOMContentLoaded', rendered)
        self.assertIn('mouseenter', rendered)
        self.assertIn('mouseleave', rendered)
        self.assertIn('themeChanged', rendered)

    def test_nav_link_active_state(self):
        """Verificar nav-link en estado activo"""
        template = Template('{% load core_tags %}{% nav_link "core:index" "fa fa-home" "Inicio" current_view="core:index" %}')
        context = Context({})
        
        rendered = template.render(context)
        
        # Verificar estado activo
        self.assertIn('!text-[var(--navbar-link-active)]', rendered)
        self.assertIn('translate-x-[-0.05rem]', rendered)
        self.assertIn('fa fa-home', rendered)
        self.assertIn('Inicio', rendered)

    def test_nav_link_inactive_state(self):
        """Verificar nav-link en estado inactivo"""
        template = Template('{% load core_tags %}{% nav_link "core:dashboard" "fa fa-user" "Dashboard" current_view="core:index" %}')
        context = Context({})
        
        rendered = template.render(context)
        
        # Verificar estado inactivo (no debe tener clases activas)
        self.assertNotIn('!text-[var(--navbar-link-active)]', rendered)
        self.assertIn('fa fa-user', rendered)
        self.assertIn('Dashboard', rendered)

    def test_nav_link_special_app_labels(self):
        """Verificar nav-link con etiquetas especiales de aplicaciones"""
        # Test WelpDesk
        template = Template('{% load core_tags %}{% nav_link "welp_desk:index" "fa fa-headset" "WelpDesk" %}')
        context = Context({})
        
        rendered = template.render(context)
        
        # Verificar clases especiales para WelpDesk
        self.assertIn('brand-text-override', rendered)
        self.assertIn('hidden md:inline', rendered)
        self.assertIn('text-xl font-bold', rendered)

        # Test Welp Payflow
        template2 = Template('{% load core_tags %}{% nav_link "welp_payflow:index" "fa fa-user-check" "Welp Payflow" %}')
        rendered2 = template2.render(context)
        
        self.assertIn('brand-text-override', rendered2)
        self.assertIn('Welp Payflow', rendered2)

    def test_button_as_link(self):
        """Verificar button renderizado como enlace"""
        template = Template('{% load core_tags %}{% button "Ver Más" variant="secondary" href="/more/" icon="fa fa-eye" %}')
        context = Context({})
        
        rendered = template.render(context)
        
        # Verificar estructura de enlace
        self.assertIn('<a href="/more/"', rendered)
        self.assertIn('button-secondary', rendered)
        self.assertIn('fa fa-eye', rendered)
        self.assertIn('Ver Más', rendered)
        self.assertNotIn('<button', rendered)

    def test_button_as_button_element(self):
        """Verificar button renderizado como elemento button"""
        template = Template('{% load core_tags %}{% button "Guardar" variant="primary" type="submit" icon="fa fa-save" %}')
        context = Context({})
        
        rendered = template.render(context)
        
        # Verificar estructura de botón
        self.assertIn('<button type="submit"', rendered)
        self.assertIn('button-primary', rendered)
        self.assertIn('fa fa-save', rendered)
        self.assertIn('Guardar', rendered)
        self.assertNotIn('<a href', rendered)

    def test_button_with_onclick(self):
        """Verificar button con evento onclick"""
        template = Template('{% load core_tags %}{% button "Eliminar" variant="danger" onclick="confirm(\'¿Estás seguro?\')" %}')
        context = Context({})
        
        rendered = template.render(context)
        
        self.assertIn('onclick="confirm(\'¿Estás seguro?\')"', rendered)
        self.assertIn('button-danger', rendered)

    def test_button_disabled_state(self):
        """Verificar button en estado deshabilitado"""
        template = Template('{% load core_tags %}{% button "Procesando" disabled=True %}')
        context = Context({})
        
        rendered = template.render(context)
        
        self.assertIn('disabled', rendered)
        self.assertIn('Procesando', rendered)

    def test_button_with_target_blank(self):
        """Verificar button con target _blank"""
        template = Template('{% load core_tags %}{% button "Abrir Enlace" href="https://example.com" target="_blank" %}')
        context = Context({})
        
        rendered = template.render(context)
        
        self.assertIn('target="_blank"', rendered)
        self.assertIn('href="https://example.com"', rendered)

    def test_button_extra_classes(self):
        """Verificar button con clases CSS adicionales"""
        template = Template('{% load core_tags %}{% button "Custom" extra_classes="ml-4 shadow-lg" %}')
        context = Context({})
        
        rendered = template.render(context)
        
        self.assertIn('ml-4 shadow-lg', rendered)

    def test_logout_component_rendering(self):
        """Verificar componente logout renderiza correctamente"""
        template = Template('{% load core_tags %}{% logout_link user=user %}')
        context = Context({'user': self.test_user})
        
        rendered = template.render(context)
        
        # Verificar estructura básica
        self.assertIn('fa fa-sign-out', rendered)
        self.assertIn('testuser', rendered)  # Username truncado
        self.assertIn('logout-form', rendered)
        self.assertIn('csrf_token', rendered)
        self.assertIn(reverse('core:logout'), rendered)

    def test_logout_component_long_username(self):
        """Verificar logout con username largo (truncado)"""
        long_user = User.objects.create_user(username='verylongusername')
        template = Template('{% load core_tags %}{% logout_link user=user %}')
        context = Context({'user': long_user})
        
        rendered = template.render(context)
        
        # Username debe truncarse a 8 caracteres
        self.assertIn('verylong...', rendered)

    def test_logout_component_no_user(self):
        """Verificar logout sin usuario"""
        template = Template('{% load core_tags %}{% logout_link %}')
        context = Context({})
        
        rendered = template.render(context)
        
        self.assertIn('logout', rendered)  # Fallback text

    def test_separator_component_default(self):
        """Verificar separator por defecto"""
        template = Template('{% load core_tags %}{% separator %}')
        context = Context({})
        
        rendered = template.render(context)
        
        # Verificar estructura básica (aunque es muy simple)
        self.assertIsInstance(rendered, str)
        self.assertNotEqual(rendered.strip(), '')

    def test_separator_component_custom_classes(self):
        """Verificar separator con clases personalizadas"""
        template = Template('{% load core_tags %}{% separator custom_classes="border-red-500 mx-8" %}')
        context = Context({})
        
        rendered = template.render(context)
        
        self.assertIn('border-red-500 mx-8', rendered)

    def test_status_badge_desk_system(self):
        """Verificar status-badge para sistema desk"""
        template = Template('{% load core_tags %}{% status_badge "open" system="desk" %}')
        context = Context({})
        
        rendered = template.render(context)
        
        self.assertIn('status-open', rendered)
        self.assertIn('Abierto', rendered)

    def test_status_badge_payflow_system(self):
        """Verificar status-badge para sistema payflow"""
        template = Template('{% load core_tags %}{% status_badge "authorized" system="payflow" %}')
        context = Context({})
        
        rendered = template.render(context)
        
        self.assertIn('status-authorized', rendered)
        self.assertIn('Autorizado', rendered)

    def test_status_badge_with_variant(self):
        """Verificar status-badge con variante"""
        template = Template('{% load core_tags %}{% status_badge "open" variant="outline" %}')
        context = Context({})
        
        rendered = template.render(context)
        
        self.assertIn('status-outline', rendered)

    def test_status_badge_custom_label(self):
        """Verificar status-badge con etiqueta personalizada"""
        template = Template('{% load core_tags %}{% status_badge "open" label="Estado Especial" %}')
        context = Context({})
        
        rendered = template.render(context)
        
        self.assertIn('Estado Especial', rendered)


class ComponentAccessibilityTest(TestCase):
    """
    Suite de pruebas para verificar accesibilidad básica de componentes.
    
    Verifica que los componentes incluyan atributos apropiados
    para accesibilidad y usabilidad.
    """

    def test_nav_link_has_proper_structure(self):
        """Verificar que nav-link tiene estructura accesible"""
        template = Template('{% load core_tags %}{% nav_link "core:index" "fa fa-home" "Inicio" %}')
        context = Context({})
        
        rendered = template.render(context)
        
        # Verificar estructura semántica
        self.assertIn('<a href=', rendered)
        self.assertIn('no-underline', rendered)  # Estilo controlado por CSS

    def test_button_semantic_structure(self):
        """Verificar estructura semántica de button"""
        template = Template('{% load core_tags %}{% button "Enviar" type="submit" %}')
        context = Context({})
        
        rendered = template.render(context)
        
        self.assertIn('type="submit"', rendered)
        # Button debe tener tipo explícito

    def test_logout_form_has_csrf(self):
        """Verificar que logout incluye protección CSRF"""
        template = Template('{% load core_tags %}{% logout_link %}')
        context = Context({})
        
        rendered = template.render(context)
        
        self.assertIn('csrf_token', rendered)
        self.assertIn('method="post"', rendered)

    def tearDown(self):
        """Limpieza tras cada test"""
        User.objects.all().delete() 