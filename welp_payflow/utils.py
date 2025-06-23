from .constants import PAYFLOW_STATUSES, PAYFLOW_ROLE_PERMISSIONS


def get_available_payflow_transitions(current_status):
    """Obtiene las transiciones disponibles para un estado dado"""
    return PAYFLOW_STATUSES.get(current_status, {}).get('transitions', [])


def get_permissions_for_role_type(role_type):
    """Obtiene los permisos por defecto para un tipo de rol específico"""
    return PAYFLOW_ROLE_PERMISSIONS.get(role_type, {}) 