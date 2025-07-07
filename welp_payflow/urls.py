from django.urls import path
from .views.views import home, list_tickets, CreateTicketView
from .views.others import close_ticket
from .views.htmx import (
    htmx_udn,
    htmx_sector,
    htmx_accounting_category,
    htmx_list_content,
    htmx_confirm_close_ticket,
)

app_name = 'welp_payflow'

urlpatterns = [
    path('', home, name='index'),
    path('create/', CreateTicketView.as_view(), name='create'),
    path('list/', list_tickets, name='list'),
]

# URLs para selección con HTMX
urlpatterns += [
    path('htmx/create/udn/', htmx_udn, name='htmx-udn'),
    path('htmx/create/sector/<int:udn>/', htmx_sector, name='htmx-sector'),
    path('htmx/create/accounting-category/<int:sector>/', htmx_accounting_category, name='htmx-accounting-category'),
]

# URLs para operaciones HTMX adicionales
urlpatterns += [
    path('htmx/list-content/', htmx_list_content, name='htmx-list-content'),
    path('htmx/confirm-close/<int:ticket_id>/', htmx_confirm_close_ticket, name='htmx-confirm-close'),
    path('tickets/<int:ticket_id>/close/', close_ticket, name='close-ticket'),
] 