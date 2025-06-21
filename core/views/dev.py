"""
Vistas del módulo de desarrollo y documentación técnica.

Este módulo contiene todas las vistas relacionadas con herramientas de desarrollo,
documentación técnica del sistema y configuración organizacional del proyecto.

Estructura de navegación:
- UDNs: Ubicaciones y centros de operación
- Sectores: Áreas funcionales por ubicación  
- Categorías: Tipos de incidencias y tickets
- Jerarquía: Estructura organizacional del sistema
- Workflow: Procesos de negocio (compras, autorizaciones)
"""
from django.shortcuts import render

def dev_view(request):
    """
    Vista principal del módulo de desarrollo.
    
    Presenta una interfaz de navegación con pestañas para acceder
    a diferentes secciones de documentación técnica usando HTMX.
    """
    return render(request, 'core/dev.html')

def dev_udns(request):
    """
    Documentación de UDNs (Unidades de Negocio).
    
    Muestra información sobre las ubicaciones físicas y centros
    de operación del sistema (Km 1151, Las Bóvedas, Oficina Espejo).
    """
    return render(request, 'core/dev/udns.html')

def dev_sectors(request):
    """
    Documentación de Sectores Operativos.
    
    Presenta los sectores funcionales organizados por UDN:
    Full, Playa, Administración, Parador, etc.
    """
    return render(request, 'core/dev/sectors.html')

def dev_categories(request):
    """
    Categorías de Issues y Tickets.
    
    Documenta los tipos de incidencias manejadas por el sistema:
    DEBO, YPF, Soporte IT, Seguridad, Mantenimiento, etc.
    """
    return render(request, 'core/dev/categories.html')

def dev_hierarchy(request):
    """
    Jerarquía y Estructura del Sistema.
    
    Flujo organizacional completo: UDN → Sector → IssueCategory → Issue → Ticket.
    Muestra las relaciones entre entidades del sistema.
    """
    return render(request, 'core/dev/hierarchy.html')

def dev_purchase_workflow(request):
    """
    Workflow de Procesos de Compras.
    
    Documenta el proceso completo de adquisiciones con 6 etapas,
    actores involucrados, adjuntos requeridos y flujo de decisiones.
    """
    return render(request, 'core/dev/purchase-workflow.html') 