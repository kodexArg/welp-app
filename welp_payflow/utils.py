"""
Utilidades y funciones de apoyo para la aplicación Payflow.
"""
from .constants import PAYFLOW_STATUSES, PAYFLOW_ROLE_PERMISSIONS, FA_ICONS
from .models import UDN, Sector, AccountingCategory, Message, Attachment
from django.urls import reverse
from django.db import transaction


def has_user_role(user, role_name):
    if not user or not user.is_authenticated:
        return False
    
    user_roles = {role.role for role in user.payflow_roles.all()}
    return role_name in user_roles

def can_user_edit_amount(user):
    return has_user_role(user, 'technician') or has_user_role(user, 'purchase_manager')


def get_available_payflow_transitions(current_status):
    return PAYFLOW_STATUSES.get(current_status, {}).get('transitions', [])


def get_permissions_for_role_type(role_type):
    return PAYFLOW_ROLE_PERMISSIONS.get(role_type, {})


def _get_user_accessible_ids(user):
    if user.is_superuser:
        return {
            'udn_ids': set(UDN.objects.values_list('id', flat=True)),
            'sector_ids': set(Sector.objects.values_list('id', flat=True))
        }

    user_roles = user.payflow_roles.filter(can_open=True).select_related('udn', 'sector')
    udn_ids, sector_ids = set(), set()

    for role in user_roles:
        if role.udn and not role.sector:
            udn_ids.add(role.udn.id)
            sector_ids.update(role.udn.payflow_sectors.values_list('id', flat=True))
        
        elif role.udn and role.sector:
            if role.sector.udn.filter(pk=role.udn.id).exists():
                udn_ids.add(role.udn.id)
                sector_ids.add(role.sector.id)
            
    return {'udn_ids': udn_ids, 'sector_ids': sector_ids}


def get_user_udns(user):
    accessible_ids = _get_user_accessible_ids(user)
    queryset = UDN.objects.filter(id__in=accessible_ids['udn_ids'])
    return queryset


def get_user_sectors(user, udn=None):
    accessible_ids = _get_user_accessible_ids(user)
    queryset = Sector.objects.filter(id__in=accessible_ids['sector_ids'])
    
    if udn:
        queryset = queryset.filter(udn=udn)
        
    return queryset


def get_user_accounting_categories(user, sector=None):
    if user.is_superuser:
        queryset = AccountingCategory.objects.all()
        if sector:
            queryset = queryset.filter(sector=sector)
        return queryset

    accessible_sectors = get_user_sectors(user)
    
    if sector:
        accessible_sectors = accessible_sectors.filter(pk=sector.pk)

    queryset = AccountingCategory.objects.filter(sector__in=accessible_sectors)
    return queryset


def can_user_create_ticket_in_context(user, udn, sector):
    if user.is_superuser:
        return True
    user_roles = user.payflow_roles.filter(
        can_open=True
    )
    for role in user_roles:
        if role.udn and role.udn != udn:
            continue
        if role.sector and role.sector != sector:
            continue
        if not role.sector and role.udn:
            if not sector.udn.filter(id=role.udn.id).exists():
                continue
        return True
    return False


def can_user_close_ticket(user, ticket):
    if not getattr(user, 'is_authenticated', False):
        return False
    ticket_owner = ticket.created_by
    if user == ticket_owner:
        return True

    owner_roles_queryset = getattr(ticket_owner, 'payflow_roles', None)
    owner_roles = {role.role for role in owner_roles_queryset.all()} if owner_roles_queryset else set()

    if has_user_role(user, 'supervisor') and 'end_user' in owner_roles:
        return True

    if has_user_role(user, 'manager') and owner_roles & {'end_user', 'technician', 'supervisor'}:
        return True

    return False


def can_user_transition_ticket(user, ticket, target_status):
    if user.is_superuser:
        return True
    if not user or not user.is_authenticated:
        return False
    current_status = ticket.status
    possible_transitions = PAYFLOW_STATUSES.get(current_status, {}).get('transitions', [])
    if target_status not in possible_transitions:
        return False

    if target_status == 'closed':
        return can_user_close_ticket(user, ticket)

    allowed_roles = PAYFLOW_STATUSES.get(target_status, {}).get('allowed_roles', [])

    if not allowed_roles:
        return False

    for role_name in allowed_roles:
        if has_user_role(user, role_name):
            return True

    return False


def get_user_ticket_transitions(user, ticket):
    current_status = ticket.status
    transitions = PAYFLOW_STATUSES.get(current_status, {}).get('transitions', [])
    
    if user.is_superuser:
        return transitions

    allowed = []
    for target_status in transitions:
        if can_user_transition_ticket(user, ticket, target_status):
            allowed.append(target_status)
    return allowed


def should_hide_ticket_from_attention(user, ticket):
    """
    Determina si un ticket debe estar oculto de la lista de 'requiere atención'
    basándose en los roles del usuario y la configuración 'hidden_from_attention'
    del estado actual del ticket.
    
    Args:
        user: Usuario actual
        ticket: Ticket a evaluar
        
    Returns:
        bool: True si el ticket debe estar oculto, False si debe mostrarse
    """
    if not user or not user.is_authenticated:
        return False
        
    # Los superusuarios ven todos los tickets
    if user.is_superuser:
        return False
    
    current_status = ticket.status
    hidden_roles = PAYFLOW_STATUSES.get(current_status, {}).get('hidden_from_attention', [])
    
    # Si no hay roles configurados para ocultar, mostrar el ticket
    if not hidden_roles:
        return False
    
    # Verificar si el usuario tiene alguno de los roles que deben ocultar este estado
    for role_name in hidden_roles:
        if has_user_role(user, role_name):
            return True
    
    return False


