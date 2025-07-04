import os
from django.conf import settings

STATUS_MAX_LENGTH = int(os.environ.get('PAYFLOW_STATUS_MAX_LENGTH', '20'))

PAYFLOW_STATUSES = {
    'open': {
        'label': os.environ.get('PAYFLOW_STATUS_OPEN_LABEL', 'Abierto'),
        'color': os.environ.get('PAYFLOW_STATUS_OPEN_COLOR', '#dc2626'),
        'icon': os.environ.get('PAYFLOW_STATUS_OPEN_ICON', '🔴'),
        'description': os.environ.get('PAYFLOW_STATUS_OPEN_DESC', 'Solicitud creada, esperando autorización inicial'),
        'is_active': os.environ.get('PAYFLOW_STATUS_OPEN_ACTIVE', 'true').lower() == 'true',
        'is_final': os.environ.get('PAYFLOW_STATUS_OPEN_FINAL', 'false').lower() == 'true',
        'transitions': os.environ.get('PAYFLOW_STATUS_OPEN_TRANSITIONS', 'authorized,closed').split(','),
    },
    'authorized': {
        'label': os.environ.get('PAYFLOW_STATUS_AUTHORIZED_LABEL', 'Autorizado'),
        'color': os.environ.get('PAYFLOW_STATUS_AUTHORIZED_COLOR', '#a855f7'),
        'icon': os.environ.get('PAYFLOW_STATUS_AUTHORIZED_ICON', '🟣'),
        'description': os.environ.get('PAYFLOW_STATUS_AUTHORIZED_DESC', 'Solicitud autorizada, esperando presupuestos'),
        'is_active': os.environ.get('PAYFLOW_STATUS_AUTHORIZED_ACTIVE', 'true').lower() == 'true',
        'is_final': os.environ.get('PAYFLOW_STATUS_AUTHORIZED_FINAL', 'false').lower() == 'true',
        'transitions': os.environ.get('PAYFLOW_STATUS_AUTHORIZED_TRANSITIONS', 'budgeted,closed').split(','),
    },
    'budgeted': {
        'label': os.environ.get('PAYFLOW_STATUS_BUDGETED_LABEL', 'Presupuestado'),
        'color': os.environ.get('PAYFLOW_STATUS_BUDGETED_COLOR', '#16a34a'),
        'icon': os.environ.get('PAYFLOW_STATUS_BUDGETED_ICON', '🟢'),
        'description': os.environ.get('PAYFLOW_STATUS_BUDGETED_DESC', 'Presupuestos adjuntados, esperando autorización de pago'),
        'is_active': os.environ.get('PAYFLOW_STATUS_BUDGETED_ACTIVE', 'true').lower() == 'true',
        'is_final': os.environ.get('PAYFLOW_STATUS_BUDGETED_FINAL', 'false').lower() == 'true',
        'transitions': os.environ.get('PAYFLOW_STATUS_BUDGETED_TRANSITIONS', 'payment_authorized,rejected,closed').split(','),
    },
    'rejected': {
        'label': os.environ.get('PAYFLOW_STATUS_REJECTED_LABEL', 'Rechazado'),
        'color': os.environ.get('PAYFLOW_STATUS_REJECTED_COLOR', '#eab308'),
        'icon': os.environ.get('PAYFLOW_STATUS_REJECTED_ICON', '🟡'),
        'description': os.environ.get('PAYFLOW_STATUS_REJECTED_DESC', 'Presupuestos rechazados, requieren revisión'),
        'is_active': os.environ.get('PAYFLOW_STATUS_REJECTED_ACTIVE', 'true').lower() == 'true',
        'is_final': os.environ.get('PAYFLOW_STATUS_REJECTED_FINAL', 'false').lower() == 'true',
        'transitions': os.environ.get('PAYFLOW_STATUS_REJECTED_TRANSITIONS', 'budgeted,closed').split(','),
    },
    'payment_authorized': {
        'label': os.environ.get('PAYFLOW_STATUS_PAYMENT_AUTH_LABEL', 'Pago Autorizado'),
        'color': os.environ.get('PAYFLOW_STATUS_PAYMENT_AUTH_COLOR', '#f97316'),
        'icon': os.environ.get('PAYFLOW_STATUS_PAYMENT_AUTH_ICON', '🔶'),
        'description': os.environ.get('PAYFLOW_STATUS_PAYMENT_AUTH_DESC', 'Pago autorizado, esperando proceso de facturación'),
        'is_active': os.environ.get('PAYFLOW_STATUS_PAYMENT_AUTH_ACTIVE', 'true').lower() == 'true',
        'is_final': os.environ.get('PAYFLOW_STATUS_PAYMENT_AUTH_FINAL', 'false').lower() == 'true',
        'transitions': os.environ.get('PAYFLOW_STATUS_PAYMENT_AUTH_TRANSITIONS', 'processing_payment,closed').split(','),
    },
    'processing_payment': {
        'label': os.environ.get('PAYFLOW_STATUS_PROCESSING_LABEL', 'Procesando Pago'),
        'color': os.environ.get('PAYFLOW_STATUS_PROCESSING_COLOR', '#06b6d4'),
        'icon': os.environ.get('PAYFLOW_STATUS_PROCESSING_ICON', '💰'),
        'description': os.environ.get('PAYFLOW_STATUS_PROCESSING_DESC', 'Procesando pago/facturación'),
        'is_active': os.environ.get('PAYFLOW_STATUS_PROCESSING_ACTIVE', 'true').lower() == 'true',
        'is_final': os.environ.get('PAYFLOW_STATUS_PROCESSING_FINAL', 'false').lower() == 'true',
        'transitions': os.environ.get('PAYFLOW_STATUS_PROCESSING_TRANSITIONS', 'shipping,closed').split(','),
    },
    'shipping': {
        'label': os.environ.get('PAYFLOW_STATUS_SHIPPING_LABEL', 'En Envío'),
        'color': os.environ.get('PAYFLOW_STATUS_SHIPPING_COLOR', '#8b5cf6'),
        'icon': os.environ.get('PAYFLOW_STATUS_SHIPPING_ICON', '📦'),
        'description': os.environ.get('PAYFLOW_STATUS_SHIPPING_DESC', 'En proceso de envío/entrega'),
        'is_active': os.environ.get('PAYFLOW_STATUS_SHIPPING_ACTIVE', 'true').lower() == 'true',
        'is_final': os.environ.get('PAYFLOW_STATUS_SHIPPING_FINAL', 'false').lower() == 'true',
        'transitions': os.environ.get('PAYFLOW_STATUS_SHIPPING_TRANSITIONS', 'closed').split(','),
    },
    'closed': {
        'label': os.environ.get('PAYFLOW_STATUS_CLOSED_LABEL', 'Cerrado'),
        'color': os.environ.get('PAYFLOW_STATUS_CLOSED_COLOR', '#6b7280'),
        'icon': os.environ.get('PAYFLOW_STATUS_CLOSED_ICON', '⚫'),
        'description': os.environ.get('PAYFLOW_STATUS_CLOSED_DESC', 'Solicitud finalizada'),
        'is_active': os.environ.get('PAYFLOW_STATUS_CLOSED_ACTIVE', 'false').lower() == 'true',
        'is_final': os.environ.get('PAYFLOW_STATUS_CLOSED_FINAL', 'true').lower() == 'true',
        'transitions': os.environ.get('PAYFLOW_STATUS_CLOSED_TRANSITIONS', '').split(',') if os.environ.get('PAYFLOW_STATUS_CLOSED_TRANSITIONS') else [],
    },
}

