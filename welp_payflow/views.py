from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views import View

from .models import Ticket, Message, Attachment, UDN, Sector, AccountingCategory, Roles
from .forms import PayflowTicketCreationForm


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


class SelectOptionsView(LoginRequiredMixin, View):
    """Vista genérica para obtener opciones de select fields con dependencias"""
    
    def get(self, request, field_type):
        try:
            if field_type == 'udn':
                return self._get_udn_options(request)
            elif field_type == 'sector':
                return self._get_sector_options(request)
            elif field_type == 'accounting':
                return self._get_accounting_options(request)
            else:
                return JsonResponse({'error': 'Tipo de campo no válido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def _get_udn_options(self, request):
        """Obtiene todas las opciones de UDN (sin filtros por ahora)"""
        udns = UDN.objects.all().values('id', 'name')
        options = [{'value': '', 'text': '--- Seleccionar UDN ---'}]
        options.extend([{'value': udn['id'], 'text': udn['name']} for udn in udns])
        return JsonResponse({'options': options})
    
    def _get_sector_options(self, request):
        """Obtiene opciones de Sector filtradas por UDN"""
        udn_id = request.GET.get('udn_id')
        options = [{'value': '', 'text': '--- Seleccionar Sector ---'}]
        
        if udn_id:
            try:
                udn = UDN.objects.get(id=udn_id)
                sectors = udn.payflow_sectors.all().values('id', 'name')
                options.extend([{'value': sector['id'], 'text': sector['name']} for sector in sectors])
            except UDN.DoesNotExist:
                pass
        
        return JsonResponse({'options': options})
    
    def _get_accounting_options(self, request):
        """Obtiene todas las opciones de Categoría Contable (sin filtros por ahora)"""
        categories = AccountingCategory.objects.all().values('id', 'name')
        options = [{'value': '', 'text': '--- Seleccionar Categoría ---'}]
        options.extend([{'value': cat['id'], 'text': cat['name']} for cat in categories])
        return JsonResponse({'options': options})


class CreateTicketView(LoginRequiredMixin, FormView):
    template_name = 'welp_payflow/create.html'
    form_class = PayflowTicketCreationForm
    success_url = reverse_lazy('welp_payflow:list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
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
                
                files = self.request.FILES.getlist('attachments')
                for file in files:
                    if file.size <= 52428800:
                        Attachment.objects.create(
                            file=file,
                            message=first_message
                        )
                
                messages.success(self.request, f'Solicitud #{ticket.id} creada exitosamente')
                
        except Exception as e:
            messages.error(self.request, 'Error al crear la solicitud')
            return self.form_invalid(form)
        
        return super().form_valid(form) 