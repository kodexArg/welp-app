from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    Configuración de la aplicación core.
    
    Esta clase define la configuración principal de la aplicación core,
    incluyendo el campo de auto-incremento por defecto y el nombre de la aplicación.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """Importar componentes para registrarlos"""
        try:
            from components.core.ping import ping
        except ImportError:
            pass
