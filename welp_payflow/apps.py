from django.apps import AppConfig


class PayflowConfig(AppConfig):
    """
    Configuración de la aplicación Payflow.
    
    Esta clase define la configuración principal de la aplicación welp_payflow,
    para el sistema de pagos y facturación.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'welp_payflow' 