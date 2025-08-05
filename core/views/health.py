"""
Vistas de health checks y diagnósticos del sistema.

Este módulo contiene todos los endpoints de verificación de salud
del sistema, base de datos y servicios externos.
"""
from django.http import JsonResponse
from django.db import connection

def health(request):
    """Endpoint de verificación de salud del sistema"""
    return JsonResponse({'status': 'ok', 'message': 'Verificación de estado exitosa'}, status=200)

def db_health_check(request):
    """Endpoint de verificación de salud de la base de datos"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return JsonResponse({'status': 'ok', 'message': 'Conexión a la base de datos exitosa'}, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Error en la conexión a la base de datos'}, status=500) 