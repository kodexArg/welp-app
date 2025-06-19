from django.apps import AppConfig


class WelpPayConfig(AppConfig):
    """
    Configuración de la aplicación Welp Pay.
    
    Esta clase define la configuración principal de la aplicación welp_pay,
    para el sistema de pagos y facturación.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'welp_pay'

    def ready(self):
        """Importar componentes de welp_pay para registrarlos automáticamente"""
        import importlib
        import os
        import sys

        components_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "components", "welp_pay")
        if os.path.isdir(components_dir):
            for name in os.listdir(components_dir):
                comp_path = os.path.join(components_dir, name, f"{name}.py")
                if os.path.isfile(comp_path):
                    module_name = f"components.welp_pay.{name}.{name}"
                    if module_name not in sys.modules:
                        importlib.import_module(module_name) 