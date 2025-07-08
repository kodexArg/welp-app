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
    estimated_amount = forms.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        required=False, 
        label="Monto Estimado (opcional)",
        error_messages={
            'invalid': 'Ingrese un número válido.',
            'max_digits': 'Monto demasiado grande.',
            'max_decimal_places': 'Máximo 2 decimales.',
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
        kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        udn = cleaned_data.get('udn')
        sector = cleaned_data.get('sector')
        accounting_category = cleaned_data.get('accounting_category')
        
        if not all([udn, sector, accounting_category]):
            raise ValidationError("UDN, Sector y Categoría Contable son obligatorios.")
        
        if not sector.udn.filter(id=udn.id).exists():
            raise ValidationError(f"El sector '{sector.name}' no pertenece a la UDN '{udn.name}'.")
        
        if not accounting_category.sector.filter(id=sector.id).exists():
            raise ValidationError(f"La categoría '{accounting_category.name}' no está disponible para el sector '{sector.name}'.")
        
        return cleaned_data

    def clean_attachments(self):
        files = self.files.getlist('attachments')
        for file in files:
            if file.size > MAX_FILE_SIZE:
                raise ValidationError(f'Archivo {file.name} demasiado grande. Máximo: 50MB')
        return files

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if title and len(title) < 10:
            raise ValidationError('Mínimo 10 caracteres.')
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description', '').strip()
        if description and len(description) < 20:
            raise ValidationError('Mínimo 20 caracteres.')
        return description 