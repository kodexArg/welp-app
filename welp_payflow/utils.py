from .constants import PAYFLOW_STATUSES, PAYFLOW_ROLE_PERMISSIONS, PAYFLOW_STATUS_FLOW


def get_available_payflow_transitions(current_status):
    return PAYFLOW_STATUSES.get(current_status, {}).get('transitions', [])


def get_permissions_for_role_type(role_type):
    return PAYFLOW_ROLE_PERMISSIONS.get(role_type, {})


def get_user_udns(user):
    from .models import UDN
    
    if user.is_superuser:
        return UDN.objects.all()
    
    user_roles = user.payflow_roles.filter(can_open=True)
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
    
    user_roles = user.payflow_roles.filter(can_open=True)
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
    
    user_roles = user.payflow_roles.filter(can_open=True)
    
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
    if user.is_superuser:
        return True
    if not user.is_authenticated:
        return False
    user_roles = user.payflow_roles.all()
    ticket_owner = ticket.created_by
    if user == ticket_owner:
        return True
    for role in user_roles:
        role_type = role.get_role_type()
        if role_type == 'manager':
            return True
        if role_type == 'supervisor':
            if hasattr(ticket_owner, 'payflow_roles'):
                for owner_role in ticket_owner.payflow_roles.all():
                    if owner_role.get_role_type() in ['end_user', 'technician']:
                        return True
    return False


def can_user_transition_ticket(user, ticket, target_status):
    if not user or not user.is_authenticated:
        return False
    current_status = ticket.status
    possible_transitions = PAYFLOW_STATUSES.get(current_status, {}).get('transitions', [])
    if target_status not in possible_transitions:
        return False
    allowed_roles = PAYFLOW_STATUSES.get(target_status, {}).get('allowed_roles', [])
    if user.is_superuser:
        return True
    if not allowed_roles:
        return False
    user_roles = getattr(user, 'payflow_roles', None)
    if user_roles is None:
        return False
    for role in user.payflow_roles.all():
        if role.get_role_type() in allowed_roles:
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