# ----------------------------
# Imports
# ----------------------------

from django import forms
from django.core.exceptions import ValidationError

from .models import UDN, Sector, AccountingCategory
from .constants import MAX_FILE_SIZE


# ----------------------------
# Widgets personalizados
# ----------------------------


class MultipleFileInput(forms.ClearableFileInput):
    """Widget que habilita carga múltiple sin generar ValueError."""

    allow_multiple_selected = True


# ----------------------------
# Formulario de creación
# ----------------------------


class PayflowTicketCreationForm(forms.Form):
    udn = forms.ModelChoiceField(
        queryset=UDN.objects.all(), 
        label="UDN"
    )
    sector = forms.ModelChoiceField(
        queryset=Sector.objects.all(), 
        label="Sector"
    )
    accounting_category = forms.ModelChoiceField(
        queryset=AccountingCategory.objects.all(), 
        label="Categoría Contable"
    )
    title = forms.CharField(
        max_length=255, 
        label="Título de la Solicitud",
        error_messages={
            'required': 'Este campo es obligatorio.',
            'max_length': 'Máximo 255 caracteres.'
        }
    )
    description = forms.CharField(
        widget=forms.Textarea, 
        label="Descripción",
        help_text="Esta descripción se convertirá en el primer mensaje del ticket",
        error_messages={
            'required': 'Este campo es obligatorio.',
        }
    )
    estimated_amount = forms.IntegerField(
        required=False,
        label="Monto Estimado (opcional)",
        error_messages={
            'invalid': 'Ingrese un número válido.',
            'max_value': 'Monto demasiado grande.',
            'min_value': 'No puede ser negativo.'
        }
    )
    
    attachments = forms.FileField(
        required=False,
        widget=MultipleFileInput(attrs={'multiple': True}),
        label="Archivos Adjuntos",
        error_messages={
            'invalid': 'Archivo no válido.'
        }
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            from .utils import get_user_udns, get_user_sectors, get_user_accounting_categories
            available_udns = get_user_udns(self.user)
            self.fields['udn'].queryset = available_udns
            # Inicializar querysets vacíos por defecto
            self.fields['sector'].queryset = Sector.objects.none()
            self.fields['accounting_category'].queryset = AccountingCategory.objects.none()
            # Si hay datos en self.data (POST), poblar dinámicamente los querysets
            udn_id = self.data.get('udn')
            sector_id = self.data.get('sector')
            if udn_id:
                try:
                    udn_obj = UDN.objects.get(pk=udn_id)
                    self.fields['sector'].queryset = get_user_sectors(self.user, udn_obj)
                except UDN.DoesNotExist:
                    pass
            if sector_id:
                try:
                    sector_obj = Sector.objects.get(pk=sector_id)
                    self.fields['accounting_category'].queryset = get_user_accounting_categories(self.user, sector_obj)
                except Sector.DoesNotExist:
                    pass
    
    def clean(self):
        cleaned_data = super().clean()
        udn = cleaned_data.get('udn')
        sector = cleaned_data.get('sector')
        accounting_category = cleaned_data.get('accounting_category')
        user = self.user
        missing = []
        if not udn:
            missing.append('udn')
        if not sector:
            missing.append('sector')
        if not accounting_category:
            missing.append('accounting_category')
        if missing:
            print(f"[PAYFLOW_FORM] Faltan campos obligatorios: {missing} | cleaned_data={cleaned_data} | self.data={self.data}")
            raise ValidationError("UDN, Sector y Categoría Contable son obligatorios.")
        if self.user:
            from .utils import can_user_create_ticket_in_context
            if not can_user_create_ticket_in_context(self.user, udn, sector):
                print("[PAYFLOW_FORM] Sin permisos")
                raise ValidationError("No tiene permisos para crear tickets en esta UDN/Sector.")
        if not sector.udn.filter(id=udn.id).exists():
            print("[PAYFLOW_FORM] Sector no pertenece a UDN")
            raise ValidationError(f"El sector '{sector.name}' no pertenece a la UDN '{udn.name}'.")
        if not accounting_category.sector.filter(id=sector.id).exists():
            print("[PAYFLOW_FORM] Categoría no pertenece a sector")
            raise ValidationError(f"La categoría '{accounting_category.name}' no está disponible para el sector '{sector.name}'.")
        ticket_data = {
            'udn': udn.name if udn else None,
            'sector': sector.name if sector else None,
            'accounting_category': accounting_category.name if accounting_category else None,
            'title': cleaned_data.get('title'),
            'description': cleaned_data.get('description'),
            'estimated_amount': cleaned_data.get('estimated_amount'),
            'user': user.username if user else None,
            'attachments_count': len(self.files.getlist('attachments')) if hasattr(self, 'files') and self.files else 0
        }
        print(f"[PAYFLOW_FORM] Datos para guardar en DB: {ticket_data}")
        return cleaned_data

    def clean_attachments(self):
        files = self.files.getlist('attachments')
        for file in files:
            if file.size > MAX_FILE_SIZE:
                raise ValidationError(f'Archivo {file.name} demasiado grande. Máximo: 50MB')
        return files

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description', '').strip()
        return description 