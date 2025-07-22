import os
from django.conf import settings

STATUS_MAX_LENGTH = int(os.environ.get('CORE_STATUS_MAX_LENGTH', '20'))

API_BASE_URL = os.environ.get('CORE_API_BASE_URL', '/api/core/')
DEFAULT_TIMEOUT = int(os.environ.get('CORE_DEFAULT_TIMEOUT', '300'))
MAX_UPLOAD_SIZE = int(os.environ.get('CORE_MAX_UPLOAD_SIZE', '52428800')) 