import os
from django.conf import settings

STATUS_MAX_LENGTH = int(os.environ.get('DESK_STATUS_MAX_LENGTH', '20'))

DESK_STATUSES = {
    'open': {
        'label': os.environ.get('DESK_STATUS_OPEN_LABEL', 'Abierto'),
        'color': os.environ.get('DESK_STATUS_OPEN_COLOR', '#dc2626'),
        'icon': os.environ.get('DESK_STATUS_OPEN_ICON', '🔴'),
        'description': os.environ.get('DESK_STATUS_OPEN_DESC', 'Ticket abierto, esperando asignación'),
        'is_active': os.environ.get('DESK_STATUS_OPEN_ACTIVE', 'true').lower() == 'true',
        'is_final': os.environ.get('DESK_STATUS_OPEN_FINAL', 'false').lower() == 'true',
        'transitions': os.environ.get('DESK_STATUS_OPEN_TRANSITIONS', 'comment,in_progress,solved,closed').split(','),
        'requires_comment': os.environ.get('DESK_STATUS_OPEN_REQUIRES_COMMENT', 'false').lower() == 'true',
    },
    'comment': {
        'label': os.environ.get('DESK_STATUS_COMMENT_LABEL', 'Comentado'),
        'color': os.environ.get('DESK_STATUS_COMMENT_COLOR', '#2563eb'),
        'icon': os.environ.get('DESK_STATUS_COMMENT_ICON', '💬'),
        'description': os.environ.get('DESK_STATUS_COMMENT_DESC', 'Ticket con comentarios del usuario o técnico'),
        'is_active': os.environ.get('DESK_STATUS_COMMENT_ACTIVE', 'true').lower() == 'true',
        'is_final': os.environ.get('DESK_STATUS_COMMENT_FINAL', 'false').lower() == 'true',
        'transitions': os.environ.get('DESK_STATUS_COMMENT_TRANSITIONS', 'in_progress,solved,closed').split(','),
        'requires_comment': os.environ.get('DESK_STATUS_COMMENT_REQUIRES_COMMENT', 'false').lower() == 'true',
    },
    'in_progress': {
        'label': os.environ.get('DESK_STATUS_IN_PROGRESS_LABEL', 'En Progreso'),
        'color': os.environ.get('DESK_STATUS_IN_PROGRESS_COLOR', '#f59e0b'),
        'icon': os.environ.get('DESK_STATUS_IN_PROGRESS_ICON', '🟡'),
        'description': os.environ.get('DESK_STATUS_IN_PROGRESS_DESC', 'Ticket en progreso, siendo trabajado'),
        'is_active': os.environ.get('DESK_STATUS_IN_PROGRESS_ACTIVE', 'true').lower() == 'true',
        'is_final': os.environ.get('DESK_STATUS_IN_PROGRESS_FINAL', 'false').lower() == 'true',
        'transitions': os.environ.get('DESK_STATUS_IN_PROGRESS_TRANSITIONS', 'comment,solved,authorized,closed').split(','),
        'requires_comment': os.environ.get('DESK_STATUS_IN_PROGRESS_REQUIRES_COMMENT', 'true').lower() == 'true',
    },
    'solved': {
        'label': os.environ.get('DESK_STATUS_SOLVED_LABEL', 'Solucionado'),
        'color': os.environ.get('DESK_STATUS_SOLVED_COLOR', '#16a34a'),
        'icon': os.environ.get('DESK_STATUS_SOLVED_ICON', '🟢'),
        'description': os.environ.get('DESK_STATUS_SOLVED_DESC', 'Ticket solucionado, esperando autorización'),
        'is_active': os.environ.get('DESK_STATUS_SOLVED_ACTIVE', 'true').lower() == 'true',
        'is_final': os.environ.get('DESK_STATUS_SOLVED_FINAL', 'false').lower() == 'true',
        'transitions': os.environ.get('DESK_STATUS_SOLVED_TRANSITIONS', 'authorized,rejected,closed').split(','),
        'requires_comment': os.environ.get('DESK_STATUS_SOLVED_REQUIRES_COMMENT', 'true').lower() == 'true',
    },
    'authorized': {
        'label': os.environ.get('DESK_STATUS_AUTHORIZED_LABEL', 'Autorizado'),
        'color': os.environ.get('DESK_STATUS_AUTHORIZED_COLOR', '#8b5cf6'),
        'icon': os.environ.get('DESK_STATUS_AUTHORIZED_ICON', '🟣'),
        'description': os.environ.get('DESK_STATUS_AUTHORIZED_DESC', 'Solución autorizada, ticket cerrado automáticamente'),
        'is_active': os.environ.get('DESK_STATUS_AUTHORIZED_ACTIVE', 'false').lower() == 'true',
        'is_final': os.environ.get('DESK_STATUS_AUTHORIZED_FINAL', 'true').lower() == 'true',
        'transitions': os.environ.get('DESK_STATUS_AUTHORIZED_TRANSITIONS', '').split(',') if os.environ.get('DESK_STATUS_AUTHORIZED_TRANSITIONS') else [],
        'requires_comment': os.environ.get('DESK_STATUS_AUTHORIZED_REQUIRES_COMMENT', 'false').lower() == 'true',
    },
    'rejected': {
        'label': os.environ.get('DESK_STATUS_REJECTED_LABEL', 'Rechazado'),
        'color': os.environ.get('DESK_STATUS_REJECTED_COLOR', '#e11d48'),
        'icon': os.environ.get('DESK_STATUS_REJECTED_ICON', '🔴'),
        'description': os.environ.get('DESK_STATUS_REJECTED_DESC', 'Solución rechazada, requiere revisión'),
        'is_active': os.environ.get('DESK_STATUS_REJECTED_ACTIVE', 'true').lower() == 'true',
        'is_final': os.environ.get('DESK_STATUS_REJECTED_FINAL', 'false').lower() == 'true',
        'transitions': os.environ.get('DESK_STATUS_REJECTED_TRANSITIONS', 'comment,in_progress,closed').split(','),
        'requires_comment': os.environ.get('DESK_STATUS_REJECTED_REQUIRES_COMMENT', 'true').lower() == 'true',
    },
    'closed': {
        'label': os.environ.get('DESK_STATUS_CLOSED_LABEL', 'Cerrado'),
        'color': os.environ.get('DESK_STATUS_CLOSED_COLOR', '#6b7280'),
        'icon': os.environ.get('DESK_STATUS_CLOSED_ICON', '⚫'),
        'description': os.environ.get('DESK_STATUS_CLOSED_DESC', 'Ticket cerrado permanentemente'),
        'is_active': os.environ.get('DESK_STATUS_CLOSED_ACTIVE', 'false').lower() == 'true',
        'is_final': os.environ.get('DESK_STATUS_CLOSED_FINAL', 'true').lower() == 'true',
        'transitions': os.environ.get('DESK_STATUS_CLOSED_TRANSITIONS', '').split(',') if os.environ.get('DESK_STATUS_CLOSED_TRANSITIONS') else [],
        'requires_comment': os.environ.get('DESK_STATUS_CLOSED_REQUIRES_COMMENT', 'false').lower() == 'true',
    },
}

DESK_PERMISSIONS = [
    'can_read',
    'can_comment',
    'can_solve',
    'can_authorize',
    'can_open',
    'can_close',
]

DESK_ROLE_PERMISSIONS = {
    'end_user': {
        'can_read': True,
        'can_comment': False,
        'can_solve': False,
        'can_authorize': False,
        'can_open': True,
        'can_close': False,
        'can_view_others_tickets': False,
    },
    'technician': {
        'can_read': True,
        'can_comment': True,
        'can_solve': True,
        'can_authorize': False,
        'can_open': True,
        'can_close': False,
        'can_view_others_tickets': False,
    },
    'supervisor': {
        'can_read': True,
        'can_comment': True,
        'can_solve': False,
        'can_authorize': True,
        'can_open': True,
        'can_close': True,
        'can_view_others_tickets': True,
    },
    'admin': {
        'can_read': True,
        'can_comment': True,
        'can_solve': True,
        'can_authorize': True,
        'can_open': True,
        'can_close': True,
        'can_view_others_tickets': True,
    },
}

MAX_FILE_SIZE = int(os.environ.get('DESK_MAX_FILE_SIZE', '52428800'))
