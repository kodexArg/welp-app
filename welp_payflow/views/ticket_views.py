from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.http import HttpResponse
from decimal import Decimal, InvalidOperation

from ..models import Ticket, Message, Attachment
from ..forms import PayflowTicketCreationForm
from ..utils import get_ticket_detail_context_data, can_user_transition_ticket
from ..constants import PAYFLOW_STATUSES


class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'welp_payflow/list.html'
    context_object_name = 'tickets'
    # paginate_by = 10 # Deshabilitado para mostrar todos los tickets

    def get_queryset(self):
        return Ticket.objects.get_queryset(self.request.user).select_related(
            'udn', 'sector', 'accounting_category'
        ).prefetch_related(
            'messages__user', 'messages__attachments'
        ).order_by('-id')


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'welp_payflow/detail.html'
    pk_url_kwarg = 'ticket_id'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'udn', 'sector', 'accounting_category'
        ).prefetch_related(
            'messages__user', 'messages__attachments'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        detail_context = get_ticket_detail_context_data(self.request, self.object)
        
        final_context = {**context, **detail_context}
        
        view_only = self.request.GET.get('view_only', 'false').lower() == 'true'
        final_context['view_only'] = view_only
        
        return final_context

    def post(self, request, *args, **kwargs):
        from ..utils import process_ticket_response
        ticket = self.get_object()
        success, message = process_ticket_response(request, ticket)
        if success:
            messages.success(request, message)
            return redirect('welp_payflow:list')

        messages.error(request, message)
        return redirect('welp_payflow:detail', ticket_id=ticket.id)


class CreateTicketView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = PayflowTicketCreationForm
    template_name = 'welp_payflow/create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from ..utils import get_user_udns
        context['has_create_permissions'] = get_user_udns(self.request.user).exists()
        return context

    def form_valid(self, form):
        with transaction.atomic():
            self.object = form.save()
            
            first_message = Message.objects.create(
                ticket=self.object,
                status='open',
                user=self.request.user,
                body=form.cleaned_data['description']
            )

            for file in form.cleaned_data.get('attachments', []):
                Attachment.objects.create(file=file, message=first_message)
        
        messages.success(self.request, f'Solicitud #{self.object.id} creada exitosamente')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('welp_payflow:success', kwargs={'ticket_id': self.object.id})


class ConfirmCloseTicketView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'welp_payflow/detail.html'
    pk_url_kwarg = 'ticket_id'

    def get(self, request, *args, **kwargs):
        ticket = self.get_object()
        if ticket.status == 'closed':
            messages.warning(request, 'Este ticket ya está cerrado.')
            return redirect('welp_payflow:detail', ticket_id=ticket.id)
        
        is_owner = ticket.created_by == request.user
        if not (is_owner or request.user.is_superuser):
            messages.error(request, 'No tiene permisos para cerrar este ticket.')
            return redirect('welp_payflow:detail', ticket_id=ticket.id)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket = self.object
        is_owner = ticket.created_by == self.request.user
        
        context.update({
            'is_owner': is_owner,
            'requires_comment': not (is_owner or self.request.user.is_superuser),
            'process_close_url': reverse('welp_payflow:process_close', kwargs={'ticket_id': ticket.id}),
            'cancel_url': reverse('welp_payflow:detail', kwargs={'ticket_id': ticket.id}),
            'response_type': 'close',
        })
        return context


class ProcessCloseTicketView(LoginRequiredMixin, View):
    def post(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id)
        if ticket.status == 'closed':
            messages.warning(request, 'Este ticket ya está cerrado.')
            return redirect('welp_payflow:detail', ticket_id=ticket.id)

        comment = request.POST.get('close_comment', '').strip()
        is_owner = ticket.created_by == request.user

        if not (is_owner or request.user.is_superuser) and not comment:
            messages.error(request, 'Debe proporcionar un motivo para cerrar este ticket.')
            return redirect('welp_payflow:detail', ticket_id=ticket.id)

        Message.objects.create(
            ticket=ticket, status='closed', user=request.user, body=comment
        )
        messages.success(request, 'Ticket cerrado exitosamente')
        return redirect('welp_payflow:list')


class TransitionTicketView(LoginRequiredMixin, View):
    def post(self, request, ticket_id, target_status):
        ticket = get_object_or_404(Ticket, id=ticket_id)
        if not ticket.can_transition_to_status(target_status):
            messages.error(request, f'Este ticket no puede cambiar al estado {target_status}.')
            return redirect('welp_payflow:detail', ticket_id=ticket.id)

        if not can_user_transition_ticket(request.user, ticket, target_status):
            messages.error(request, f'No tiene permisos para cambiar este ticket al estado {target_status}.')
            return redirect('welp_payflow:detail', ticket_id=ticket.id)

        comment_field = f'{target_status}_comment'
        comment = request.POST.get(comment_field, '').strip()
        status_info = PAYFLOW_STATUSES.get(target_status, {})
        is_comment_required = status_info.get('comment_required', True)

        # Nueva lógica: solo guardar comentario real, nunca texto automático
        if is_comment_required and not comment:
            messages.error(request, 'Debe ingresar un comentario para este estado.')
            return redirect('welp_payflow:detail', ticket_id=ticket.id)
        body = comment  # Puede ser vacío si no es obligatorio

        with transaction.atomic():
            message = Message.objects.create(
                ticket=ticket, status=target_status, user=request.user, body=body
            )

            if target_status == 'budgeted':
                estimated_amount_str = request.POST.get('estimated_amount')
                if estimated_amount_str:
                    try:
                        ticket.estimated_amount = Decimal(estimated_amount_str)
                        ticket.save(update_fields=['estimated_amount'])
                    except InvalidOperation:
                        messages.warning(request, f"El monto '{estimated_amount_str}' no es un número válido y no se guardó.")
            
            files = request.FILES.getlist('attachments')
            for file in files:
                if file.size <= 52428800:  # 50MB
                    Attachment.objects.create(file=file, message=message)
                else:
                    messages.warning(request, f"El archivo {file.name} es demasiado grande y no se ha adjuntado.")

        messages.success(request, f'Ticket cambiado exitosamente a {status_info.get('label', target_status)}')
        return redirect('welp_payflow:list')
