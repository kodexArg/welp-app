"""
Vistas del módulo de desarrollo y documentación técnica.

Este módulo contiene todas las vistas relacionadas con herramientas de desarrollo,
documentación técnica del sistema y configuración organizacional del proyecto.
"""
from django.shortcuts import render
from welp_desk.models import UDN as DeskUDN, Sector as DeskSector, IssueCategory as DeskIssueCategory
from welp_payflow.models import UDN as PayflowUDN, Sector as PayflowSector, AccountingCategory

def dev_view(request):
    """
    Vista principal del módulo de desarrollo.
    
    Presenta un portal de navegación a las diferentes secciones de
    documentación y herramientas de desarrollo.
    """
    return render(request, 'core/dev.html')

def dev_categories_view(request):
    """
    Documentación de UDNs, Sectores y Categorías.
    
    Muestra información sobre las UDNs, Sectores y Categorías de ambos
    sistemas (Welp Desk y Welp Payflow), así como sus jerarquías.
    """
    desk_udns = DeskUDN.objects.all()
    payflow_udns = PayflowUDN.objects.all()
    desk_sectors = DeskSector.objects.prefetch_related('udn').all()
    payflow_sectors = PayflowSector.objects.prefetch_related('udn').all()
    desk_categories = DeskIssueCategory.objects.prefetch_related('sector').all()
    payflow_categories = AccountingCategory.objects.prefetch_related('sector').all()
    
    context = {
        'desk_udns': desk_udns,
        'payflow_udns': payflow_udns,
        'desk_sectors': desk_sectors,
        'payflow_sectors': payflow_sectors,
        'desk_categories': desk_categories,
        'payflow_categories': payflow_categories,
    }
    return render(request, 'core/dev/categories.html', context)

def dev_purchase_workflow_view(request):
    """
    Manual de Usuario del Workflow de Compras.
    
    Documenta el proceso completo de adquisiciones, actores, estados y
    flujo de decisiones, sirviendo como guía para usuarios finales.
    """
    return render(request, 'core/dev/purchase_workflow.html')

def dev_playground_view(request):
    """
    Página de Playground para pruebas de componentes y desarrollo.
    """
    return render(request, 'core/dev/under_development.html')