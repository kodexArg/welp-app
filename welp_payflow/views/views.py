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
from ..utils import can_user_close_ticket


def home(request):
    return render(request, 'welp_payflow/home.html')


def list_tickets(request):
    context = {
        'tickets': Ticket.objects.get_queryset(request.user).select_related(
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
    """Vista de detalle de un ticket individual con distintas acciones"""
    ticket = get_object_or_404(
        Ticket.objects.select_related(
            'udn', 'sector', 'accounting_category'
        ).prefetch_related(
            'messages__user',
            'messages__attachments'
        ),
        id=ticket_id
    )

    response_type = request.GET.get('action', 'comment')

    if request.method == 'POST' and response_type == 'comment':
        response_body = request.POST.get('response_body', '').strip()
        # Obtener el estado actual del ticket para el nuevo comentario
        current_status = ticket.status
        new_status = current_status
        
        if response_body:
            # Crear el nuevo mensaje de comentario
            message = Message.objects.create(
                ticket=ticket,
                status=new_status,
                user=request.user,
                body=response_body
            )
            
            # Manejar archivos adjuntos múltiples
            files = request.FILES.getlist('attachments')
            attachment_count = 0
            for file in files:
                if file and file.size > 0:  # Verificar que el archivo no esté vacío
                    if file.size <= 52428800:  # 50MB limit
                        Attachment.objects.create(
                            file=file,
                            message=message
                        )
                        attachment_count += 1
                    else:
                        messages.warning(request, f'Archivo {file.name} demasiado grande (máximo 50MB)')
            
            success_msg = 'Comentario agregado exitosamente'
            if attachment_count > 0:
                success_msg += f' con {attachment_count} archivo{"s" if attachment_count > 1 else ""} adjunto{"s" if attachment_count > 1 else ""}'
            
            messages.success(request, success_msg)
            
            # Redirect para evitar resubmit
            return redirect('welp_payflow:detail', ticket_id=ticket.id)

        else:
            messages.error(request, 'El comentario es obligatorio')
    
    context = {
        'ticket': ticket,
        'response_type': response_type,
        'can_close_ticket': can_user_close_ticket(request.user, ticket),
    }

    if response_type == 'close':
        is_owner = ticket.created_by == request.user
        requires_comment = not (is_owner or request.user.is_superuser)
        context.update({
            'process_close_url': reverse('welp_payflow:process_close', kwargs={'ticket_id': ticket.id}),
            'cancel_url': reverse('welp_payflow:detail', kwargs={'ticket_id': ticket.id}),
            'requires_comment': requires_comment,
            'is_owner': is_owner,
        })
    elif response_type == 'authorize':
        context.update({
            'authorize_url': reverse('welp_payflow:authorize-ticket', kwargs={'ticket_id': ticket.id}),
            'cancel_url': reverse('welp_payflow:detail', kwargs={'ticket_id': ticket.id}),
        })

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
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from ..utils import get_user_udns
        available_udns = get_user_udns(self.request.user)
        context['has_create_permissions'] = available_udns.exists()
        return context
    
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


@login_required(login_url='login')
def ticket_status_htmx(request, ticket_id):
    """Vista HTMX para actualizar el estado del ticket"""
    try:
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        # Verificar que el usuario tenga permisos para ver este ticket
        # (simplificado - en producción implementar lógica de permisos completa)
        
        context = {
            'ticket': ticket,
        }
        return render(request, 'components/core/ticket_status.html', context)
    except Exception as e:
        # En caso de error, devolver componente vacío
        context = {
            'ticket': None,
        }
        return render(request, 'components/core/ticket_status.html', context) 