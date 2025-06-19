# welp_desk/constants.py

# Configuración del campo de estado
STATUS_MAX_LENGTH = 12  # Suficiente para 'authorized' (10 chars) + margen

# Estados de tickets en orden de flujo de trabajo lógico
TICKET_STATUS_CHOICES = [
    ('open', 'Abierto'),
    ('feedback', 'Comentado'),
    ('solved', 'Solucionado'),
    ('authorized', 'Autorizado'),
    ('rejected', 'Rechazado'),  
    ('closed', 'Cerrado'),
]

# Extraer solo las keys para validación
VALID_TICKET_STATUSES = [choice[0] for choice in TICKET_STATUS_CHOICES]

# Mapeo directo desde choices (elimina redundancia)
TICKET_STATUS_LABELS = dict(TICKET_STATUS_CHOICES)

# Colores hex para admin panel
TICKET_STATUS_COLORS = {
    'open': '#dc2626',      # rojo (casi naranja)
    'feedback': '#2563eb',  # azul
    'solved': '#16a34a',    # verde
    'authorized': '#22c55e', # verde claro
    'rejected': '#eab308',  # naranja (casi amarillo)
    'closed': '#6b7280'     # gris
}

# Transiciones válidas de estado (flujo de trabajo)
TICKET_STATUS_TRANSITIONS = {
    'open': ['feedback', 'solved', 'closed'],
    'feedback': ['solved', 'closed'],
    'solved': ['authorized', 'rejected', 'closed'],
    'authorized': ['closed'],
    'rejected': ['feedback', 'solved'],
    'closed': [],  # Estado final
}

# Estados que permiten continuar trabajando
ACTIVE_STATUSES = ['open', 'feedback', 'solved', 'rejected']
FINAL_STATUSES = ['authorized', 'closed']

def is_valid_status(status):
    """Valida si un estado es válido"""
    return status in VALID_TICKET_STATUSES

def can_transition_to(current_status, new_status):
    """Verifica si es posible transicionar de un estado a otro"""
    if not is_valid_status(current_status) or not is_valid_status(new_status):
        return False
    return new_status in TICKET_STATUS_TRANSITIONS.get(current_status, [])

def get_available_transitions(current_status):
    """Obtiene los estados disponibles desde el estado actual"""
    return TICKET_STATUS_TRANSITIONS.get(current_status, []) 