STATUS_MAX_LENGTH = 12
TICKET_STATUS_CHOICES = [
    ('open', 'Abierto'),
    ('feedback', 'Comentado'),
    ('solved', 'Solucionado'),
    ('authorized', 'Autorizado'),
    ('rejected', 'Rechazado'),  
    ('closed', 'Cerrado'),
]

VALID_TICKET_STATUSES = [choice[0] for choice in TICKET_STATUS_CHOICES]
TICKET_STATUS_LABELS = dict(TICKET_STATUS_CHOICES)
TICKET_STATUS_COLORS = {
    'open': '#dc2626',      # rojo (casi naranja)
    'feedback': '#2563eb',  # azul
    'solved': '#16a34a',    # verde
    'authorized': '#22c55e', # verde claro
    'rejected': '#eab308',  # naranja (casi amarillo)
    'closed': '#6b7280'     # gris
}

TICKET_STATUS_TRANSITIONS = {
    'open': ['feedback', 'solved', 'closed'],
    'feedback': ['solved', 'closed'],
    'solved': ['authorized', 'rejected', 'closed'],
    'authorized': ['closed'],
    'rejected': ['feedback', 'solved'],
    'closed': [],  # Estado final
}

ACTIVE_STATUSES = ['open', 'feedback', 'solved', 'rejected']
FINAL_STATUSES = ['authorized', 'closed']

def is_valid_status(status):
    """Valida estados según TICKET_STATUS_CHOICES"""
    return status in VALID_TICKET_STATUSES

def can_transition_to(current_status, new_status):
    """Verifica transiciones válidas según business rules"""
    if not is_valid_status(current_status) or not is_valid_status(new_status):
        return False
    return new_status in TICKET_STATUS_TRANSITIONS.get(current_status, [])

def get_available_transitions(current_status):
    """Estados disponibles desde estado actual"""
    return TICKET_STATUS_TRANSITIONS.get(current_status, []) 