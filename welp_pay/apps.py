from django.apps import AppConfig


class WelpPayConfig(AppConfig):
    """
    Configuración de la aplicación Welp Pay.
    
    Esta clase define la configuración principal de la aplicación welp_pay,
    para el sistema de pagos y facturación.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'welp_pay' 