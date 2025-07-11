from django.urls import path
from .views.views import (
    HomeView, TicketListView, TicketDetailView, attachment_view, 
    CreateTicketView, success_view, confirm_close_ticket_page
)
from .views.others import close_ticket, process_close_ticket, authorize_ticket, transition_ticket
from .views.htmx import (
    htmx_udn,
    htmx_sector,
    htmx_accounting_category,
    htmx_list_content,
    htmx_fields_body,
    htmx_ticket_feedback_count,
    ticket_status_htmx,
)

app_name = 'welp_payflow'

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('create/', CreateTicketView.as_view(), name='create'),
    path('success/<int:ticket_id>/', success_view, name='success'),
    path('list/', TicketListView.as_view(), name='list'),
    path('ticket/<int:ticket_id>/', TicketDetailView.as_view(), name='detail'),
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
    path('ticket/<int:ticket_id>/confirm-close/', confirm_close_ticket_page, name='confirm-close'),
    path('htmx/ticket-status/<int:ticket_id>/', ticket_status_htmx, name='ticket_status'),
    path('htmx/ticket-feedback-count/<int:ticket_id>/', htmx_ticket_feedback_count, name='htmx-ticket-feedback-count'),
    path('tickets/<int:ticket_id>/close/', close_ticket, name='close-ticket'),
    path('ticket/<int:ticket_id>/process-close/', process_close_ticket, name='process_close'),
    path('ticket/<int:ticket_id>/authorize/', authorize_ticket, name='authorize-ticket'),
    path('ticket/<int:ticket_id>/transition/<str:target_status>/', transition_ticket, name='transition'),
]