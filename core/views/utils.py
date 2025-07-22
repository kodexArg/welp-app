"""
Utilidades auxiliares para las vistas.

Este módulo contiene funciones de apoyo utilizadas por múltiples vistas
del sistema, como formateo de fechas, procesamiento de datos, etc.
"""
from datetime import datetime, timezone, timedelta
from django.utils import timezone as django_timezone

def format_relative_date(date_obj):
    """
    Formatea una fecha de manera relativa en español.
    
    Args:
        date_obj: datetime object o fecha a formatear
        
    Returns:
        str: Fecha formateada relativamente
        
    Ejemplos:
        - hace 20 minutos
        - ayer  
        - 24 de marzo
        - 30 de abril de 2024
    """
    if not date_obj:
        return "fecha desconocida"
    
    # Asegurar que tenemos timezone info
    if hasattr(date_obj, 'tzinfo') and date_obj.tzinfo is None:
        date_obj = django_timezone.make_aware(date_obj)
    
    now = django_timezone.now()
    
    # Calcular diferencia
    diff = now - date_obj
    
    # Para fechas futuras (edge case)
    if diff.total_seconds() < 0:
        return date_obj.strftime("%-d de %B")
    
    # Menos de 1 hora: "hace X minutos"
    if diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() / 60)
        if minutes <= 1:
            return "hace un momento"
        return f"hace {minutes} minutos"
    
    # Menos de 24 horas: "hace X horas"
    if diff.days == 0:
        hours = int(diff.total_seconds() / 3600)
        if hours == 1:
            return "hace una hora"
        return f"hace {hours} horas"
    
    # Ayer
    if diff.days == 1:
        return "ayer"
    
    # Menos de 7 días: "hace X días"
    if diff.days < 7:
        return f"hace {diff.days} días"
    
    # Mismo año: "24 de marzo"
    if date_obj.year == now.year:
        months = [
            '', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
        ]
        return f"{date_obj.day} de {months[date_obj.month]}"
    
    # Años pasados: "30 de abril de 2024"
    months = [
        '', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
    ]
    return f"{date_obj.day} de {months[date_obj.month]} de {date_obj.year}" 