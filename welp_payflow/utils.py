from .constants import PAYFLOW_STATUSES, PAYFLOW_ROLE_PERMISSIONS, FA_ICONS
from .models import UDN, Sector, AccountingCategory, Message, Attachment
from django.urls import reverse
from django.db import transaction


def has_user_role(user, role_name):
    if not user or not user.is_authenticated:
        return False
    
    user_roles = {role.role for role in user.payflow_roles.all()}
    return role_name in user_roles


def get_available_payflow_transitions(current_status):
    return PAYFLOW_STATUSES.get(current_status, {}).get('transitions', [])


def get_permissions_for_role_type(role_type):
    return PAYFLOW_ROLE_PERMISSIONS.get(role_type, {})


def _get_user_accessible_ids(user):
    """Obtiene los IDs de UDNs y Sectores a los que un usuario tiene acceso."""
    user_roles = user.payflow_roles.filter(can_open=True)
    udn_ids, sector_ids = set(), set()

    for role in user_roles:
        if role.sector:
            sector_ids.add(role.sector.id)
            udn_ids.update(role.sector.udn.all().values_list('id', flat=True))
        elif role.udn:
            udn_ids.add(role.udn.id)
            sector_ids.update(role.udn.payflow_sectors.values_list('id', flat=True))
            
    return {'udn_ids': udn_ids, 'sector_ids': sector_ids}


def get_user_udns(user):
    """Obtiene las UDNs a las que el usuario tiene acceso."""
    if user.is_superuser:
        return UDN.objects.all()
    accessible_ids = _get_user_accessible_ids(user)
    return UDN.objects.filter(id__in=accessible_ids['udn_ids'])


def get_user_sectors(user, udn=None):
    """Obtiene los Sectores a los que el usuario tiene acceso, opcionalmente filtrados por UDN."""
    if user.is_superuser:
        qs = Sector.objects.all()
        return qs.filter(udn=udn) if udn else qs

    accessible_ids = _get_user_accessible_ids(user)
    qs = Sector.objects.filter(id__in=accessible_ids['sector_ids'])
    return qs.filter(udn=udn) if udn else qs


def get_user_accounting_categories(user, sector=None):
    """Obtiene las Categorías Contables a las que el usuario tiene acceso."""
    if user.is_superuser:
        qs = AccountingCategory.objects.all()
        return qs.filter(sector=sector) if sector else qs

    accessible_sectors = get_user_sectors(user)
    
    if sector:
        accessible_sectors = accessible_sectors.filter(pk=sector.pk)

    return AccountingCategory.objects.filter(sector__in=accessible_sectors)


def can_user_create_ticket_in_context(user, udn, sector):
    """Verifica si el usuario puede crear tickets en el contexto dado."""
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
    """Verifica si el usuario puede cerrar el ticket."""
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
    if not user or not user.is_authenticated:
        return False
    current_status = ticket.status
    possible_transitions = PAYFLOW_STATUSES.get(current_status, {}).get('transitions', [])
    if target_status not in possible_transitions:
        return False

    if user.is_superuser:
        return True

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
    allowed = []
    for target_status in transitions:
        if can_user_transition_ticket(user, ticket, target_status):
            allowed.append(target_status)
    return allowed


def get_ticket_action_data(action, ticket_id=None):
    if action == 'feedback':
        status_info = PAYFLOW_STATUSES.get('comment', {})
    elif action == 'close':
        status_info = PAYFLOW_STATUSES.get('closed', {})
    else:
        status_info = PAYFLOW_STATUSES.get(action, {})
    
    label = status_info.get('action_label', status_info.get('button_text', action.replace('_', ' ').title()))
    fa_icons = FA_ICONS
    
    fa_icon = fa_icons.get(action, 'fa-solid fa-circle')
    href = '#'
    if ticket_id:
        try:
            if action == 'feedback':
                href = reverse('welp_payflow:detail', kwargs={'ticket_id': ticket_id}) + '?response_type=comment'
            else:
                href = reverse('welp_payflow:detail', kwargs={'ticket_id': ticket_id}) + f'?response_type={action}'
        except Exception:
            href = '#'
    return {
        'action': action,
        'href': href,
        'label': label,
        'fa_icon': fa_icon,
    }


def get_ticket_actions_context(user, ticket):
    actions_data = []
    if not user or not user.is_authenticated or not ticket:
        return {'ticket': ticket, 'actions': []}

    all_allowed_actions = get_user_ticket_transitions(user, ticket)

    close_action = None
    comment_action = None
    other_actions = []

    for action in all_allowed_actions:
        action_data = get_ticket_action_data(action, ticket.id)
        if action_data:
            if action == 'close':
                close_action = action_data
            elif action == 'feedback':
                comment_action = action_data
            elif action != 'closed':
                other_actions.append(action_data)

    if ticket.status != 'closed':
        if not comment_action:
            temp_comment_action = get_ticket_action_data('feedback', ticket.id)
            if temp_comment_action:
                comment_action = temp_comment_action

    final_actions = []
    if close_action:
        final_actions.append(close_action)
    
    final_actions.extend(other_actions)

    if comment_action:
        final_actions.append(comment_action)
    
    return {
        'ticket': ticket,
        'actions': final_actions
    } 


def get_ticket_detail_context_data(request, ticket):
    """Prepara el contexto para la vista de detalle del ticket."""
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
    }

    if response_type == 'close':
        context['form_action'] = reverse('welp_payflow:process_close', kwargs={'ticket_id': ticket.id})
    elif response_type == 'comment':
        context['form_action'] = request.get_full_path()
    else:
        context['form_action'] = reverse('welp_payflow:transition', kwargs={'ticket_id': ticket.id, 'target_status': response_type})
    
    context['cancel_url'] = reverse('welp_payflow:detail', kwargs={'ticket_id': ticket.id})

    return context 