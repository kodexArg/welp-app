from .constants import DESK_STATUSES, DESK_ROLE_PERMISSIONS


def get_available_desk_transitions(current_status):
    """Obtiene las transiciones disponibles para un estado dado"""
    return DESK_STATUSES.get(current_status, {}).get('transitions', [])


def get_permissions_for_role_type(role_type):
    """Obtiene los permisos por defecto para un tipo de rol específico"""
    return DESK_ROLE_PERMISSIONS.get(role_type, {}) 