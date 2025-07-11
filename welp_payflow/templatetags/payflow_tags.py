from django import template
from django.urls import reverse
from django.utils.html import format_html
from welp_desk.constants import DESK_STATUSES
from welp_payflow.constants import PAYFLOW_STATUSES, FA_ICONS
from welp_payflow.utils import get_ticket_actions_context

register = template.Library()

@register.inclusion_tag('components/payflow/radio-button.html')
def radio_button(target, id, label, next_target, visible=True):
    """Componente radio-button HTMX usado en Welp Payflow."""
    try:
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

@register.inclusion_tag('components/payflow/status-badge.html')
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

@register.inclusion_tag('components/payflow/ticket_message.html')
def ticket_message(message):
    return {'message': message}

@register.inclusion_tag('components/payflow/ticket_actions.html', takes_context=True)
def ticket_actions(context, ticket):
    user = context.get('request').user
    return get_ticket_actions_context(user, ticket)

@register.inclusion_tag('components/payflow/pagination.html')
def pagination(page_obj, request):
    return {'page_obj': page_obj, 'request': request}

@register.inclusion_tag('components/payflow/ticket_container.html', takes_context=True)
def ticket_container(context, ticket, expanded=False, hide_buttons=False):
    return {
        'ticket': ticket,
        'expanded': expanded,
        'hide_buttons': hide_buttons,
        'request': context.get('request'),
    }

@register.inclusion_tag('components/payflow/ticket_empty.html')
def ticket_empty():
    return {}

@register.filter
def get_status_flow(ticket):
    status = ticket.status or 'open'
    status_data = PAYFLOW_STATUSES.get(status, {})
    flow_info = status_data.get('flow', {})
    return {
        'status': status,
        'label': status_data.get('label', 'Desconocido'),
        'description': status_data.get('description', 'Estado desconocido'),
        'current_action': flow_info.get('current_action'),
        'next_action': flow_info.get('next_action'),
        'responsible_roles': flow_info.get('responsible_roles', []),
        'priority': flow_info.get('priority'),
        'color_name': status_data.get('color_name', 'gray'),
        'icon': status_data.get('icon', '❓'),
        'is_final': status_data.get('is_final', False),
        'is_waiting': flow_info.get('is_waiting', False),
    }

@register.filter
def get_status_label(status, system='payflow'):
    if system == 'payflow':
        return PAYFLOW_STATUSES.get(status, {}).get('label', status.title())
    return DESK_STATUSES.get(status, {}).get('label', status.title())

@register.inclusion_tag('components/payflow/ticket_status.html')
def ticket_status(ticket):
    status = ticket.status or 'open'
    status_info = PAYFLOW_STATUSES.get(status, {})
    return {
        'icon': status_info.get('icon', ''),
        'label': status_info.get('label', status.upper()),
        'color': status_info.get('color', '#6b7280'),
    }

@register.filter
def get_ticket_action_info(ticket):
    status = ticket.status or 'open'
    status_info = PAYFLOW_STATUSES.get(status, {})
    flow_info = status_info.get('flow', {})
    return {
        'current_action': flow_info.get('current_action', ''),
        'next_action': flow_info.get('next_action', ''),
        'responsible_roles': flow_info.get('responsible_roles', []),
    }

@register.filter
def get_ticket_comment_count(ticket):
    count = 0
    for message in ticket.messages.order_by('created_on'):
        if message.status != 'feedback':
            break
        count += 1
    if count > 0:
        return format_html('<span class="ml-2 align-middle text-xs text-sky-400"><i class="fa fa-comments"></i><sub>{}</sub></span>', count)
    return format_html('')

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''

@register.inclusion_tag('components/payflow/status-flow.html')
def payflow_status_flow(status, user_role=None, ticket_id=None, is_owner=False, ticket=None):
    status_data = PAYFLOW_STATUSES.get(status, {})
    flow_info = status_data.get('flow', {})
    if not flow_info and status == 'comment':
        return {}
    current_transitions = []
    if ticket and user_role:
        pass
    return {
        'status': status,
        'label': status_data.get('label', 'Desconocido'),
        'description': status_data.get('description', 'Estado desconocido'),
        'current_action': flow_info.get('current_action'),
        'next_action': flow_info.get('next_action'),
        'responsible_roles': flow_info.get('responsible_roles', []),
        'priority': flow_info.get('priority'),
        'color_name': status_data.get('color_name', 'gray'),
        'icon': status_data.get('icon', '❓'),
        'is_final': status_data.get('is_final', False),
        'is_waiting': flow_info.get('is_waiting', False),
        'current_transitions': current_transitions,
        'ticket_id': ticket_id,
        'is_owner': is_owner,
    }

@register.inclusion_tag('components/payflow/action-button.html')
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

@register.inclusion_tag('components/payflow/ticket_message_input.html')
def payflow_response_form(ticket, response_type, user_can_transition=True, is_owner=False, comment_value='', cancel_url=None, cancel_text="Cancelar", hidden_fields=None):
    action_info = PAYFLOW_STATUSES.get(response_type, {}).get('ui', {})
    if not action_info and response_type != 'comment':
        action_info = PAYFLOW_STATUSES.get('comment', {}).get('ui', {})
        if response_type == 'comment':
            user_can_transition = True
    if not action_info or not user_can_transition:
        return {'visible': False}
    
    button_text = action_info.get('button_text', response_type.replace('_', ' ').title())
    label_text = action_info.get('comment_label', 'Comentario')
    placeholder = action_info.get('comment_placeholder', 'Escriba su comentario aquí...')
    required = action_info.get('comment_required', False)
    show_attachments = action_info.get('show_attachments', False)
    show_comment_box = action_info.get('show_comment_box', False)
    label_color = action_info.get('color_class', 'text-gray-500')
    confirmation_message = action_info.get('confirmation', {}).get('message')

    if response_type == 'close':
        if is_owner:
            required = False
        else:
            required = True
        close_confirmation = action_info.get('confirmation', {})
        owner_message = close_confirmation.get('owner_message', '')
        non_owner_message = close_confirmation.get('non_owner_message', '')
        confirmation_style = close_confirmation.get('style', {})
    else:
        owner_message = ''
        non_owner_message = ''
        confirmation_style = {}

    field_name = f"{response_type}_comment"
    form_action = reverse('welp_payflow:transition', kwargs={'ticket_id': ticket.id, 'target_status': response_type})
    icon_class = FA_ICONS.get(response_type, '')

    return {
        'ticket': ticket,
        'response_type': response_type,
        'button_text': button_text,
        'label_text': label_text,
        'placeholder': placeholder,
        'required': required,
        'show_attachments': show_attachments,
        'show_comment_box': show_comment_box,
        'confirmation_message': confirmation_message,
        'field_name': field_name,
        'form_action': form_action,
        'is_owner': is_owner,
        'owner_message': owner_message,
        'non_owner_message': non_owner_message,
        'confirmation_style': confirmation_style,
        'comment_value': comment_value,
        'cancel_url': reverse('welp_payflow:list'),
        'cancel_text': cancel_text,
        'hidden_fields': hidden_fields if hidden_fields is not None else {},
        'visible': True,
        'label_color': label_color,
        'icon_class': icon_class,
    }
