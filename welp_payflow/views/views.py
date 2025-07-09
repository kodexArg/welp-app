from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse

from ..models import Ticket, Message, Attachment
from ..forms import PayflowTicketCreationForm


def home(request):
    return render(request, 'welp_payflow/home.html')


def list_tickets(request):
    context = {
        'tickets': Ticket.objects.all().select_related(
            'udn', 'sector', 'accounting_category'
        ).prefetch_related(
            'messages__user',
            'messages__attachments'
        ).order_by('-id'),
    }
    return render(request, 'welp_payflow/list.html', context)


@login_required(login_url='login')
def attachment_view(request, attachment_id):
    """Vista para mostrar un adjunto individual"""
    attachment = get_object_or_404(Attachment, id=attachment_id)
    
    # Determinar el tipo de archivo para la presentación
    file_extension = attachment.file.name.split('.')[-1].lower() if '.' in attachment.file.name else ''
    
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
    pdf_extensions = ['pdf']
    document_extensions = ['doc', 'docx', 'txt', 'rtf']
    spreadsheet_extensions = ['xls', 'xlsx', 'csv']
    
    file_type = 'unknown'
    if file_extension in image_extensions:
        file_type = 'image'
    elif file_extension in pdf_extensions:
        file_type = 'pdf'
    elif file_extension in document_extensions:
        file_type = 'document'
    elif file_extension in spreadsheet_extensions:
        file_type = 'spreadsheet'
    
    context = {
        'attachment': attachment,
        'file_type': file_type,
        'file_extension': file_extension,
        'ticket': attachment.message.ticket,
    }
    return render(request, 'welp_payflow/attachment.html', context)


@login_required(login_url='login')
def ticket_detail(request, ticket_id):
    """Vista de detalle de un ticket individual"""
    ticket = get_object_or_404(
        Ticket.objects.select_related(
            'udn', 'sector', 'accounting_category'
        ).prefetch_related(
            'messages__user',
            'messages__attachments'
        ), 
        id=ticket_id
    )
    
    if request.method == 'POST':
        response_body = request.POST.get('response_body', '').strip()
        new_status = request.POST.get('status', '').strip()
        
        if response_body:
            # Crear el nuevo mensaje de respuesta
            message_status = new_status if new_status else ticket.status
            
            message = Message.objects.create(
                ticket=ticket,
                status=message_status,
                user=request.user,
                body=response_body
            )
            
            # Manejar archivos adjuntos si los hay
            files = request.FILES.getlist('attachments')
            for file in files:
                if file.size <= 52428800:  # 50MB limit
                    Attachment.objects.create(
                        file=file,
                        message=message
                    )
            
            messages.success(request, 'Respuesta enviada exitosamente')
            
            # Redirect para evitar resubmit
            return redirect('welp_payflow:detail', ticket_id=ticket.id)
        else:
            messages.error(request, 'El mensaje de respuesta es obligatorio')
    
    context = {
        'ticket': ticket,
    }
    return render(request, 'welp_payflow/detail.html', context)


def success_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    context = {
        'ticket': ticket,
    }
    return render(request, 'welp_payflow/success.html', context)


class CreateTicketView(LoginRequiredMixin, FormView):
    template_name = 'welp_payflow/create.html'
    form_class = PayflowTicketCreationForm
    
    def get_form_kwargs(self):
        return super().get_form_kwargs()
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            field_name = form.fields[field].label if field in form.fields else 'Error'
            for error in errors:
                messages.error(self.request, f'{field_name}: {error}')
        
        for error in form.non_field_errors():
            messages.error(self.request, error)
        
        if self.request.headers.get('HX-Request'):
            return render(self.request, self.template_name, {'form': form})
        
        return super().form_invalid(form)
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                ticket = Ticket.objects.create(
                    udn=form.cleaned_data['udn'],
                    sector=form.cleaned_data['sector'],
                    accounting_category=form.cleaned_data['accounting_category'],
                    title=form.cleaned_data['title'],
                    estimated_amount=form.cleaned_data.get('estimated_amount')
                )
                
                first_message = Message.objects.create(
                    ticket=ticket,
                    status='open',
                    user=self.request.user,
                    body=form.cleaned_data['description']
                )
                
                files = form.cleaned_data.get('attachments') or []
                for file in files:
                    if file.size <= 52428800:
                        Attachment.objects.create(
                            file=file,
                            message=first_message
                        )
                
                messages.success(self.request, f'Solicitud #{ticket.id} creada exitosamente')
                
                if self.request.headers.get('HX-Request'):
                    response = HttpResponse()
                    response['HX-Redirect'] = reverse('welp_payflow:success', kwargs={'ticket_id': ticket.id})
                    return response
                
                return redirect('welp_payflow:success', ticket_id=ticket.id)
                
        except Exception as e:
            messages.error(self.request, 'Error al crear la solicitud')
            return self.form_invalid(form) 