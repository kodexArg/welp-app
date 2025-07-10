"""HTMX views for welp_payflow"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db import models
from django.core.paginator import Paginator
from django.http import HttpResponse

from ..models import UDN, Sector, AccountingCategory, Ticket
from ..utils import get_user_udns, get_user_sectors, get_user_accounting_categories


@login_required(login_url='login')
def htmx_list_content(request):
    """Devuelve el contenido paginado de la lista de tickets para HTMX ordenados por el último mensaje creado"""
    tickets = Ticket.objects.get_queryset(request.user).annotate(
        last_message_timestamp=models.Max('messages__created_on')
    ).order_by('-last_message_timestamp')
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
    udns = get_user_udns(request.user)
    return render(request, 'welp_payflow/partials/create/udn.html', {'udns': udns})


@login_required(login_url='login')
def htmx_sector(request, udn):
    """Devuelve los sectores disponibles para una UDN específica"""
    udn_obj = get_object_or_404(UDN, id=udn)
    sectors = get_user_sectors(request.user, udn_obj)
    return render(request, 'welp_payflow/partials/create/sector.html', {'sectors': sectors})


@login_required(login_url='login')
def htmx_accounting_category(request, sector):
    """Devuelve las categorías contables asociadas a un sector"""
    sector_obj = get_object_or_404(Sector, id=sector)
    categories = get_user_accounting_categories(request.user, sector_obj)
    return render(request, 'welp_payflow/partials/create/accounting-category.html', {
        'categories': categories
    })


@login_required(login_url='login')
def htmx_fields_body(request, accounting_category):
    """Devuelve los campos de detalle (Body) una vez seleccionada la categoría contable"""
    from ..forms import PayflowTicketCreationForm

    form = PayflowTicketCreationForm(user=request.user)
    return render(
        request,
        'welp_payflow/partials/create/fields-body.html',
        {
            'form': form,
        }
    )


@login_required(login_url='login')
def confirm_close_ticket_page(request, ticket_id):
    """Muestra la página de confirmación para cerrar un ticket"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Verificar si el ticket ya está cerrado
    if ticket.status == 'closed':
        messages.warning(request, 'Este ticket ya está cerrado.')
        return redirect('welp_payflow:detail', ticket_id=ticket.id)
    
    # Determinar permisos y tipo de usuario
    is_owner = ticket.created_by == request.user
    is_superuser = request.user.is_superuser
    can_close = is_owner or is_superuser
    
    if not can_close:
        messages.error(request, 'No tiene permisos para cerrar este ticket.')
        return redirect('welp_payflow:detail', ticket_id=ticket.id)
    
    # Preparar variables para el template
    requires_comment = not (is_owner or is_superuser)
    
    if requires_comment:
        label_text = "Motivo del cierre (obligatorio)"
        placeholder_text = "Explique detalladamente el motivo por el cual está cerrando este ticket..."
    else:
        label_text = "Comentario de cierre (opcional)"
        placeholder_text = "Agregue un comentario sobre el cierre del ticket (opcional)..."
    
    context = {
        'ticket': ticket,
        'can_close': can_close,
        'is_owner': is_owner,
        'requires_comment': requires_comment,
        'process_close_url': reverse('welp_payflow:process_close', kwargs={'ticket_id': ticket.id}),
        'cancel_url': reverse('welp_payflow:detail', kwargs={'ticket_id': ticket.id}),
        'label_text': label_text,
        'placeholder_text': placeholder_text,
        'response_type': 'close',
    }
    return render(request, 'welp_payflow/detail.html', context)


@login_required(login_url='login')
def htmx_ticket_feedback_count(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    count = 0
    for _ in ticket.messages.order_by('created_on'):
        if ticket.status != 'feedback':
            break
        count += 1
    if count > 0:
        return HttpResponse(f'<span class="ml-2 align-middle text-xs text-sky-400"><i class="fa fa-comments"></i><sub>{count}</sub></span>')
    return HttpResponse('')