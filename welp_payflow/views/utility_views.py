from django.shortcuts import render
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from ..models import Attachment, Ticket


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'welp_payflow/home.html'


class AttachmentView(LoginRequiredMixin, DetailView):
    model = Attachment
    template_name = 'welp_payflow/attachment.html'
    pk_url_kwarg = 'attachment_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attachment = self.object
        file_extension = attachment.file.name.split('.')[-1].lower() if '.' in attachment.file.name else ''
        
        file_type = 'unknown'
        if file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']:
            file_type = 'image'
        elif file_extension == 'pdf':
            file_type = 'pdf'
        elif file_extension in ['doc', 'docx', 'txt', 'rtf']:
            file_type = 'document'
        elif file_extension in ['xls', 'xlsx', 'csv']:
            file_type = 'spreadsheet'
        context.update({
            'file_type': file_type,
            'file_extension': file_extension,
            'ticket': attachment.message.ticket,
        })
        return context


class SuccessView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'welp_payflow/success.html'
    pk_url_kwarg = 'ticket_id'
    context_object_name = 'ticket'


class PermissionDeniedErrorView(LoginRequiredMixin, TemplateView):
    """
    Muestra una página de error específica cuando un usuario intenta
    realizar una acción para la que no tiene permisos.
    """
    template_name = 'welp_payflow/permission_denied_error.html'
