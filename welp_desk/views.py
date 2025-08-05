from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy

from .models import Ticket, Message, Attachment, UDN, Sector, IssueCategory, Issue, Roles
from .forms import TicketCreationForm
from .constants import MAX_FILE_SIZE


def index(request):
    return render(request, 'welp_desk/index.html')


def list_dev(request):
    context = {
        'tickets': Ticket.objects.get_queryset(request.user).select_related(
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
                
                files = self.request.FILES.getlist('attachments')
                for file in files:
                    if file.size <= MAX_FILE_SIZE:
                        Attachment.objects.create(
                            file=file,
                            message=message
                        )
                
                messages.success(self.request, f'Ticket #{ticket.id} creado exitosamente')
                
        except Exception as e:
            messages.error(self.request, 'Error al crear el ticket')
            return self.form_invalid(form)
        
        return super().form_valid(form) 