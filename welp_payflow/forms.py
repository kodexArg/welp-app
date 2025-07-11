# ----------------------------
# Imports
# ----------------------------

from django import forms
from django.core.exceptions import ValidationError

from .models import UDN, Sector, AccountingCategory, Ticket
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


class PayflowTicketCreationForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea,
        label="Descripción",
        help_text="Esta descripción se convertirá en el primer mensaje del ticket",
        error_messages={'required': 'Este campo es obligatorio.'}
    )
    attachments = forms.FileField(
        required=False,
        widget=MultipleFileInput(attrs={'multiple': True}),
        label="Archivos Adjuntos",
        error_messages={'invalid': 'Archivo no válido.'}
    )

    class Meta:
        model = Ticket
        fields = [
            'udn', 'sector', 'accounting_category', 'title', 
            'description', 'estimated_amount', 'attachments'
        ]
        labels = {
            'udn': "UDN",
            'sector': "Sector",
            'accounting_category': "Categoría Contable",
            'title': "Título de la Solicitud",
            'estimated_amount': "Monto Estimado (opcional)",
        }
        error_messages = {
            'title': {
                'required': 'Este campo es obligatorio.',
                'max_length': 'Máximo 255 caracteres.'
            },
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            from .utils import get_user_udns, get_user_sectors, get_user_accounting_categories
            self.fields['udn'].queryset = get_user_udns(self.user)
            self.fields['sector'].queryset = Sector.objects.none()
            self.fields['accounting_category'].queryset = AccountingCategory.objects.none()

            if self.is_bound:
                try:
                    udn_id = int(self.data.get('udn'))
                    udn_obj = UDN.objects.get(pk=udn_id)
                    self.fields['sector'].queryset = get_user_sectors(self.user, udn_obj)
                except (ValueError, TypeError, UDN.DoesNotExist):
                    pass
                
                try:
                    sector_id = int(self.data.get('sector'))
                    sector_obj = Sector.objects.get(pk=sector_id)
                    self.fields['accounting_category'].queryset = get_user_accounting_categories(self.user, sector_obj)
                except (ValueError, TypeError, Sector.DoesNotExist):
                    pass

    def clean(self):
        cleaned_data = super().clean()
        udn = cleaned_data.get('udn')
        sector = cleaned_data.get('sector')
        
        if udn and sector and not sector.udn.filter(id=udn.id).exists():
            raise ValidationError(f"El sector '{sector.name}' no pertenece a la UDN '{udn.name}'.")
        
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