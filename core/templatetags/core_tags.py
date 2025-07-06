from django import template
from django.urls import reverse, NoReverseMatch
from django.utils.safestring import mark_safe
from django.utils.html import format_html

from welp_desk.constants import DESK_STATUSES
from welp_payflow.constants import PAYFLOW_STATUSES
from welp_payflow.utils import get_available_payflow_transitions

register = template.Library()

@register.inclusion_tag('components/core/brand-logo.html')
def brand_logo(show_text=False, current_namespace=None):
    """
    Componente del logo de la marca
    
    Args:
        show_text (bool): Si mostrar el texto "Welp" junto al logo
        current_namespace (str): Namespace actual para determinar el color
    
    Returns:
        dict: Contexto para el template
    """
    return {
        'show_text': show_text,
        'current_namespace': current_namespace,
    }

@register.inclusion_tag('components/core/nav-link.html')
def nav_link(link, icon, label, current_view=None, always_show_label=False):
    """
    Componente de enlace de navegación que se ilumina cuando está seleccionado
    
    Args:
        link (str): Nombre de la URL de Django
        icon (str): Clases CSS del ícono (ej: 'fa fa-home')
        label (str): Texto del enlace
        current_view (str): Vista actual para determinar estado activo
        always_show_label (bool): Si siempre mostrar el label o solo en md+
    
    Returns:
        dict: Contexto para el template
    """
    is_active = False
    if current_view:
        if current_view == link:
            is_active = True
        elif current_view == 'index' and link == 'core:index':
            is_active = True
    
    return {
        'link': link,
        'icon': icon,
        'label': label,
        'active': is_active,
        'always_show_label': always_show_label,
    }

@register.inclusion_tag('components/core/separator.html')
def separator():
    """
    Componente de separador visual
    
    Returns:
        dict: Contexto para el template
    """
    return {}

@register.inclusion_tag('components/core/logout-link.html')
def logout_link(user):
    """
    Componente de enlace de cierre de sesión
    
    Args:
        user (User): Usuario autenticado
    
    Returns:
        dict: Contexto para el template
    """
    return {
        'user': user
    }

@register.inclusion_tag('components/core/treemap.html')
def treemap_component(items, field_name, selected_values=None, clear_enabled=True):
    """
    Componente de mapa de árbol para selección múltiple
    
    Args:
        items (list): Lista de items a mostrar
        field_name (str): Nombre del campo del formulario
        selected_values (list): Valores seleccionados
        clear_enabled (bool): Si mostrar el botón de limpiar
    
    Returns:
        dict: Contexto para el template
    """
    if selected_values is None:
        selected_values = []
    
    return {
        'items': items,
        'field_name': field_name,
        'selected_values': selected_values,
        'clear_enabled': clear_enabled,
    }

@register.inclusion_tag('components/core/loading-spinner.html')
def loading_spinner(text=None, size='md'):
    """
    Componente de spinner de carga
    
    Args:
        text (str): Texto opcional a mostrar
        size (str): Tamaño del spinner ('sm', 'md', 'lg')
    
    Returns:
        dict: Contexto para el template
    """
    return {
        'text': text,
        'size': size,
    }

@register.inclusion_tag('components/core/app-wide-button.html')
def app_wide_button(url, icon, title, description, variant='primary'):
    """
    Componente de botón grande para aplicaciones
    
    Args:
        url (str): URL de destino
        icon (str): Clases CSS del ícono
        title (str): Título del botón
        description (str): Descripción
        variant (str): Variante de estilo ('primary', 'secondary')
    
    Returns:
        dict: Contexto para el template
    """
    return {
        'url': url,
        'icon': icon,
        'title': title,
        'description': description,
        'variant': variant,
    }

@register.inclusion_tag('components/core/status-badge.html')
def status_badge(status, label=None, variant=None, system='desk'):
    """
    Componente de badge de estado para tickets
    
    Args:
        status (str): Estado del ticket
        label (str): Etiqueta personalizada (opcional)
        variant (str): Variante de estilo (solid, outline) (opcional)
        system (str): Sistema de origen ('desk' o 'payflow')
    
    Returns:
        dict: Contexto para el template
    """
    if system == 'payflow':
        status_labels = {key: value['label'] for key, value in PAYFLOW_STATUSES.items()}
    else:
        status_labels = {key: value['label'] for key, value in DESK_STATUSES.items()}
    
    return {
        'status': status,
        'label': label or status_labels.get(status, status.title() if status else 'Sin Estado'),
        'variant': variant,
        'system': system,
    }

@register.inclusion_tag('components/core/theme-selector.html')
def theme_selector(show_text=False, style='button'):
    """
    Componente de selector de tema multi-theme
    
    Args:
        show_text (bool): Si mostrar el texto del tema junto al ícono
        style (str): Estilo del selector ('button', 'dropdown')
    
    Returns:
        dict: Contexto para el template
    """
    return {
        'show_text': show_text,
        'style': style,
    }