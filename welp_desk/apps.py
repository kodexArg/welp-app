from django.apps import AppConfig


class WelpDeskConfig(AppConfig):
    """
    Configuración de la aplicación Welp Desk.
    
    Esta clase define la configuración principal de la aplicación welp_desk,
    para el sistema de mesa de ayuda y soporte técnico.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'welp_desk'

    def ready(self):
        """Importar componentes de welp_desk para registrarlos automáticamente"""
        import importlib
        import os
        import sys

        components_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "components", "welp_desk")
        if os.path.isdir(components_dir):
            for name in os.listdir(components_dir):
                comp_path = os.path.join(components_dir, name, f"{name}.py")
                if os.path.isfile(comp_path):
                    module_name = f"components.welp_desk.{name}.{name}"
                    if module_name not in sys.modules:
                        importlib.import_module(module_name) 