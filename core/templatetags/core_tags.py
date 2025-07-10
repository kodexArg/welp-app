from django import template
from django.urls import reverse
from welp_desk.constants import DESK_STATUSES
from welp_payflow.constants import PAYFLOW_STATUSES, PAYFLOW_STATUS_FLOW
from welp_payflow.utils import can_user_close_ticket, get_user_ticket_transitions

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
        'form': form,
    }

@register.inclusion_tag("components/core/ticket_header.html")
def ticket_header(ticket):
    return {"ticket": ticket}

@register.inclusion_tag("components/core/ticket_message.html")
def ticket_message(message):
    return {"message": message}


def get_ticket_action_data(action, ticket_id=None):
    """Obtiene datos simplificados para acciones de tickets usando íconos FontAwesome"""
    from django.urls import reverse
    
    # Definiciones simplificadas en el componente con íconos FA
    # NOTA: 'close' y 'closed' no deben ser procesados aquí
    action_data = {
        'feedback': {'label': 'COMENTAR', 'fa_icon': 'fa-regular fa-comment'},
        'authorized': {'label': 'AUTORIZAR', 'fa_icon': 'fa-solid fa-check'},
        'budgeted': {'label': 'PRESUPUESTAR', 'fa_icon': 'fa-solid fa-file-invoice-dollar'},
        'rejected': {'label': 'RECHAZAR', 'fa_icon': 'fa-solid fa-ban'},
        'payment_authorized': {'label': 'AUTORIZAR PAGO', 'fa_icon': 'fa-solid fa-credit-card'},
        'processing_payment': {'label': 'PROCESAR PAGO', 'fa_icon': 'fa-solid fa-money-bill-transfer'},
        'shipping': {'label': 'ENVÍO', 'fa_icon': 'fa-solid fa-truck'},
    }
    
    # Retornar None para acciones inválidas
    if action in ['close', 'closed']:
        return None
    
    info = action_data.get(action, {'label': action.upper(), 'fa_icon': 'fa-solid fa-circle'})
    
    # Generar URL
    href = '#'
    if ticket_id:
        try:
            if action == 'feedback':
                href = reverse('welp_payflow:detail', kwargs={'ticket_id': ticket_id})
            else:
                href = reverse('welp_payflow:detail', kwargs={'ticket_id': ticket_id}) + f'?response_type={action}'
        except Exception:
            href = '#'
    
    return {
        'action': action,
        'href': href,
        'label': info['label'],
        'fa_icon': info['fa_icon'],
    }

@register.inclusion_tag("components/core/ticket_actions.html", takes_context=True)
def ticket_actions(context, ticket):
    user = context['request'].user if 'request' in context else None
    can_close_ticket = can_user_close_ticket(user, ticket) if user else False
    transition_buttons = get_user_ticket_transitions(user, ticket)
    
    # Preparar datos de acciones
    actions_data = []
    
    # Solo agregar transiciones válidas (excluir 'closed' y 'close')
    for action in transition_buttons:
        if action not in ['closed', 'close']:
            action_data = get_ticket_action_data(action, ticket.id)
            if action_data:  # Solo agregar si no es None
                actions_data.append(action_data)
    
    # Siempre agregar feedback al final
    feedback_data = get_ticket_action_data('feedback', ticket.id)
    if feedback_data:
        actions_data.append(feedback_data)
    
    return {
        "ticket": ticket,
        "actions_data": actions_data,
        "can_close_ticket": can_close_ticket,
    }

@register.inclusion_tag("components/core/ticket_message_input.html")
def ticket_message_input(form_action, button_text="Agregar Comentario", label_text="Comentario", 
                        placeholder="Escriba su comentario aquí...", cancel_url=None, 
                        required=True, show_attachments=False, field_name="response_body",
                        cancel_text="Cancelar", hidden_fields=None):
    """
    Componente reutilizable para input de mensajes de tickets
    
    Args:
        form_action (str): URL de acción del formulario
        button_text (str): Texto del botón de envío
        label_text (str): Etiqueta del campo de texto
        placeholder (str): Placeholder del textarea
        cancel_url (str): URL de cancelación (opcional)
        required (bool): Si el campo es obligatorio
        show_attachments (bool): Si mostrar sección de archivos adjuntos
        field_name (str): Nombre del campo en el formulario
        cancel_text (str): Texto del botón de cancelar
        hidden_fields (dict): Campos ocultos del formulario
    
    Returns:
        dict: Contexto para el template
    """
    return {
        'form_action': form_action,
        'button_text': button_text,
        'label_text': label_text,
        'placeholder': placeholder,
        'cancel_url': cancel_url,
        'required': required,
        'show_attachments': show_attachments,
        'field_name': field_name,
        'cancel_text': cancel_text,
        'hidden_fields': hidden_fields or {},
    }

