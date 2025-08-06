"""
Vistas del módulo de desarrollo y documentación técnica.

Este módulo contiene todas las vistas relacionadas con herramientas de desarrollo,
documentación técnica del sistema y configuración organizacional del proyecto.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from collections import defaultdict
from welp_desk.models import UDN as DeskUDN, Sector as DeskSector, IssueCategory as DeskIssueCategory
from welp_payflow.models import UDN as PayflowUDN, Sector as PayflowSector, AccountingCategory, Roles
from core.models import User
from core.forms import ChangePasswordForm
from core.views.utils import generate_password

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
@require_http_methods(["GET", "POST"])
def dev_test_users_view(request):
    """
    Vista para mostrar usuarios de prueba con sus credenciales y permisos.
    
    Solo accesible para superusuarios.
    Organiza usuarios en jerarquía: UDN > Sector > Rol > Usuario
    
    Maneja POST requests para cambiar contraseñas de usuarios.
    """
    
    # Manejar POST request para cambio de contraseña
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(
                    request, 
                    f'Contraseña actualizada exitosamente para {user.username}'
                )
            except Exception as e:
                messages.error(
                    request, 
                    f'Error al actualizar contraseña: {str(e)}'
                )
        else:
            messages.error(request, 'Error en el formulario de cambio de contraseña')
        
        return redirect('core:dev_test_users')
    # Definir orden de importancia de roles
    role_priority = {
        'director': 1,
        'manager': 2,
        'supervisor': 3,
        'purchase_manager': 4,
        'technician': 5,
        'end_user': 6
    }
    
    # Obtener todos los roles con sus relaciones
    roles = Roles.objects.select_related('user', 'udn', 'sector').all()
    
    # Organizar en jerarquía: UDN > Sector > Rol > Usuario
    hierarchy = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    for role in roles:
        udn_name = role.udn.name if role.udn else 'Sin UDN'
        sector_name = role.sector.name if role.sector else 'Sin Sector'
        role_name = role.get_role_display()
        
        user_data = {
            'user': role.user,
            'username': role.user.username,
            'full_name': f"{role.user.first_name} {role.user.last_name}".strip() or role.user.username,
            'role_type': role.role,
            'role_display': role_name,
            'role_priority': role_priority.get(role.role, 999)
        }
        
        hierarchy[udn_name][sector_name][role_name].append(user_data)
    
    # Ordenar usuarios dentro de cada rol por prioridad y nombre
    for udn in hierarchy:
        for sector in hierarchy[udn]:
            for role in hierarchy[udn][sector]:
                hierarchy[udn][sector][role].sort(
                    key=lambda x: (x['role_priority'], x['full_name'])
                )
    
    # Convertir a dict regular para el template
    hierarchy_dict = {}
    for udn, sectors in hierarchy.items():
        hierarchy_dict[udn] = {}
        for sector, roles in sectors.items():
            hierarchy_dict[udn][sector] = dict(roles)
    
    # Estadísticas generales
    total_users = User.objects.count()
    total_roles = Roles.objects.count()
    unique_udns = len(hierarchy_dict)
    
    # Crear formulario para cambio de contraseña
    change_password_form = ChangePasswordForm()
    
    context = {
        'hierarchy': hierarchy_dict,
        'total_users': total_users,
        'total_roles': total_roles,
        'unique_udns': unique_udns,
        'change_password_form': change_password_form,
    }
    
    return render(request, 'core/dev/test_users.html', context)