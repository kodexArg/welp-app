from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from ..models import Ticket

@login_required(login_url='login')
def close_ticket(request, ticket_id):
    """Cierra un ticket si el usuario tiene permiso"""
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if ticket.is_final:
        return redirect(ticket.get_absolute_url())

    # Permisos simplificados: cualquier usuario autenticado puede cerrar

    ticket.messages.create(
        user=request.user,
        status='closed',
        body='Ticket cerrado por el usuario'
    )

    return redirect(ticket.get_absolute_url()) 