@register.inclusion_tag("components/core/pagination.html")
def pagination(page_obj, request):
    return {"page_obj": page_obj, "request": request}

@register.inclusion_tag('components/core/radio-button.html')
def radio_button(target, id, label, next_target, visible=True):
    try:
        from django.urls import reverse
        full_url = reverse(f'welp_payflow:htmx-{next_target}', kwargs={target: id})
    except Exception:
        full_url = ''

    return {
        'target': target,
        'id': id,
        'label': label,
        'next_target': next_target,
        'full_url': full_url,
        'visible': visible,
    }

@register.inclusion_tag('components/core/ticket_container.html', takes_context=True)
def ticket_container(context, ticket, expanded=False, hide_buttons=False):
    ctx = context.flatten() if hasattr(context, 'flatten') else dict(context)
    return {'ticket': ticket, 'expanded': expanded, 'hide_buttons': hide_buttons, **ctx}

@register.inclusion_tag('components/core/ticket_empty.html')
def ticket_empty():
    return {}

@register.filter
def get_status_flow(ticket):
    """
    Obtiene la información del flujo de estado del ticket
    
    Args:
        ticket: Ticket de PayFlow
    
    Returns:
        dict: Información del estado actual y siguiente acción
    """
    try:
        if not ticket or not hasattr(ticket, 'status'):
            return {
                'current_action': 'Estado desconocido',
                'next_action': None,
                'is_waiting': False,
                'priority': 'none'
            }
        
        status = ticket.status or 'open'
        flow_info = PAYFLOW_STATUS_FLOW.get(status)
        
        if not flow_info:
            return {
                'current_action': f'Estado: {status}',
                'next_action': None,
                'is_waiting': False,
                'priority': 'none'
            }
        
        return flow_info
    except Exception:
        return {
            'current_action': 'Error al obtener estado',
            'next_action': None,
            'is_waiting': False,
            'priority': 'none'
        }

@register.filter
def get_status_label(status, system='payflow'):
    """
    Obtiene la etiqueta legible del estado
    
    Args:
        status (str): Estado del ticket
        system (str): Sistema de origen ('desk' o 'payflow')
    
    Returns:
        str: Etiqueta legible del estado
    """
    if system == 'payflow':
        return PAYFLOW_STATUSES.get(status, {}).get('label', status.title() if status else 'Sin Estado')
    else:
        return DESK_STATUSES.get(status, {}).get('label', status.title() if status else 'Sin Estado')

@register.inclusion_tag('components/core/ticket_status.html')
def ticket_status(ticket):
    """
    Componente de estado del ticket con información de flujo
    
    Args:
        ticket: Ticket de PayFlow
    
    Returns:
        dict: Contexto para el template
    """
    return {'ticket': ticket}

@register.filter
def get_ticket_action_info(ticket):
    """
    Dado un ticket, retorna un dict con la acción esperada, ícono y color según el estado actual.
    """
    status = getattr(ticket, 'status', None) or 'open'
    status_info = PAYFLOW_STATUSES.get(status, {})
    flow_info = PAYFLOW_STATUS_FLOW.get(status, {})
    return {
        'icon': status_info.get('icon', ''),
        'color': status_info.get('color', ''),
        'label': status_info.get('label', status.title()),
        'status': status,
        'current_action': flow_info.get('current_action', ''),
        'next_action': flow_info.get('next_action', ''),
    }

@register.filter
def get_ticket_comment_count(ticket):
    """
    Retorna la cantidad de mensajes que son comentarios (no transiciones de estado).
    Un comentario es un mensaje cuyo status es igual al status del mensaje anterior (no cambia el estado) y tiene body no vacío.
    Si no es posible comparar, cuenta como comentario todo mensaje cuyo status es igual al status actual del ticket y tiene body no vacío.
    """
    if not ticket:
        return 0
    messages = list(ticket.messages.order_by('created_on'))
    if not messages:
        return 0
    count = 0
    prev_status = None
    for msg in messages:
        if prev_status is not None and msg.status == prev_status and msg.body and msg.body.strip():
            count += 1
        prev_status = msg.status
    # fallback: si no hay ninguno detectado, cuenta los mensajes cuyo status es igual al status actual del ticket
    if count == 0:
        status = getattr(ticket, 'status', None)
        if status:
            count = ticket.messages.filter(status=status).exclude(body__isnull=True).exclude(body__exact='').count()
    return count

@register.filter
def get_item(dictionary, key):
    """
    Permite acceder a un valor de un diccionario por clave en los templates.
    Usage: {{ dict|get_item:key }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''