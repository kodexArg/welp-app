"""
Vistas del módulo de desarrollo y documentación técnica.

Este módulo contiene todas las vistas relacionadas con herramientas de desarrollo,
documentación técnica del sistema y configuración organizacional del proyecto.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from collections import defaultdict
from welp_desk.models import UDN as DeskUDN, Sector as DeskSector, IssueCategory as DeskIssueCategory
from welp_payflow.models import UDN as PayflowUDN, Sector as PayflowSector, AccountingCategory, Roles
from core.models import User

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

@user_passes_test(lambda u: u.is_superuser)
def dev_test_users_view(request):
    """
    Vista para mostrar usuarios de prueba con sus credenciales y permisos.
    
    Solo accesible para superusuarios.
    Muestra todos los usuarios del sistema organizados por rol,
    incluyendo sus UDNs, sectores y contraseñas iniciales.
    """
    # Obtener todos los usuarios con sus roles
    users = User.objects.all().order_by('username')
    
    # Crear diccionario de usuarios con sus datos organizados
    users_data = []
    for user in users:
        user_roles = Roles.objects.filter(user=user).select_related('udn', 'sector')
        
        # Obtener UDNs y sectores únicos del usuario
        user_udns = set()
        user_sectors = set()
        user_role_types = set()
        
        for role in user_roles:
            user_udns.add(role.udn.name)
            user_sectors.add(role.sector.name)
            user_role_types.add(role.role)
        
        users_data.append({
            'user': user,
            'user_udns': sorted(list(user_udns)),
            'user_sectors': sorted(list(user_sectors)),
            'role_types': sorted(list(user_role_types))
        })
    
    # Organizar usuarios por tipo de rol principal
    users_by_role = defaultdict(list)
    for user_data in users_data:
        # Usar el primer rol como principal para organización
        primary_role = user_data['role_types'][0] if user_data['role_types'] else 'sin_rol'
        users_by_role[primary_role].append(user_data)
    
    # Estadísticas generales
    total_users = users.count()
    total_roles = Roles.objects.count()
    unique_role_types = Roles.objects.values('role').distinct()
    
    context = {
        'users_by_role': dict(users_by_role),
        'total_users': total_users,
        'total_roles': total_roles,
        'unique_role_types': unique_role_types,
    }
    
    return render(request, 'core/dev/test_users.html', context)