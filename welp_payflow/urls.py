from django.urls import path
from .views.views import home, list_tickets, ticket_detail, attachment_view, CreateTicketView, success_view, ticket_status_htmx
from .views.others import close_ticket
from .views.htmx import (
    htmx_udn,
    htmx_sector,
    htmx_accounting_category,
    htmx_list_content,
    htmx_confirm_close_ticket,
    htmx_fields_body,
)

app_name = 'welp_payflow'

urlpatterns = [
    path('', home, name='index'),
    path('create/', CreateTicketView.as_view(), name='create'),
    path('success/<int:ticket_id>/', success_view, name='success'),
    path('list/', list_tickets, name='list'),
    path('ticket/<int:ticket_id>/', ticket_detail, name='detail'),
    path('attachment/<int:attachment_id>/', attachment_view, name='attachment'),
]

# URLs para selección con HTMX
urlpatterns += [
    path('htmx/create/udn/', htmx_udn, name='htmx-udn'),
    path('htmx/create/sector/<int:udn>/', htmx_sector, name='htmx-sector'),
    path('htmx/create/accounting-category/<int:sector>/', htmx_accounting_category, name='htmx-accounting-category'),
    path('htmx/create/fields-body/<int:accounting_category>/', htmx_fields_body, name='htmx-fields-body'),
]

# URLs para operaciones HTMX adicionales
urlpatterns += [
    path('htmx/list-content/', htmx_list_content, name='htmx-list-content'),
    path('htmx/confirm-close/<int:ticket_id>/', htmx_confirm_close_ticket, name='htmx-confirm-close'),
    path('htmx/ticket-status/<int:ticket_id>/', ticket_status_htmx, name='ticket_status'),
    path('tickets/<int:ticket_id>/close/', close_ticket, name='close-ticket'),
] 