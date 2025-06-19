# welp_desk/constants.py

# Estados de tickets en orden de flujo de trabajo lógico
TICKET_STATUS_CHOICES = [
    ('open', 'Abierto'),
    ('feedback', 'Comentado'),
    ('solved', 'Solucionado'),
    ('authorized', 'Autorizado'),
    ('rejected', 'Rechazado'),  
    ('closed', 'Cerrado'),
]

# Mapeo para etiquetas en template tags
TICKET_STATUS_LABELS = {
    'open': 'Abierto',
    'feedback': 'Comentado',
    'solved': 'Solucionado',
    'authorized': 'Autorizado',
    'rejected': 'Rechazado',
    'closed': 'Cerrado',
}

# Colores hex para admin panel
TICKET_STATUS_COLORS = {
    'open': '#dc2626',      # rojo (casi naranja)
    'feedback': '#2563eb',  # azul
    'solved': '#16a34a',    # verde
    'authorized': '#22c55e', # verde claro
    'rejected': '#eab308',  # naranja (casi amarillo)
    'closed': '#6b7280'     # gris
} 