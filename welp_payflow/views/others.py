from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import Ticket, Message

@login_required(login_url='login')
def close_ticket(request, ticket_id):
    """Cierra un ticket si el usuario tiene permiso"""
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if ticket.is_final:
        return redirect(ticket.get_absolute_url())


@login_required(login_url='login')
def process_close_ticket(request, ticket_id):
    """Procesa el cierre de un ticket con validaciones de permisos"""
    if request.method != 'POST':
        return redirect('welp_payflow:list')
    
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Verificar si el ticket ya está cerrado
    if ticket.status == 'closed':
        messages.warning(request, 'Este ticket ya está cerrado.')
        return redirect('welp_payflow:detail', ticket_id=ticket.id)
    
    # Validar permisos
    is_owner = ticket.created_by == request.user
    is_superuser = request.user.is_superuser
    
    if not (is_owner or is_superuser):
        # Otros usuarios: requieren comentario obligatorio
        comment = request.POST.get('close_comment', '').strip()
        if not comment:
            messages.error(request, 'Debe proporcionar un motivo para cerrar este ticket.')
            return redirect('welp_payflow:detail', ticket_id=ticket.id)
        
        # Crear mensaje con advertencia para otros usuarios
        close_message = f"Ticket cerrado por {request.user.username} (no propietario): {comment}"
    else:
        # Usuario propietario o superusuario
        comment = request.POST.get('close_comment', '').strip()
        if comment:
            close_message = f"Ticket cerrado: {comment}"
        else:
            close_message = 'Ticket cerrado por el usuario'
    
    # Crear mensaje de cierre
    Message.objects.create(
        ticket=ticket,
        status='closed',
        user=request.user,
        body=close_message
    )
    
    messages.success(request, 'Ticket cerrado exitosamente')
    return redirect('welp_payflow:list')

    # Permisos simplificados: cualquier usuario autenticado puede cerrar

    ticket.messages.create(
        user=request.user,
        status='closed',
        body='Ticket cerrado por el usuario'
    )
    return redirect(ticket.get_absolute_url())


@login_required(login_url='login')
def authorize_ticket(request, ticket_id):
    """Autoriza un ticket si el usuario tiene permisos"""
    if request.method != 'POST':
        return redirect('welp_payflow:detail', ticket_id=ticket_id)

    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Verificar permisos básicos
    has_permission = request.user.is_superuser or request.user.payflow_roles.filter(can_authorize=True).exists()
    if not has_permission:
        messages.error(request, 'No tiene permisos para autorizar este ticket.')
        return redirect('welp_payflow:detail', ticket_id=ticket.id)

    # Validar transición de estado
    if not ticket.can_transition_to_status('authorized'):
        messages.error(request, 'Este ticket no puede ser autorizado en su estado actual.')
        return redirect('welp_payflow:detail', ticket_id=ticket.id)

    comment = request.POST.get('authorize_comment', '').strip()

    Message.objects.create(
        ticket=ticket,
        status='authorized',
        user=request.user,
        body=comment or 'Ticket autorizado por el usuario'
    )

    messages.success(request, 'Ticket autorizado exitosamente')
    return redirect('welp_payflow:detail', ticket_id=ticket.id)
