from .constants import PAYFLOW_STATUSES, PAYFLOW_ROLE_PERMISSIONS, FA_ICONS


def get_available_payflow_transitions(current_status):
    return PAYFLOW_STATUSES.get(current_status, {}).get('transitions', [])


def get_permissions_for_role_type(role_type):
    return PAYFLOW_ROLE_PERMISSIONS.get(role_type, {})


def get_user_udns(user):
    from .models import UDN
    if user.is_superuser:
        return UDN.objects.all()
    user_roles = user.payflow_roles.filter(
        can_open=True
    )
    udn_ids = set()
    for role in user_roles:
        if role.udn:
            udn_ids.add(role.udn.id)
        elif role.sector:
            udn_ids.update(role.sector.udn.values_list('id', flat=True))
    return UDN.objects.filter(id__in=udn_ids)


def get_user_sectors(user, udn=None):
    from .models import Sector
    if user.is_superuser:
        if udn:
            return Sector.objects.filter(udn=udn)
        return Sector.objects.all()
    user_roles = user.payflow_roles.filter(
        can_open=True
    )
    sector_ids = set()
    for role in user_roles:
        if udn:
            if role.udn and role.udn == udn:
                if role.sector:
                    sector_ids.add(role.sector.id)
                else:
                    sector_ids.update(udn.payflow_sectors.values_list('id', flat=True))
            elif role.sector and role.sector.udn.filter(id=udn.id).exists():
                sector_ids.add(role.sector.id)
        else:
            if role.sector:
                sector_ids.add(role.sector.id)
            elif role.udn:
                sector_ids.update(role.udn.payflow_sectors.values_list('id', flat=True))
    return Sector.objects.filter(id__in=sector_ids)


def get_user_accounting_categories(user, sector=None):
    from .models import AccountingCategory
    if user.is_superuser:
        if sector:
            return AccountingCategory.objects.filter(sector=sector)
        return AccountingCategory.objects.all()
    if sector:
        return AccountingCategory.objects.filter(sector=sector)
    return AccountingCategory.objects.all()


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

    user_roles = {role.get_role_type() for role in user.payflow_roles.all()}

    owner_roles_queryset = getattr(ticket_owner, 'payflow_roles', None)
    owner_roles = {role.get_role_type() for role in owner_roles_queryset.all()} if owner_roles_queryset else set()

    if 'supervisor' in user_roles and 'end_user' in owner_roles:
        return True

    if 'manager' in user_roles and owner_roles & {'end_user', 'technician', 'supervisor'}:
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

    user_role_types = {role.get_role_type() for role in user.payflow_roles.all()}

    if user_role_types.intersection(allowed_roles):
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
    else:
        status_info = PAYFLOW_STATUSES.get(action, {})
    
    ui_info = status_info.get('ui', {})
    fa_icons = FA_ICONS
    if action == 'closed':
        return None
    label = ui_info.get('button_text', status_info.get('label', action.upper()))
    fa_icon = fa_icons.get(action, 'fa-solid fa-circle')
    href = '#'
    if ticket_id:
        from django.urls import reverse
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
        'label': label,
        'fa_icon': fa_icon,
    }


def get_ticket_actions_context(user, ticket):
    actions_data = []
    if not user or not user.is_authenticated or not ticket:
        return {'ticket': ticket, 'actions': []}

    # Obtener todas las transiciones permitidas
    all_allowed_actions = get_user_ticket_transitions(user, ticket)

    # Preparar las acciones por separado
    close_action = None
    comment_action = None
    other_actions = []

    # Generar data para cada acción y clasificarlas
    for action in all_allowed_actions:
        action_data = get_ticket_action_data(action, ticket.id)
        if action_data:
            if action == 'close':
                close_action = action_data
            elif action == 'feedback': # 'feedback' es el tipo de acción para comentar
                comment_action = action_data
            elif action != 'closed': # 'closed' no es una acción, es un estado final
                other_actions.append(action_data)

    # Añadir el botón de comentar si es posible y no está en la lista
    # Cualquier usuario autenticado puede comentar si el ticket no está cerrado
    if ticket.status != 'closed':
        if not comment_action:
            # Asegurarse de que el botón de comentar se genere correctamente
            temp_comment_action = get_ticket_action_data('feedback', ticket.id)
            if temp_comment_action:
                comment_action = temp_comment_action

    # Construir la lista final de acciones en el orden deseado
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