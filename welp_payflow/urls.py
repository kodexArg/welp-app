from django.urls import path
from .views.htmx_views import (
    htmx_udn, htmx_sector, htmx_accounting_category, htmx_fields_body, htmx_list_content, ticket_status_htmx
)
from .views.ticket_views import (
    TicketListView, TicketDetailView, CreateTicketView,
    ConfirmCloseTicketView, ProcessCloseTicketView, TransitionTicketView
)
from .views.utility_views import AttachmentView, SuccessView, HomeView

app_name = 'welp_payflow'

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('list/', TicketListView.as_view(), name='list'),
    path('ticket/<int:ticket_id>/', TicketDetailView.as_view(), name='detail'),
    path('create/', CreateTicketView.as_view(), name='create'),
    path('success/', SuccessView.as_view(), name='success'),
    path('ticket/<int:ticket_id>/attachment/<int:attachment_id>/', AttachmentView.as_view(), name='attachment'),
    path('ticket/<int:ticket_id>/transition/<str:target_status>/', TransitionTicketView.as_view(), name='transition'),
    path('ticket/<int:ticket_id>/close/confirm/', ConfirmCloseTicketView.as_view(), name='confirm_close'),
    path('ticket/<int:ticket_id>/close/process/', ProcessCloseTicketView.as_view(), name='process_close'),

    # HTMX partials
    path('htmx/udn/', htmx_udn, name='htmx_udn'),
    path('htmx/sectors/<int:udn>/', htmx_sector, name='load_sectors'),
    path('htmx/categories/<int:sector>/', htmx_accounting_category, name='load_categories'),
    path('htmx/fields-body/<int:accounting_category>/', htmx_fields_body, name='htmx_fields_body'),
    path('htmx/list-content/', htmx_list_content, name='htmx_list_content'),
    path('htmx/ticket-status/<int:ticket_id>/', ticket_status_htmx, name='htmx_ticket_status'),
]