from django import forms
from django.core.exceptions import ValidationError
from .models import UDN, Sector, AccountingCategory, Roles, Ticket
from .constants import MAX_FILE_SIZE


class PayflowTicketCreationForm(forms.Form):
    udn = forms.ModelChoiceField(queryset=UDN.objects.all(), label="UDN")
    sector = forms.ModelChoiceField(queryset=Sector.objects.all(), label="Sector")
    accounting_category = forms.ModelChoiceField(queryset=AccountingCategory.objects.all(), label="Categoría Contable")
    title = forms.CharField(max_length=255, label="Título de la Solicitud")
    description = forms.CharField(widget=forms.Textarea, label="Descripción", help_text="Esta descripción se convertirá en el primer mensaje del ticket")
    estimated_amount = forms.DecimalField(max_digits=12, decimal_places=2, required=False, label="Monto Estimado (opcional)")
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.is_authenticated:
            user_roles = Roles.objects.filter(user=user, can_open=True)
            
            if user_roles.exists():
                user_udns = UDN.objects.filter(
                    id__in=user_roles.values_list('udn__id', flat=True)
                ).distinct()
                user_sectors = Sector.objects.filter(
                    id__in=user_roles.values_list('sector__id', flat=True)
                ).distinct()
                
                if user_udns.exists():
                    self.fields['udn'].queryset = user_udns
                    if user_udns.count() == 1:
                        self.fields['udn'].initial = user_udns.first()
                
                if user_sectors.exists():
                    self.fields['sector'].queryset = user_sectors
                    if user_sectors.count() == 1:
                        self.fields['sector'].initial = user_sectors.first()
    
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


class AttachmentForm(forms.Form):
    file = forms.FileField(label="Archivo")
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > MAX_FILE_SIZE:
                raise forms.ValidationError("El archivo no puede superar los 50MB.")
        return file


class TicketForm(forms.ModelForm):
    attachments = forms.FileField(
        required=False, 
        widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True}),
        help_text="Puedes adjuntar múltiples archivos"
    )
    
    class Meta:
        model = Ticket
        fields = ['udn', 'sector', 'accounting_category', 'title', 'estimated_amount']
        widgets = {
            'udn': forms.Select(attrs={'class': 'form-select'}),
            'sector': forms.Select(attrs={'class': 'form-select'}),
            'accounting_category': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'placeholder': 'Título de la solicitud'
            }),
            'estimated_amount': forms.NumberInput(attrs={
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if not self.data:
            self.fields['sector'].queryset = Sector.objects.none()
            self.fields['accounting_category'].queryset = AccountingCategory.objects.all()

    def clean_attachments(self):
        files = self.files.getlist('attachments')
        
        for file in files:
            if file.size > MAX_FILE_SIZE:
                raise ValidationError(f'El archivo {file.name} es demasiado grande. Máximo permitido: 50MB')
                
        return files 