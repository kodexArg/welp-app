from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy

from .models import Ticket, Message, Attachment, UDN, Sector, IssueCategory, Issue, Roles
from .forms import TicketCreationForm


def index(request):
    """Vista index (página principal) para Welp Desk"""
    return render(request, 'welp_desk/index.html')


def list_dev(request):
    """Vista para listar tickets con sus mensajes y attachments de forma verbosa"""
    context = {
        'tickets': Ticket.objects.all().select_related(
            'udn', 'sector', 'issue_category', 'issue'
        ).prefetch_related(
            'messages__user',
            'messages__attachments'
        ).order_by('-id'),
    }
    return render(request, 'welp_desk/list-dev.html', context)


class CreateTicketView(LoginRequiredMixin, FormView):
    template_name = 'welp_desk/create-dev.html'
    form_class = TicketCreationForm
    success_url = reverse_lazy('welp_desk:index')
    
    def form_valid(self, form):
        try:
            # Se utiliza una transacción atómica para asegurar que la creación del ticket,
            # el mensaje inicial y los archivos adjuntos se realicen como una única operación indivisible.
            # Si ocurre un error en cualquier paso, todos los cambios se revierten automáticamente.
            with transaction.atomic():
                ticket = Ticket.objects.create(
                    udn=form.cleaned_data['udn'],
                    sector=form.cleaned_data['sector'],
                    issue_category=form.cleaned_data['issue_category'],
                    issue=form.cleaned_data['issue']
                )
                
                message = Message.objects.create(
                    ticket=ticket,
                    status='open',
                    user=self.request.user,
                    body=form.cleaned_data['body']
                )
                
                # Procesar archivos adjuntos
                files = self.request.FILES.getlist('attachments')
                for file in files:
                    if file.size <= 52428800:  # 50MB
                        Attachment.objects.create(
                            file=file,
                            filename=file.name,
                            message=message
                        )
                
                messages.success(self.request, f'Ticket #{ticket.id} creado exitosamente')
                
        except Exception as e:
            messages.error(self.request, 'Error al crear el ticket')
            return self.form_invalid(form)
        
        return super().form_valid(form) 