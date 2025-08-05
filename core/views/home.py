"""
Vistas principales del home y dashboard.

Este módulo contiene las vistas de la página principal y el dashboard
de usuario autenticado.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
import sys
import django

def index(request):
    """Vista home principal con información del sistema"""
    context = {
        'django_version': django.get_version(),
        'python_version': sys.version.split()[0],
        'csrf_enabled': settings.CSRF_COOKIE_SECURE,
        'https_enabled': settings.SECURE_PROXY_SSL_HEADER is not None,
        'debug_mode': settings.DEBUG,
        'storage_backend': 'S3' if not settings.IS_LOCAL else 'Local',
        'cdn_enabled': bool(settings.AWS_S3_CUSTOM_DOMAIN),
        's3_bucket_name': settings.AWS_STORAGE_BUCKET_NAME,
        'environment': 'Desarrollo' if settings.IS_LOCAL else 'Producción',
        'aws_region': settings.AWS_S3_REGION_NAME,
        'server_info': 'Gunicorn' if not settings.IS_LOCAL else 'Django Development Server',
        'htmx_enabled': hasattr(request, 'htmx'),
    }
    return render(request, 'core/index.html', context)

@login_required
def dashboard_view(request):
    """Vista del dashboard de usuario autenticado"""
    context = {
        'user': request.user,
    }
    return render(request, 'core/dashboard.html', context) 