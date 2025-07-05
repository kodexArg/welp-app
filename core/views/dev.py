"""
Vistas del módulo de desarrollo y documentación técnica.

Este módulo contiene todas las vistas relacionadas con herramientas de desarrollo,
documentación técnica del sistema y configuración organizacional del proyecto.

Estructura de navegación:
- UDNs: Ubicaciones y centros de operación
- Sectores: Áreas funcionales por ubicación  
- Categorías Welp Desk: Tipos de incidencias y tickets
- Categorías Welp Payflow: Categorías contables y presupuestarias
- Jerarquía: Estructura organizacional del sistema
- Workflow: Procesos de negocio (compras, autorizaciones)
"""
from django.shortcuts import render
from welp_desk.models import UDN as DeskUDN, Sector as DeskSector, IssueCategory as DeskIssueCategory, Issue
from welp_payflow.models import UDN as PayflowUDN, Sector as PayflowSector, AccountingCategory

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
    
    Muestra información dinámica sobre las ubicaciones físicas y centros
    de operación del sistema desde ambos modelos.
    """
    desk_udns = DeskUDN.objects.all()
    payflow_udns = PayflowUDN.objects.all()
    
    context = {
        'desk_udns': desk_udns,
        'payflow_udns': payflow_udns,
    }
    return render(request, 'core/dev/udns.html', context)

def dev_sectors(request):
    """
    Documentación de Sectores Operativos.
    
    Presenta los sectores funcionales organizados por UDN desde ambos modelos.
    """
    desk_sectors = DeskSector.objects.prefetch_related('udn').all()
    payflow_sectors = PayflowSector.objects.prefetch_related('udn').all()
    
    context = {
        'desk_sectors': desk_sectors,
        'payflow_sectors': payflow_sectors,
    }
    return render(request, 'core/dev/sectors.html', context)

def dev_desk_categories(request):
    """
    Categorías de Incidencias de Welp Desk.
    
    Documenta los tipos de incidencias manejadas por el sistema de tickets:
    DEBO, YPF, Soporte IT, Seguridad, Mantenimiento, etc.
    """
    categories = DeskIssueCategory.objects.prefetch_related('sector', 'issues').all()
    
    context = {
        'categories': categories,
    }
    return render(request, 'core/dev/desk-categories.html', context)

def dev_payflow_categories(request):
    """
    Categorías Contables de Welp Payflow.
    
    Documenta las categorías contables y presupuestarias del sistema
    de flujo de pagos y compras.
    """
    categories = AccountingCategory.objects.prefetch_related('sector').all()
    
    context = {
        'categories': categories,
    }
    return render(request, 'core/dev/payflow-categories.html', context)

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