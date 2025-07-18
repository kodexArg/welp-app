import logging
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.views.generic import TemplateView

from ..models import UDN, Sector, AccountingCategory, Ticket
from ..utils import get_user_udns, get_user_sectors, get_user_accounting_categories
from ..forms import PayflowTicketCreationForm

logger = logging.getLogger('welp_payflow')

@login_required(login_url='login')
def htmx_list_content(request):
    tickets = Ticket.objects.get_queryset(request.user).annotate(
        last_message_timestamp=models.Max('messages__created_on')
    ).order_by('-last_message_timestamp')
    return render(
        request,
        'welp_payflow/partials/list-content.html',
        {'tickets': tickets}
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
