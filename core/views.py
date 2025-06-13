from django.http import HttpResponse
import os
import sys
import django
from django.db import connection
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

def home(request):
    """
    Vista principal de la aplicación con información detallada del sistema.
    
    Args:
        request: Objeto HttpRequest de Django
        
    Returns:
        HttpResponse: Renderiza la plantilla home.html con información del sistema
    """
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
    return render(request, 'core/home.html', context)

def hello_world(request):
    """
    Vista de prueba que devuelve un mensaje simple.
    
    Args:
        request: Objeto HttpRequest de Django
        
    Returns:
        HttpResponse: Mensaje "Hello World"
    """
    return HttpResponse("Hola Mundo")

def health(request):
    """
    Endpoint de verificación de salud de la aplicación.
    
    Args:
        request: Objeto HttpRequest de Django
        
    Returns:
        JsonResponse: Estado de la aplicación y mensaje de éxito
    """
    return JsonResponse({'status': 'ok', 'message': 'Verificación de estado exitosa'}, status=200)

def db_health_check(request):
    """
    Verifica la conexión a la base de datos.
    
    Args:
        request: Objeto HttpRequest de Django
        
    Returns:
        JsonResponse: Estado de la conexión a la base de datos
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return JsonResponse({'status': 'ok', 'message': 'Conexión a la base de datos exitosa'}, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Error en la conexión a la base de datos'}, status=500)

def htmx_demo(request):
    """
    Vista de demostración para HTMX
    """
    if request.htmx:
        # Es una request HTMX, devolver solo el fragmento
        import time
        timestamp = int(time.time())
        return HttpResponse(f"""
            <div class="bg-green-50 border border-green-200 rounded p-3">
                <div class="flex items-center justify-between">
                    <span class="text-green-700 font-medium">✅ HTMX Funcionando!</span>
                    <span class="text-xs text-green-600">Timestamp: {timestamp}</span>
                </div>
                <div class="text-sm text-green-600 mt-1">
                    Request detectada como HTMX. Intercambio exitoso sin recarga de página.
                </div>
                <button 
                    hx-get="{request.path}"
                    hx-target="#htmx-demo-result" 
                    hx-swap="outerHTML"
                    class="mt-2 text-xs bg-green-600 hover:bg-green-700 text-white px-2 py-1 rounded transition-colors">
                    🔄 Probar de nuevo
                </button>
            </div>
        """)
    else:
        # Request normal
        return HttpResponse("""
            <div class="bg-yellow-50 border border-yellow-200 rounded p-3">
                <span class="text-yellow-700">⚠️ Request no HTMX detectada</span>
            </div>
        """)
