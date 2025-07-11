from django.urls import path
from .views import (
    HomeView, TicketListView, TicketDetailView, AttachmentView,
    CreateTicketView, SuccessView, ConfirmCloseTicketView,
    ProcessCloseTicketView, TransitionTicketView,
    htmx_udn, htmx_sector, htmx_accounting_category,
    htmx_list_content, htmx_fields_body, htmx_ticket_feedback_count,
    ticket_status_htmx,
)

app_name = 'welp_payflow'

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('create/', CreateTicketView.as_view(), name='create'),
    path('success/<int:ticket_id>/', SuccessView.as_view(), name='success'),
    path('list/', TicketListView.as_view(), name='list'),
    path('ticket/<int:ticket_id>/', TicketDetailView.as_view(), name='detail'),
    path('attachment/<int:attachment_id>/', AttachmentView.as_view(), name='attachment'),
    path('ticket/<int:ticket_id>/confirm-close/', ConfirmCloseTicketView.as_view(), name='confirm-close'),
    path('ticket/<int:ticket_id>/process-close/', ProcessCloseTicketView.as_view(), name='process_close'),
    path('ticket/<int:ticket_id>/transition/<str:target_status>/', TransitionTicketView.as_view(), name='transition'),
]

htmx_urlpatterns = [
    path('htmx/create/udn/', htmx_udn, name='htmx-udn'),
    path('htmx/create/sector/<int:udn>/', htmx_sector, name='htmx-sector'),
    path('htmx/create/accounting-category/<int:sector>/', htmx_accounting_category, name='htmx-accounting-category'),
    path('htmx/create/fields-body/<int:accounting_category>/', htmx_fields_body, name='htmx-fields-body'),
    path('htmx/list-content/', htmx_list_content, name='htmx-list-content'),
    path('htmx/ticket-status/<int:ticket_id>/', ticket_status_htmx, name='ticket_status'),
    path('htmx/ticket-feedback-count/<int:ticket_id>/', htmx_ticket_feedback_count, name='htmx-ticket-feedback-count'),
]

urlpatterns += htmx_urlpatterns