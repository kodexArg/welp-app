from django import template
from django.urls import reverse
from welp_desk.constants import DESK_STATUSES
from welp_payflow.constants import PAYFLOW_STATUSES

register = template.Library()

@register.inclusion_tag('components/core/brand-logo.html')
def brand_logo(show_text=True, current_namespace=None):
    """
    Componente de logo de marca con animación
    
    Args:
        show_text (bool): Si mostrar el texto o solo el ícono
        current_namespace (str): Namespace actual para determinar el texto
    
    Returns:
        dict: Contexto para el template
    """
    if current_namespace and 'welp_payflow' in current_namespace:
        brand_text = 'Payflow'
    elif current_namespace and 'welp_desk' in current_namespace:
        brand_text = 'Desk'
    else:
        brand_text = 'App'
    
    return {
        'show_text': show_text,
        'home_url': reverse('core:index'),
        'brand_text': brand_text,
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

@register.inclusion_tag('components/core/logout.html')
def logout_link(user=None, active=False):
    """
    Componente de enlace de logout
    
    Args:
        user (User): Usuario actual
        active (bool): Si el enlace está activo
    
    Returns:
        dict: Contexto para el template
    """
    return {
        'user': user,
        'active': active,
    }

@register.inclusion_tag('components/core/separator.html')
def separator(custom_classes=""):
    """
    Componente separador para navbar
    
    Args:
        custom_classes (str): Clases CSS adicionales
    
    Returns:
        dict: Contexto para el template
    """
    return {
        'custom_classes': custom_classes,
    }


@register.inclusion_tag('components/core/button.html')
def button(text, variant='primary', href=None, icon=None, onclick=None, type='button', target=None, disabled=False, extra_classes=""):
    """
    Componente de botón genérico
    
    Args:
        text (str): Texto del botón
        variant (str): Variante del botón (primary, secondary, success, danger, cancel, minimal)
        href (str): URL si es un enlace
        icon (str): Clases CSS del ícono
        onclick (str): Código JavaScript para el evento click
        type (str): Tipo del botón (button, submit, reset)
        target (str): Target del enlace (_blank, etc.)
        disabled (bool): Si el botón está deshabilitado
        extra_classes (str): Clases CSS adicionales
    
    Returns:
        dict: Contexto para el template
    """
    return {
        'text': text,
        'variant': variant,
        'href': href,
        'icon': icon,
        'onclick': onclick,
        'type': type,
        'target': target,
        'disabled': disabled,
        'extra_classes': extra_classes,
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

@register.inclusion_tag('components/core/select-field.html')
def select_field(field, help_text=None):
    """
    Componente de campo de selección minimalista
    
    Args:
        field (forms.Field): Campo de formulario Django
        help_text (str): Texto de ayuda adicional
    
    Returns:
        dict: Contexto para el template
    """
    return {
        'field': field,
        'help_text': help_text,
    }

@register.inclusion_tag('components/core/select-fields-body.html')
def select_fields_body(form):
    """
    Componente de cuerpo de campos de formulario con título, descripción, monto y archivos
    
    Args:
        form (forms.Form): Formulario Django con los campos necesarios
    
    Returns:
        dict: Contexto para el template
    """
    return {
        'form': form,    }



