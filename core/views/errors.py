"""
Vistas para el manejo de errores HTTP.
"""
from django.shortcuts import render

def handler404(request, exception):
    """Manejador para errores 404 - Página no encontrada."""
    return render(request, 'core/404.html', status=404) 