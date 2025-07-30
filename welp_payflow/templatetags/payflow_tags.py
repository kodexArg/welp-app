from django import template
from django.urls import reverse
from django.utils.html import format_html
from welp_desk.constants import DESK_STATUSES
from welp_payflow.constants import PAYFLOW_STATUSES, FA_ICONS, PAYFLOW_FILTERS, FILTER_THEMES
from welp_payflow.utils import get_ticket_actions_context

register = template.Library()

@register.inclusion_tag('welp_payflow/components/filter_button.html')
def filter_button(filter_id, is_active=None, request_params=None):
    """Componente de botón de filtro configurable para Welp Payflow."""
    filter_config = PAYFLOW_FILTERS.get(filter_id, {})
    if not filter_config:
        return {'visible': False}
    
    theme_name = filter_config.get('theme', 'earth')
    theme_config = FILTER_THEMES.get(theme_name, FILTER_THEMES['earth'])
    
    # Determinar estado activo
    if is_active is None:
        is_active = filter_config.get('default_active', False)
    
    # Construir URL de toggle
    url_param = filter_config.get('url_param', filter_id)
    toggle_value = 'false' if is_active else 'true'
    
    return {
        'visible': True,
        'filter_id': filter_id,
        'label': filter_config.get('label', filter_id.replace('_', ' ').title()),
        'icon': filter_config.get('icon', 'fa-solid fa-filter'),
        'description': filter_config.get('description', ''),
        'is_active': is_active,
        'url_param': url_param,
        'toggle_value': toggle_value,
        'theme': theme_config,
    }

@register.inclusion_tag('welp_payflow/components/radio-button.html')
def radio_button(target, id, label, next_target, visible=True):
    """Componente radio-button HTMX usado en Welp Payflow."""
    try:
        kwarg_key = target
        url_name = f'welp_payflow:htmx-{next_target}'
        if next_target == 'sector':
            kwarg_key = 'udn'
            url_name = 'welp_payflow:htmx-sector'
        elif next_target == 'accounting-category':
            kwarg_key = 'sector'
            url_name = 'welp_payflow:htmx-accounting-category'
        elif next_target == 'fields-body':
            kwarg_key = 'accounting_category'
            url_name = 'welp_payflow:htmx-fields-body'
        
        full_url = reverse(url_name, kwargs={kwarg_key: id})
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

@register.inclusion_tag('welp_payflow/components/status-badge.html')
def status_badge(status, label=None, variant=None, system='desk'):
    """Badge de estado para tickets."""
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

@register.inclusion_tag('welp_payflow/components/mermaid_workflow.html')
def mermaid_workflow(ticket):
    """
    Genera el diagrama de flujo de Mermaid con estilos condicionales.
    Por defecto, todos los nodos son grises. Solo se colorean los nodos
    correspondientes a los estados que existen en el historial de mensajes del ticket.
    Incluye información de usuarios para cada nodo que tenga mensajes asociados.
    """
    styles = {}
    gray_style = "fill:#f3f4f6,stroke:#e5e7eb,stroke-width:2px,color:#9ca3b9,rx:20,ry:20"

    # 1. Inicializar todos los nodos del gráfico en gris.
    workflow_nodes = {
        data['mermaid_node']: gray_style
        for slug, data in PAYFLOW_STATUSES.items() if 'mermaid_node' in data
    }
    
    # 2. Obtener los estados únicos del historial de mensajes del ticket.
    message_statuses = set(ticket.messages.values_list('status', flat=True))
    
    # 3. Crear un diccionario para mapear nodos a usuarios
    node_users = {}
    
    # 4. Obtener información de usuarios para cada estado
    for status_slug in message_statuses:
        if status_slug in PAYFLOW_STATUSES:
            status_info = PAYFLOW_STATUSES[status_slug]
            if 'mermaid_node' in status_info:
                node_id = status_info['mermaid_node']
                # Obtener el último mensaje de este estado para obtener el usuario
                last_message = ticket.messages.filter(status=status_slug).order_by('-created_on').first()
                if last_message and last_message.user:
                    user_name = last_message.user.get_full_name() or last_message.user.username
                    node_users[node_id] = user_name
                elif status_slug == 'payment_authorized' and last_message and not last_message.user:
                    # Caso especial para mensajes del sistema
                    node_users[node_id] = "Sistema"
    
    # 5. Sobrescribir el estilo gris con el estilo de color para los estados existentes.
    for status_slug in message_statuses:
        if status_slug in PAYFLOW_STATUSES:
            status_info = PAYFLOW_STATUSES[status_slug]
            if 'mermaid_node' in status_info and 'mermaid_style' in status_info:
                node_id = status_info['mermaid_node']
                workflow_nodes[node_id] = status_info['mermaid_style']
    
    return {'styles': workflow_nodes, 'node_users': node_users}


@register.inclusion_tag('welp_payflow/components/action-button.html')
def payflow_action_button(ticket, action_type, user_can_transition=True, is_owner=False):
    action_info = PAYFLOW_STATUSES.get(action_type, {}).get('ui', {})
    if not action_info:
        action_info = PAYFLOW_STATUSES.get('comment', {}).get('ui', {})
        if action_type == 'comment':
            user_can_transition = True
    if not action_info or not user_can_transition:
        return {'visible': False}
    button_text = action_info.get('button_text', action_type.replace('_', ' ').title())
    color_class = action_info.get('color_class', 'text-gray-500')
    confirmation_message = action_info.get('confirmation', {}).get('message', '¿Confirmar acción?')
    if action_type == 'close':
        confirmation_messages = action_info.get('confirmation', {})
        if is_owner:
            confirmation_message = confirmation_messages.get('owner_message', '')
        else:
            confirmation_message = confirmation_messages.get('non_owner_message', '')
    return {
        'ticket_id': ticket.id,
        'action_type': action_type,
        'button_text': button_text,
        'color_class': color_class,
        'confirmation_message': confirmation_message,
        'visible': True,
        'comment_label': action_info.get('comment_label', 'Comentario'),
        'comment_placeholder': action_info.get('comment_placeholder', 'Escriba su comentario aquí...'),
        'comment_required': action_info.get('comment_required', False),
    }