def get_ticket_action_data(action, ticket_id=None):
    if action == 'feedback':
        status_key = 'comment'
    elif action == 'close':
        status_key = 'closed'
    elif action == 'view':
        status_key = 'view'
    else:
        status_key = action
        
    status_info = PAYFLOW_STATUSES.get(status_key, {})

    label = status_info.get('action_label', status_info.get('button_text', action.replace('_', ' ').title()))
    fa_icon = FA_ICONS.get(action, 'fa-solid fa-circle')
    
    primary_color = 'text-forest-700'

    if action == 'close':
        earth_color = status_info.get('color_class', 'text-earth-700')
        icon_color = earth_color
        text_color = earth_color
    elif action == 'view':
        gray_color = status_info.get('color_class', 'text-gray-600')
        icon_color = gray_color
        text_color = gray_color
    else:
        icon_color = primary_color
        text_color = primary_color
    
    href = '#'
    if ticket_id:
        try:
            if action == 'feedback':
                response_type = 'comment'
            elif action == 'view':
                response_type = 'view'
            else:
                response_type = action
            base_url = reverse('welp_payflow:detail', kwargs={'ticket_id': ticket_id})
            href = f"{base_url}?response_type={response_type}"
        except Exception:
            href = '#'
            
    return {
        'action': action,
        'href': href,
        'label': label,
        'fa_icon': fa_icon,
        'icon_color': icon_color,
        'text_color': text_color,
    }


def get_ticket_actions_context(user, ticket):
    if not user or not user.is_authenticated or not ticket:
        return {'ticket': ticket, 'actions': []}

    all_allowed_actions = get_user_ticket_transitions(user, ticket)
    
    close_action = None
    if can_user_close_ticket(user, ticket):
        close_action = get_ticket_action_data('close', ticket.id)

    comment_action = None
    other_actions = []

    for action in all_allowed_actions:
        action_data = get_ticket_action_data(action, ticket.id)
        if action_data:
            if action == 'close':
                if not close_action:
                    close_action = action_data
            elif action == 'feedback':
                comment_action = action_data
            elif action != 'closed':
                other_actions.append(action_data)

    if ticket.status != 'closed':
        if not comment_action and 'feedback' in PAYFLOW_STATUSES:
            comment_action = get_ticket_action_data('feedback', ticket.id)

    final_actions = []
    if close_action:
        final_actions.append(close_action)
    
    final_actions.extend(other_actions)

    if comment_action:
        final_actions.append(comment_action)
    
    # Agregar acción 'ver' al final
    view_action = get_ticket_action_data('view', ticket.id)
    if view_action:
        final_actions.append(view_action)
    
    return {
        'ticket': ticket,
        'actions': final_actions
    }


def get_ticket_detail_context_data(request, ticket):
    response_type = request.GET.get('response_type', 'comment')
    ui_key = response_type
    if ui_key == 'close':
        ui_key = 'closed'
    elif ui_key == 'feedback':
        ui_key = 'comment'

    status_info = PAYFLOW_STATUSES.get(ui_key, {})

    show_attachments = status_info.get('show_attachments', False)
    show_comment_box = status_info.get('show_comment_box', True)
    field_required = status_info.get('comment_required', False)

    is_owner = (ticket.created_by == request.user) if ticket.created_by else False
    if response_type == 'close':
        if is_owner or request.user.is_superuser:
            field_required = False
        else:
            field_required = True

    comment_field_name = 'response_body'
    if response_type == 'close':
        comment_field_name = 'close_comment'
    elif response_type != 'comment':
        comment_field_name = f'{response_type}_comment'

    confirmation_info = None
    if response_type == 'close':
        confirmation_style = status_info.get('confirmation_style', {})
        if is_owner:
            owner_message = status_info.get('owner_message', 'Está cerrando su propio ticket.')
            non_owner_message = None
        else:
            owner_message = None
            if ticket.created_by:
                owner_name = ticket.created_by.get_full_name() or ticket.created_by.username
                non_owner_message = status_info.get('non_owner_message', '').format(
                    owner_name=owner_name,
                    owner_username=ticket.created_by.username
                )
            else:
                non_owner_message = status_info.get('non_owner_message', 'Está cerrando un ticket creado por otro usuario.').format(
                    owner_name='un usuario desconocido',
                    owner_username='N/A'
                )
        
        confirmation_info = {
            'style': confirmation_style,
            'owner_message': owner_message,
            'non_owner_message': non_owner_message
        }

    context = {
        'ticket': ticket,
        'response_type': response_type,
        'response_info': status_info,
        'confirmation_message': status_info.get('confirmation_message', ''),
        'button_text': status_info.get('button_text', 'Enviar'),
        'comment_placeholder': status_info.get('comment_placeholder', 'Escriba su comentario aquí...'),
        'comment_label': status_info.get('comment_label', 'Comentario'),
        'field_required': field_required,
        'show_attachments': show_attachments,
        'show_comment_box': show_comment_box,
        'is_owner': is_owner if response_type == 'close' else False,
        'hidden_fields': {},
        'icon_class': FA_ICONS.get(response_type, 'fa-solid fa-paper-plane'),
        'comment_field_name': comment_field_name,
        'confirmation_info': confirmation_info,
    }

    if response_type == 'close':
        context['form_action'] = reverse('welp_payflow:process_close', kwargs={'ticket_id': ticket.id})
    elif response_type == 'comment':
        context['form_action'] = request.get_full_path()
    else:
        context['form_action'] = reverse('welp_payflow:transition', kwargs={'ticket_id': ticket.id, 'target_status': response_type})
    
    context['cancel_url'] = reverse('welp_payflow:detail', kwargs={'ticket_id': ticket.id})

    return context