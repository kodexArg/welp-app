# ----------------------------
# Imports
# ----------------------------

import logging
from django import forms
from django.core.exceptions import ValidationError

from .models import UDN, Sector, AccountingCategory, Ticket
from .constants import MAX_FILE_SIZE

logger = logging.getLogger('welp_payflow')

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
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Describa detalladamente su solicitud...',
            'class': 'form-textarea'
        }),
        label="Descripción",
        error_messages={'required': 'La descripción es obligatoria.'}
    )
    attachments = forms.FileField(
        required=False,
        widget=MultipleFileInput(attrs={
            'multiple': True,
            'accept': '.pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg,.gif',
            'class': 'form-file'
        }),
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
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Escriba un título descriptivo para su solicitud',
                'class': 'form-input',
                'maxlength': 255
            }),
            'estimated_amount': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'class': 'form-input',
                'step': '0.01',
                'min': '0'
            }),
            'udn': forms.Select(attrs={'class': 'form-select'}),
            'sector': forms.Select(attrs={'class': 'form-select'}),
            'accounting_category': forms.Select(attrs={'class': 'form-select'}),
        }
        error_messages = {
            'title': {
                'required': 'El título es obligatorio.',
                'max_length': 'Máximo 255 caracteres.'
            },
            'udn': {
                'required': 'Seleccione una UDN.',
                'invalid_choice': 'UDN no válida.'
            },
            'sector': {
                'required': 'Seleccione un sector.',
                'invalid_choice': 'Sector no válido.'
            },
            'accounting_category': {
                'required': 'Seleccione una categoría.',
                'invalid_choice': 'Categoría no válida.'
            },
            'estimated_amount': {
                'invalid': 'Monto no válido.',
                'min_value': 'El monto no puede ser negativo.'
            }
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        logger.info(f"Inicializando formulario para usuario: {self.user.username if self.user else 'Anónimo'}")
        
        if self.user:
            from .utils import get_user_udns, get_user_sectors, get_user_accounting_categories
            
            # Configurar querysets iniciales
            self.fields['udn'].queryset = get_user_udns(self.user)
            self.fields['sector'].queryset = Sector.objects.none()
            self.fields['accounting_category'].queryset = AccountingCategory.objects.none()

            # Si el formulario está bound (enviado), configurar querysets dinámicamente
            if self.is_bound:
                try:
                    udn_id = int(self.data.get('udn'))
                    udn_obj = UDN.objects.get(pk=udn_id)
                    self.fields['sector'].queryset = get_user_sectors(self.user, udn_obj)
                    logger.info(f"UDN {udn_id} seleccionada, {self.fields['sector'].queryset.count()} sectores disponibles")
                except (ValueError, TypeError, UDN.DoesNotExist) as e:
                    logger.warning(f"Error configurando sectores para UDN: {e}")
                
                try:
                    sector_id = int(self.data.get('sector'))
                    sector_obj = Sector.objects.get(pk=sector_id)
                    self.fields['accounting_category'].queryset = get_user_accounting_categories(self.user, sector_obj)
                    logger.info(f"Sector {sector_id} seleccionado, {self.fields['accounting_category'].queryset.count()} categorías disponibles")
                except (ValueError, TypeError, Sector.DoesNotExist) as e:
                    logger.warning(f"Error configurando categorías para sector: {e}")

    def clean(self):
        cleaned_data = super().clean()
        udn = cleaned_data.get('udn')
        sector = cleaned_data.get('sector')
        accounting_category = cleaned_data.get('accounting_category')
        
        logger.info(f"Validando formulario: UDN={udn}, Sector={sector}, Categoría={accounting_category}")
        
        # Validar relación UDN-Sector
        if udn and sector and not sector.udn.filter(id=udn.id).exists():
            error_msg = f"El sector '{sector.name}' no pertenece a la UDN '{udn.name}'."
            logger.error(f"Error de validación: {error_msg}")
            raise ValidationError(error_msg)
        
        # Validar relación Sector-Categoría
        if sector and accounting_category and not accounting_category.sector.filter(id=sector.id).exists():
            error_msg = f"La categoría '{accounting_category.name}' no pertenece al sector '{sector.name}'."
            logger.error(f"Error de validación: {error_msg}")
            raise ValidationError(error_msg)

        # ---------------------------------------------------------------
        # INICIO: Validación centralizada de permisos de usuario
        # ---------------------------------------------------------------
        if self.user:
            from .utils import get_user_udns, get_user_sectors
            
            # 1. Validar permiso sobre la UDN seleccionada
            user_udns = get_user_udns(self.user)
            if udn and udn not in user_udns:
                logger.error(f"Intento de acceso denegado. Usuario '{self.user.username}' no tiene permisos para UDN '{udn.name}'.")
                self.add_error(None, ValidationError("No tiene permisos para la UDN seleccionada.", code='permission_denied'))
            
            # 2. Si la UDN es válida, validar permiso sobre el Sector
            elif udn and sector:
                user_sectors = get_user_sectors(self.user, udn)
                if sector not in user_sectors:
                    logger.error(f"Intento de acceso denegado. Usuario '{self.user.username}' no tiene permisos para Sector '{sector.name}' en UDN '{udn.name}'.")
                    self.add_error(None, ValidationError("No tiene permisos para el Sector seleccionado.", code='permission_denied'))
        # ---------------------------------------------------------------
        # FIN: Validación de permisos de usuario
        # ---------------------------------------------------------------
        
        return cleaned_data

    def clean_attachments(self):
        files = self.files.getlist('attachments')
        logger.info(f"Validando {len(files)} archivos adjuntos")
        
        for file in files:
            if file.size > MAX_FILE_SIZE:
                error_msg = f'El archivo {file.name} es demasiado grande. Máximo permitido: 50MB'
                logger.warning(f"Archivo rechazado: {error_msg}")
                raise ValidationError(error_msg)
            
            # Validar tipos de archivo permitidos
            allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
            file_extension = '.' + file.name.split('.')[-1].lower() if '.' in file.name else ''
            
            if file_extension not in allowed_extensions:
                error_msg = f'El archivo {file.name} no tiene un formato permitido. Formatos válidos: {", ".join(allowed_extensions)}'
                logger.warning(f"Archivo rechazado: {error_msg}")
                raise ValidationError(error_msg)
        
        logger.info(f"Todos los archivos adjuntos son válidos")
        return files

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise ValidationError('El título es obligatorio.')
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description', '').strip()
        if not description:
            raise ValidationError('La descripción es obligatoria.')
        if len(description) < 10:
            raise ValidationError('La descripción debe tener al menos 10 caracteres.')
        return description
    
    def clean_estimated_amount(self):
        amount = self.cleaned_data.get('estimated_amount')
        if amount is not None and amount < 0:
            raise ValidationError('El monto estimado no puede ser negativo.')
        return amount 