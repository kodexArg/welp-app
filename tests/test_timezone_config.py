import os
import yaml
import zoneinfo
from django.test import TestCase
from django.conf import settings
from pathlib import Path


class TimezoneConfigTest(TestCase):
    """
    Suite de pruebas para verificar la configuración correcta del timezone.
    """

    def test_timezone_environment_variable_exists(self):
        """
        TEST #1 - Verificar que la variable TIMEZONE existe y no está vacía.
        """
        timezone_value = os.environ.get('TIMEZONE')
        self.assertIsNotNone(timezone_value, "La variable de entorno TIMEZONE debe estar definida")
        self.assertNotEqual(timezone_value.strip(), "", "La variable TIMEZONE no puede estar vacía")

    def test_timezone_is_valid_zoneinfo(self):
        """
        TEST #2 - Verificar que el timezone configurado es válido según zoneinfo.
        """
        try:
            tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)
            # Verificar que se puede crear una instancia válida
            self.assertIsNotNone(tz)
        except zoneinfo.ZoneInfoNotFoundError:
            self.fail(f"El timezone '{settings.TIME_ZONE}' no es válido según zoneinfo")
        except Exception as e:
            self.fail(f"Error al validar timezone '{settings.TIME_ZONE}': {e}")

    def test_apprunner_yaml_contains_timezone(self):
        """
        TEST #3 - Verificar que apprunner.yaml contiene la variable TIMEZONE.
        """
        apprunner_path = Path(__file__).parent.parent / 'apprunner.yaml'
        self.assertTrue(apprunner_path.exists(), "El archivo apprunner.yaml debe existir")
        
        with open(apprunner_path, 'r', encoding='utf-8') as f:
            apprunner_config = yaml.safe_load(f)
        
        # Verificar que existe la sección run.env
        self.assertIn('run', apprunner_config, "apprunner.yaml debe tener sección 'run'")
        self.assertIn('env', apprunner_config['run'], "apprunner.yaml debe tener 'run.env'")
        
        # Buscar la variable TIMEZONE en la lista de env
        env_vars = apprunner_config['run']['env']
        timezone_found = False
        timezone_value = None
        
        for env_var in env_vars:
            if env_var.get('name') == 'TIMEZONE':
                timezone_found = True
                timezone_value = env_var.get('value')
                break
        
        self.assertTrue(timezone_found, "apprunner.yaml debe contener la variable TIMEZONE en run.env")
        self.assertIsNotNone(timezone_value, "La variable TIMEZONE en apprunner.yaml debe tener un valor")
        self.assertNotEqual(timezone_value.strip(), "", "La variable TIMEZONE en apprunner.yaml no puede estar vacía")

    def test_apprunner_timezone_is_valid(self):
        """
        TEST #4 - Verificar que el timezone en apprunner.yaml sea válido.
        """
        apprunner_path = Path(__file__).parent.parent / 'apprunner.yaml'
        
        with open(apprunner_path, 'r', encoding='utf-8') as f:
            apprunner_config = yaml.safe_load(f)
        
        # Extraer el valor de TIMEZONE de apprunner.yaml
        env_vars = apprunner_config['run']['env']
        timezone_value = None
        
        for env_var in env_vars:
            if env_var.get('name') == 'TIMEZONE':
                timezone_value = env_var.get('value')
                break
        
        # Verificar que el timezone es válido
        try:
            tz = zoneinfo.ZoneInfo(timezone_value)
            self.assertIsNotNone(tz)
        except zoneinfo.ZoneInfoNotFoundError:
            self.fail(f"El timezone '{timezone_value}' en apprunner.yaml no es válido según zoneinfo")
        except Exception as e:
            self.fail(f"Error al validar timezone '{timezone_value}' de apprunner.yaml: {e}")

    def test_settings_and_apprunner_timezone_match(self):
        """
        TEST #5 - Verificar que el timezone en settings.py coincida con apprunner.yaml.
        """
        apprunner_path = Path(__file__).parent.parent / 'apprunner.yaml'
        
        with open(apprunner_path, 'r', encoding='utf-8') as f:
            apprunner_config = yaml.safe_load(f)
        
        # Extraer timezone de apprunner.yaml
        env_vars = apprunner_config['run']['env']
        apprunner_timezone = None
        
        for env_var in env_vars:
            if env_var.get('name') == 'TIMEZONE':
                apprunner_timezone = env_var.get('value')
                break
        
        # Comparar con settings
        settings_timezone = settings.TIME_ZONE
        
        self.assertEqual(
            settings_timezone, 
            apprunner_timezone,
            f"El timezone en settings.py ('{settings_timezone}') debe coincidir con apprunner.yaml ('{apprunner_timezone}')"
        )

    def test_timezone_is_argentina_mendoza(self):
        """
        TEST #6 - Verificar que específicamente sea el timezone de Mendoza, Argentina.
        """
        expected_timezone = "America/Argentina/Mendoza"
        self.assertEqual(
            settings.TIME_ZONE,
            expected_timezone,
            f"El timezone debe ser '{expected_timezone}' pero es '{settings.TIME_ZONE}'"
        ) 