from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView, ListView, TemplateView, View
from django.views.generic.detail import SingleObjectMixin
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse

from ..models import Ticket, Message, Attachment
from ..forms import PayflowTicketCreationForm
from ..utils import can_user_close_ticket, get_ticket_detail_context_data, process_ticket_response
from ..constants import PAYFLOW_STATUSES


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'welp_payflow/home.html'


class TicketListView(LoginRequiredMixin, ListView):
    template_name = 'welp_payflow/list.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        return Ticket.objects.get_queryset(self.request.user).select_related(
            'udn', 'sector', 'accounting_category'
        ).prefetch_related(
            'messages__user',
            'messages__attachments'
        ).order_by('-id')


@login_required(login_url='login')
def attachment_view(request, attachment_id):
    """Vista para mostrar un adjunto individual"""
    attachment = get_object_or_404(Attachment, id=attachment_id)
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


class TicketDetailView(LoginRequiredMixin, SingleObjectMixin, View):
    """
    Vista de detalle de un ticket individual que maneja la presentación (GET)
    y el procesamiento de respuestas y transiciones de estado (POST).
    """
    model = Ticket
    template_name = 'welp_payflow/detail.html'
    pk_url_kwarg = 'ticket_id'

    def get_queryset(self):
        return Ticket.objects.select_related(
            'udn', 'sector', 'accounting_category'
        ).prefetch_related(
            'messages__user',
            'messages__attachments'
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = get_ticket_detail_context_data(request, self.object)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success, message = process_ticket_response(request, self.object)

        if success:
            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Redirect'] = reverse('welp_payflow:detail', kwargs={'ticket_id': self.object.id})
                return response
            return redirect('welp_payflow:detail', ticket_id=self.object.id)
        else:
            context = get_ticket_detail_context_data(request, self.object)
            return render(request, self.template_name, context)


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
def confirm_close_ticket_page(request, ticket_id):
    """Muestra la página de confirmación para cerrar un ticket"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if ticket.status == 'closed':
        messages.warning(request, 'Este ticket ya está cerrado.')
        return redirect('welp_payflow:detail', ticket_id=ticket.id)
    is_owner = ticket.created_by == request.user
    is_superuser = request.user.is_superuser
    can_close = is_owner or is_superuser
    if not can_close:
        messages.error(request, 'No tiene permisos para cerrar este ticket.')
        return redirect('welp_payflow:detail', ticket_id=ticket.id)
    requires_comment = not (is_owner or is_superuser)
    if requires_comment:
        label_text = "Motivo del cierre (obligatorio)"
        placeholder_text = "Explique detalladamente el motivo por el cual está cerrando este ticket..."
    else:
        label_text = "Comentario de cierre (opcional)"
        placeholder_text = "Agregue un comentario sobre el cierre del ticket (opcional)..."
    context = {
        'ticket': ticket,
        'can_close': can_close,
        'is_owner': is_owner,
        'requires_comment': requires_comment,
        'process_close_url': reverse('welp_payflow:process_close', kwargs={'ticket_id': ticket.id}),
        'cancel_url': reverse('welp_payflow:detail', kwargs={'ticket_id': ticket.id}),
        'label_text': label_text,
        'placeholder_text': placeholder_text,
        'response_type': 'close',
    }
    return render(request, 'welp_payflow/detail.html', context)