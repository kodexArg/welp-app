"""
Vistas de demostración y pruebas.

Este módulo contiene vistas para testing de funcionalidades,
demos de HTMX y endpoints de prueba.
"""
from django.http import HttpResponse
import time

def hello_world(request):
    """Endpoint de prueba básico"""
    return HttpResponse("Hola Mundo")

def htmx_demo(request):
    """Vista de demostración de funcionalidad HTMX"""
    if request.htmx:
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
        return HttpResponse("""
            <div class="bg-yellow-50 border border-yellow-200 rounded p-3">
                <span class="text-yellow-700">⚠️ Request no HTMX detectada</span>
            </div>
        """) 