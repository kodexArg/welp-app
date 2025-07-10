from .constants import PAYFLOW_STATUSES, PAYFLOW_ROLE_PERMISSIONS


def get_available_payflow_transitions(current_status):
    """Obtiene las transiciones disponibles para un estado dado"""
    return PAYFLOW_STATUSES.get(current_status, {}).get('transitions', [])


def get_permissions_for_role_type(role_type):
    """Obtiene los permisos por defecto para un tipo de rol específico"""
    return PAYFLOW_ROLE_PERMISSIONS.get(role_type, {})


def can_user_close_ticket(user, ticket):
    """
    Determina si el usuario puede cerrar el ticket según la política de roles:
    - end_user, technician, purchase_manager: solo si es su propio ticket
    - supervisor: sus propios tickets y los de end_user o technician
    - manager: cualquier ticket
    - superuser: cualquier ticket
    """
    if user.is_superuser:
        return True
    if not user.is_authenticated:
        return False
    user_roles = user.payflow_roles.all()
    ticket_owner = ticket.created_by
    if user == ticket_owner:
        return True
    # Si no es el dueño, revisar roles
    for role in user_roles:
        role_type = role.get_role_type()
        if role_type == 'manager':
            return True
        if role_type == 'supervisor':
            # Puede cerrar tickets de end_user o technician
            if hasattr(ticket_owner, 'payflow_roles'):
                for owner_role in ticket_owner.payflow_roles.all():
                    if owner_role.get_role_type() in ['end_user', 'technician']:
                        return True
    return False 