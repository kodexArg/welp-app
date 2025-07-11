from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from django.core.paginator import Paginator
from django.http import HttpResponse

from ..models import UDN, Sector, AccountingCategory, Ticket
from ..utils import get_user_udns, get_user_sectors, get_user_accounting_categories
from ..forms import PayflowTicketCreationForm


@login_required(login_url='login')
def htmx_list_content(request):
    tickets = Ticket.objects.get_queryset(request.user).annotate(
        last_message_timestamp=models.Max('messages__created_on')
    ).order_by('-last_message_timestamp')
    paginator = Paginator(tickets, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'welp_payflow/partials/list-content.html',
        {'tickets': page_obj.object_list, 'page_obj': page_obj}
    )


@login_required(login_url='login')
def htmx_udn(request):
    udns = get_user_udns(request.user)
    return render(request, 'welp_payflow/partials/create/udn.html', {'udns': udns})


@login_required(login_url='login')
def htmx_sector(request, udn):
    udn_obj = get_object_or_404(UDN, id=udn)
    sectors = get_user_sectors(request.user, udn_obj)
    return render(request, 'welp_payflow/partials/create/sector.html', {'sectors': sectors})


@login_required(login_url='login')
def htmx_accounting_category(request, sector):
    sector_obj = get_object_or_404(Sector, id=sector)
    categories = get_user_accounting_categories(request.user, sector_obj)
    return render(
        request,
        'welp_payflow/partials/create/accounting-category.html',
        {'categories': categories}
    )


@login_required(login_url='login')
def htmx_fields_body(request, accounting_category):
    form = PayflowTicketCreationForm(user=request.user)
    return render(
        request,
        'welp_payflow/partials/create/fields-body.html',
        {'form': form}
    )


@login_required(login_url='login')
def ticket_status_htmx(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, 'components/payflow/ticket_status.html', {'ticket': ticket})
