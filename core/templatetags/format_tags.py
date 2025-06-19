from django import template
from django.utils import timezone
from django.conf import settings
import zoneinfo

register = template.Library()

@register.filter
def local_datetime(value):
    """
    Convierte una fecha/hora a la zona horaria local configurada
    
    Usage: {{ date|local_datetime }}
    """
    if not value:
        return value
    
    try:
        tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)
        return value.astimezone(tz)
    except:
        return value

@register.filter
def user_display_name(user):
    """
    Devuelve el nombre completo del usuario o su username
    
    Usage: {{ user|user_display_name }}
    """
    if not user:
        return 'Usuario'
    
    if hasattr(user, 'get_full_name'):
        full_name = user.get_full_name()
        if full_name and full_name.strip():
            return full_name
    
    return user.username if hasattr(user, 'username') else str(user)

@register.simple_tag
def current_time():
    """
    Devuelve la hora actual en la zona horaria configurada
    
    Usage: {% current_time %}
    """
    try:
        tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)
        return timezone.now().astimezone(tz)
    except:
        return timezone.now()