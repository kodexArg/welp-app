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
from ..constants import PAYFLOW_STATUSES


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

    response_type = request.GET.get('response_type', 'comment')

    # Determinar el estado o acción para obtener la configuración de UI
    # Si es una transición, usamos el response_type. Si es un comentario normal, usamos 'comment'.
    # Para el caso 'close', la configuración general se obtiene de 'closed' pero la validación de comentario es dinámica.
    ui_key = response_type
    if ui_key == 'close':
        ui_key = 'closed' # Usamos la configuración de 'closed' para el UI del cierre
    elif ui_key == 'feedback':
        ui_key = 'comment' # Usamos la configuración de 'comment' para el UI de feedback

    status_ui_info = PAYFLOW_STATUSES.get(ui_key, {}).get('ui', {})

    # Valores por defecto de UI
    show_attachments = status_ui_info.get('show_attachments', False)
    show_comment_box = status_ui_info.get('show_comment_box', True)
    field_required = status_ui_info.get('comment_required', False)

    # Lógica específica para el cierre de ticket (override de comment_required)
    is_owner = (ticket.created_by == request.user) if ticket.created_by else False
    if response_type == 'close':
        # Si es dueño o superuser, comentario NO es obligatorio para cerrar
        if is_owner or request.user.is_superuser:
            field_required = False
        else:
            # Para otros roles que cierran, el comentario SÍ es obligatorio
            field_required = True

    context = {
        'ticket': ticket,
        'response_type': response_type,
        'response_info': status_ui_info,
        'confirmation_info': status_ui_info.get('confirmation', {}),
        'button_text': status_ui_info.get('button_text', 'Enviar'),
        'comment_placeholder': status_ui_info.get('comment_placeholder', 'Escriba su comentario aquí...'),
        'comment_label': status_ui_info.get('comment_label', 'Comentario'),
        'field_required': field_required,
        'show_attachments': show_attachments,
        'show_comment_box': show_comment_box,
        'is_owner': is_owner if response_type == 'close' else False,
        'hidden_fields': {},
    }

    # URL para la acción del formulario
    if response_type == 'close':
        context['form_action'] = reverse('welp_payflow:process_close', kwargs={'ticket_id': ticket.id})
    elif response_type == 'comment':
        context['form_action'] = request.get_full_path()
    else: # Para otras transiciones de estado
        context['form_action'] = reverse('welp_payflow:transition', kwargs={'ticket_id': ticket.id, 'target_status': response_type})
    
    context['cancel_url'] = reverse('welp_payflow:detail', kwargs={'ticket_id': ticket.id})


    if request.method == 'POST':
        response_body = request.POST.get('response_body', '').strip()
        files = request.FILES.getlist('attachments')
        
        # Validar si el comentario es requerido y está vacío
        if field_required and not response_body:
            messages.error(request, 'El comentario es obligatorio.')
            return render(request, 'welp_payflow/detail.html', context)
        
        # Validar si se requiere adjunto y no hay
        if show_attachments and not files:
            messages.error(request, 'Es obligatorio adjuntar al menos un archivo.')
            return render(request, 'welp_payflow/detail.html', context)

        try:
            with transaction.atomic():
                current_status = ticket.status
                new_status = current_status
                message_type = 'feedback' # Default a feedback

                if response_type == 'close':
                    new_status = 'closed'
                    message_type = 'status'
                elif response_type != 'comment': # Cualquier otra respuesta que sea una transición de estado
                    new_status = response_type
                    message_type = 'status'

                message = Message.objects.create(
                    ticket=ticket,
                    status=new_status,
                    user=request.user,
                    body=response_body,
                    message_type=message_type
                )

                # Manejar archivos adjuntos múltiples
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
                
                success_msg = status_ui_info.get('action_label', response_type.capitalize()) + ' realizado exitosamente'
                if attachment_count > 0:
                    success_msg += f' con {attachment_count} archivo{"s" if attachment_count > 1 else ""} adjunto{"s" if attachment_count > 1 else ""}'
                
                messages.success(request, success_msg)

                if request.headers.get('HX-Request'):
                    response = HttpResponse()
                    response['HX-Redirect'] = reverse('welp_payflow:detail', kwargs={'ticket_id': ticket.id})
                    return response
                
                return redirect('welp_payflow:detail', ticket_id=ticket.id)
                
        except Exception as e:
            messages.error(request, f'Error al procesar la solicitud: {e}')
            return render(request, 'welp_payflow/detail.html', context)

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
        print(f"[PAYFLOW_VIEW] Form inválido. POST data: {self.request.POST.dict()} | FILES: {[f.name for f in self.request.FILES.getlist('attachments')]} | errors: {form.errors.as_json()}")
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
        return render(request, 'components/payflow/ticket_status.html', context)
    except Exception as e:
        # En caso de error, devolver componente vacío
        context = {
            'ticket': None,
        }
        return render(request, 'components/payflow/ticket_status.html', context)