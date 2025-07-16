from django import template
from django.urls import reverse
from django.utils.html import format_html
from welp_payflow.constants import FA_ICONS, PAYFLOW_STATUSES
from welp_payflow.utils import get_ticket_actions_context
from welp_desk.constants import DESK_STATUSES

register = template.Library()

@register.inclusion_tag('welp_payflow/components/ticket_message.html')
def ticket_message(message):
    return {'message': message, 'ticket_id': message.ticket.id}

@register.inclusion_tag('welp_payflow/components/_ticket_message_user_line.html')
def ticket_message_user_line(message):
    """
    Prepara el contexto para la línea de usuario de un mensaje de ticket,
    incluyendo el verbo de la acción y los iconos correspondientes.
    """
    user_name = "Usuario eliminado"
    if message.user:
        user_name = message.user.get_full_name() or message.user.username

    action_key = message.status
    
    # Valores por defecto
    verb = None
    action_icon_class = None

    if action_key == 'feedback':
        verb = "Comentario de"
        action_icon_class = FA_ICONS.get('feedback')
    else:
        action_info = PAYFLOW_STATUSES.get(action_key, {})
        action_verb = action_info.get('action_verb')
        
        if action_verb and action_verb != 'Comentado':
            verb = f"{action_verb} por"
            action_icon_class = FA_ICONS.get(action_key)

    return {
        'user_name': user_name,
        'verb': verb,
        'action_icon_class': action_icon_class,
    }


@register.inclusion_tag('welp_payflow/components/ticket_message_input.html', takes_context=True)
def ticket_message_input(context, ticket, response_type, user_can_transition=True, is_owner=False, comment_value='', cancel_url=None, cancel_text="Cancelar", hidden_fields=None):
    request = context['request']
    ui_key = response_type
    if ui_key == 'close':
        ui_key = 'closed'
    elif ui_key == 'feedback':
        ui_key = 'comment'
    action_info = PAYFLOW_STATUSES.get(ui_key, {})
    if not action_info:
        return {'visible': False}
    button_text = action_info.get('button_text', response_type.replace('_', ' ').title())
    field_required = action_info.get('comment_required', False)
    confirmation_message = action_info.get('confirmation_message', '')
    if response_type == 'close':
        if is_owner or request.user.is_superuser:
            field_required = False
    form_action = ''
    if response_type == 'close':
        form_action = reverse('welp_payflow:process_close', kwargs={'ticket_id': ticket.id})
    elif response_type == 'comment':
        form_action = request.get_full_path()
    else:
        form_action = reverse('welp_payflow:transition', kwargs={'ticket_id': ticket.id, 'target_status': response_type})
    icon_class = FA_ICONS.get(response_type, 'fa-solid fa-paper-plane')
    final_cancel_url = cancel_url or reverse('welp_payflow:detail', kwargs={'ticket_id': ticket.id})
    show_estimated_amount_input = (response_type == 'budgeted')
    form_fields = []
    if action_info.get('show_comment_box', True):
        comment_field_name = 'response_body'
        if response_type == 'close':
            comment_field_name = 'close_comment'
        elif response_type != 'comment':
            comment_field_name = f'{response_type}_comment'
        form_fields.append({
            'id': f'field_{comment_field_name}',
            'name': comment_field_name,
            'label': action_info.get('comment_label', 'Comentario'),
            'placeholder': action_info.get('comment_placeholder', 'Escriba su comentario aquí...'),
            'required': field_required,
            'field_type': 'textarea'
        })
    if action_info.get('show_attachments', False):
        form_fields.append({
            'id': 'field_attachments',
            'name': 'attachments',
            'label': 'Archivos Adjuntos',
            'placeholder': 'Seleccionar archivos...',
            'required': False,
            'field_type': 'file'
        })
    return {
        'ticket': ticket,
        'response_type': response_type,
        'response_info': action_info,
        'button_text': button_text,
        'field_required': field_required,
        'confirmation_message': confirmation_message,
        'form_action': form_action,
        'is_owner': is_owner,
        'comment_value': comment_value,
        'cancel_url': final_cancel_url,
        'cancel_text': cancel_text,
        'hidden_fields': hidden_fields if hidden_fields is not None else {},
        'visible': True,
        'icon_class': icon_class,
        'show_estimated_amount_input': show_estimated_amount_input,
        'form_fields': form_fields,
    }

@register.inclusion_tag('welp_payflow/components/ticket_actions.html', takes_context=True)
def ticket_actions(context, ticket):
    user = context.get('request').user
    return get_ticket_actions_context(user, ticket)

@register.inclusion_tag('welp_payflow/components/ticket_container.html', takes_context=True)
def ticket_container(context, ticket, expanded=False, hide_buttons=False):
    return {
        'ticket': ticket,
        'expanded': expanded,
        'hide_buttons': hide_buttons,
        'request': context.get('request'),
    }

@register.inclusion_tag('welp_payflow/components/ticket_empty.html')
def ticket_empty():
    return {}

@register.inclusion_tag('welp_payflow/components/ticket_status.html')
def ticket_status(ticket):
    status = ticket.status or 'open'
    status_info = PAYFLOW_STATUSES.get(status, {})
    return {
        'icon': status_info.get('icon', ''),
        'label': status_info.get('label', status.upper()),
        'color': status_info.get('color', '#6b7280'),
    }

@register.filter
def ticket_status_flow(ticket):
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
def ticket_status_label(status, system='payflow'):
    if system == 'payflow':
        return PAYFLOW_STATUSES.get(status, {}).get('label', status.title())
    return DESK_STATUSES.get(status, {}).get('label', status.title())

@register.filter
def ticket_action_info(ticket):
    status = ticket.status or 'open'
    status_info = PAYFLOW_STATUSES.get(status, {})
    flow_info = status_info.get('flow', {})
    return {
        'current_action': flow_info.get('current_action', ''),
        'next_action': flow_info.get('next_action', ''),
        'responsible_roles': flow_info.get('responsible_roles', []),
    }

@register.filter
def ticket_comment_count(ticket):
    count = 0
    for message in ticket.messages.order_by('created_on'):
        if message.status != 'feedback':
            break
        count += 1
    if count > 0:
        return format_html('<span class="ml-2 align-middle text-xs text-sky-400"><i class="fa fa-comments"></i><sub>{}</sub></span>', count)
    return format_html('')

@register.inclusion_tag('welp_payflow/components/ticket_summary_info.html')
def ticket_summary_info(ticket):
    feedback_count = ticket.messages.filter(status='feedback').count()
    has_estimated_amount = ticket.estimated_amount and ticket.estimated_amount > 0
    return {
        'ticket': ticket,
        'feedback_count': feedback_count,
        'has_estimated_amount': has_estimated_amount,
    } 