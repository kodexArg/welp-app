"""HTMX views for welp_payflow"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from django.core.paginator import Paginator

from ..models import UDN, Sector, AccountingCategory, Ticket


@login_required(login_url='login')
def htmx_list_content(request):
    """Devuelve el contenido paginado de la lista de tickets para HTMX"""
    tickets = Ticket.objects.all().annotate(last_message_timestamp=models.Max('messages__created_on')).order_by('-last_message_timestamp')
    paginator = Paginator(tickets, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'welp_payflow/partials/list-content.html',
        {
            'tickets': page_obj.object_list,
            'page_obj': page_obj,
        }
    )


@login_required(login_url='login')
def htmx_udn(request):
    """Devuelve el partial de selección de UDN según permisos del usuario"""
    udns = UDN.objects.all()
    return render(request, 'welp_payflow/partials/create/udn.html', {'udns': udns})


@login_required(login_url='login')
def htmx_sector(request, udn):
    """Devuelve los sectores disponibles para una UDN específica"""
    udn_obj = get_object_or_404(UDN, id=udn)
    sectors = Sector.objects.filter(udn=udn_obj)
    return render(request, 'welp_payflow/partials/create/sector.html', {'sectors': sectors})


@login_required(login_url='login')
def htmx_accounting_category(request, sector):
    """Devuelve las categorías contables asociadas a un sector"""
    categories = AccountingCategory.objects.filter(sector__id=sector)
    return render(request, 'welp_payflow/partials/create/accounting-category.html', {
        'categories': categories
    })


@login_required(login_url='login')
def htmx_confirm_close_ticket(request, ticket_id):
    """Muestra el modal de confirmación para cerrar un ticket"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, 'welp_payflow/partials/modal-confirm-close.html', {'ticket': ticket}) 