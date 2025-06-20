"""
Vistas específicas para el módulo de desarrollo.

Este módulo contiene todas las vistas relacionadas con herramientas de desarrollo,
testing y documentación técnica del proyecto.
"""
from django.shortcuts import render

def dev_view(request):
    """Vista principal de desarrollo con navegación HTMX"""
    return render(request, 'core/dev.html')

def dev_udns(request):
    """Vista para la sección de UDNs"""
    return render(request, 'core/dev/udns.html')

def dev_sectors(request):
    """Vista para la sección de Sectores"""
    return render(request, 'core/dev/sectors.html')

def dev_categories(request):
    """Vista para la sección de Categorías de Issues"""
    return render(request, 'core/dev/categories.html')

def dev_hierarchy(request):
    """Vista para la sección de Jerarquía"""
    return render(request, 'core/dev/hierarchy.html')

def dev_purchase_workflow(request):
    """Vista para la sección de Workflow de Compras"""
    return render(request, 'core/dev/purchase-workflow.html') 