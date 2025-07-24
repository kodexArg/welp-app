import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.views.generic import TemplateView

from ..models import UDN, Sector, AccountingCategory, Ticket, Message
from ..utils import get_user_udns, get_user_sectors, get_user_accounting_categories, can_user_transition_ticket
from ..forms import PayflowTicketCreationForm
from ..constants import PAYFLOW_STATUSES

logger = logging.getLogger('welp_payflow')

@login_required(login_url='login')
def htmx_list_content(request):
    base_qs = Ticket.objects.get_queryset(request.user).select_related(
        'udn', 'sector', 'accounting_category'
    ).prefetch_related(
        'messages__user', 'messages__attachments'
    ).annotate(
        last_message_timestamp=models.Max('messages__created_on')
    ).order_by('-last_message_timestamp')

    # Determinar si el filtro debe estar activo por defecto
    total_tickets = base_qs.count()
    tickets_per_page = 10
    
    # Si el total de tickets es menor a la cantidad por página, desactivar filtro por defecto
    if total_tickets <= tickets_per_page:
        default_needs_attention = False
    else:
        default_needs_attention = True
    
    # Obtener el valor del filtro, usando el valor por defecto calculado
    needs_attention_str = request.GET.get('needs_attention', str(default_needs_attention).lower())
    needs_attention = needs_attention_str.lower() in ['true', '1']

    if needs_attention:
        tickets_requiring_attention_pks = []
        for ticket in base_qs:
            current_status = ticket.status
            transitions = PAYFLOW_STATUSES.get(current_status, {}).get('transitions', [])
            
            user_can_act = any(can_user_transition_ticket(request.user, ticket, transition) for transition in transitions)

            if user_can_act:
                tickets_requiring_attention_pks.append(ticket.pk)
        
        tickets_qs = base_qs.filter(pk__in=tickets_requiring_attention_pks)
    else:
        tickets_qs = base_qs

    paginator = Paginator(tickets_qs, tickets_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tickets': page_obj, 
        'page_obj': page_obj,
        'needs_attention': needs_attention,
        'total_tickets': total_tickets
    }

    if 'needs_attention' in request.GET:
        return render(
            request,
            'welp_payflow/partials/list_content_with_filter_oob.html',
            context
        )

    return render(
        request,
        'welp_payflow/partials/view/list-content.html',
        context
    )


@login_required(login_url='login')
def htmx_udn(request):
    udns = get_user_udns(request.user)
    logger.info(f"Cargando UDNs para usuario {request.user.username}: {udns.count()} disponibles")
    return render(request, 'welp_payflow/partials/create/udn.html', {'udns': udns})


@login_required(login_url='login')
def htmx_sector(request, udn):
    udn_obj = get_object_or_404(UDN, id=udn)
    sectors = get_user_sectors(request.user, udn_obj)
    logger.info(f"Cargando sectores para UDN {udn_obj.name}: {sectors.count()} disponibles")
    return render(request, 'welp_payflow/partials/create/sector.html', {'sectors': sectors})


@login_required(login_url='login')
def htmx_accounting_category(request, sector):
    sector_obj = get_object_or_404(Sector, id=sector)
    categories = get_user_accounting_categories(request.user, sector_obj)
    logger.info(f"Cargando categorías para sector {sector_obj.name}: {categories.count()} disponibles")
    return render(
        request,
        'welp_payflow/partials/create/accounting-category.html',
        {'categories': categories}
    )


@login_required(login_url='login')
def htmx_fields_body(request, accounting_category):
    category_obj = get_object_or_404(AccountingCategory, id=accounting_category)
    form = PayflowTicketCreationForm(user=request.user)
    logger.info(f"Cargando campos del formulario para categoría {category_obj.name}")
    return render(
        request,
        'welp_payflow/partials/create/fields-body.html',
        {'form': form}
    )


@login_required(login_url='login')
def ticket_status_htmx(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, 'components/payflow/ticket_status.html', {'ticket': ticket})


@login_required(login_url='login')
def update_udn_view(request):
    udn_id = request.GET.get('udn_id')
    logger.info(f"Actualizando vista UDN para usuario {request.user.username}, UDN ID: {udn_id}")
    return render(request, "components/payflow/udn_form.html", {"udn_id": udn_id})