PAYFLOW_PERMISSIONS = os.environ.get('PAYFLOW_PERMISSIONS', 'can_open,can_comment,can_solve,can_authorize,can_process_payment,can_close').split(',')

PAYFLOW_ROLE_PERMISSIONS = {
    'end_user': {
        'can_open': os.environ.get('PAYFLOW_ROLE_END_USER_OPEN', 'true').lower() == 'true',
        'can_comment': os.environ.get('PAYFLOW_ROLE_END_USER_COMMENT', 'false').lower() == 'true',
        'can_solve': os.environ.get('PAYFLOW_ROLE_END_USER_SOLVE', 'false').lower() == 'true',
        'can_authorize': os.environ.get('PAYFLOW_ROLE_END_USER_AUTHORIZE', 'false').lower() == 'true',
        'can_process_payment': os.environ.get('PAYFLOW_ROLE_END_USER_PAYMENT', 'false').lower() == 'true',
        'can_close': os.environ.get('PAYFLOW_ROLE_END_USER_CLOSE', 'false').lower() == 'true',
    },
    'technician': {
        'can_open': os.environ.get('PAYFLOW_ROLE_TECH_OPEN', 'true').lower() == 'true',
        'can_comment': os.environ.get('PAYFLOW_ROLE_TECH_COMMENT', 'true').lower() == 'true',
        'can_solve': os.environ.get('PAYFLOW_ROLE_TECH_SOLVE', 'true').lower() == 'true',
        'can_authorize': os.environ.get('PAYFLOW_ROLE_TECH_AUTHORIZE', 'false').lower() == 'true',
        'can_process_payment': os.environ.get('PAYFLOW_ROLE_TECH_PAYMENT', 'false').lower() == 'true',
        'can_close': os.environ.get('PAYFLOW_ROLE_TECH_CLOSE', 'false').lower() == 'true',
    },
    'supervisor': {
        'can_open': os.environ.get('PAYFLOW_ROLE_SUPER_OPEN', 'true').lower() == 'true',
        'can_comment': os.environ.get('PAYFLOW_ROLE_SUPER_COMMENT', 'true').lower() == 'true',
        'can_solve': os.environ.get('PAYFLOW_ROLE_SUPER_SOLVE', 'false').lower() == 'true',
        'can_authorize': os.environ.get('PAYFLOW_ROLE_SUPER_AUTHORIZE', 'true').lower() == 'true',
        'can_process_payment': os.environ.get('PAYFLOW_ROLE_SUPER_PAYMENT', 'false').lower() == 'true',
        'can_close': os.environ.get('PAYFLOW_ROLE_SUPER_CLOSE', 'true').lower() == 'true',
    },
    'purchase_manager': {
        'can_open': os.environ.get('PAYFLOW_ROLE_PURCHASE_OPEN', 'false').lower() == 'true',
        'can_comment': os.environ.get('PAYFLOW_ROLE_PURCHASE_COMMENT', 'true').lower() == 'true',
        'can_solve': os.environ.get('PAYFLOW_ROLE_PURCHASE_SOLVE', 'true').lower() == 'true',
        'can_authorize': os.environ.get('PAYFLOW_ROLE_PURCHASE_AUTHORIZE', 'false').lower() == 'true',
        'can_process_payment': os.environ.get('PAYFLOW_ROLE_PURCHASE_PAYMENT', 'true').lower() == 'true',
        'can_close': os.environ.get('PAYFLOW_ROLE_PURCHASE_CLOSE', 'false').lower() == 'true',
    },
    'manager': {
        'can_open': os.environ.get('PAYFLOW_ROLE_MANAGER_OPEN', 'true').lower() == 'true',
        'can_comment': os.environ.get('PAYFLOW_ROLE_MANAGER_COMMENT', 'true').lower() == 'true',
        'can_solve': os.environ.get('PAYFLOW_ROLE_MANAGER_SOLVE', 'false').lower() == 'true',
        'can_authorize': os.environ.get('PAYFLOW_ROLE_MANAGER_AUTHORIZE', 'true').lower() == 'true',
        'can_process_payment': os.environ.get('PAYFLOW_ROLE_MANAGER_PAYMENT', 'true').lower() == 'true',
        'can_close': os.environ.get('PAYFLOW_ROLE_MANAGER_CLOSE', 'true').lower() == 'true',
    },
}

MAX_FILE_SIZE = int(os.environ.get('PAYFLOW_MAX_FILE_SIZE', '52428800'))

API_BASE_URL = os.environ.get('PAYFLOW_API_BASE_URL', '/api/payflow/')
SELECT_OPTIONS_ENDPOINT = os.environ.get('PAYFLOW_SELECT_OPTIONS_ENDPOINT', 'select-options')

FORM_TIMEOUT_SECONDS = int(os.environ.get('PAYFLOW_FORM_TIMEOUT', '300'))
MAX_UPLOAD_FILES = int(os.environ.get('PAYFLOW_MAX_UPLOAD_FILES', '10'))

TREEMAP_MIN_ITEMS = int(os.environ.get('PAYFLOW_TREEMAP_MIN_ITEMS', '3'))
TREEMAP_MAX_ITEMS = int(os.environ.get('PAYFLOW_TREEMAP_MAX_ITEMS', '50')) 