from django import forms
from django.core.exceptions import ValidationError
from .models import UDN, Sector, AccountingCategory


class PayflowTicketCreationForm(forms.Form):
    udn = forms.ModelChoiceField(queryset=UDN.objects.all(), label="UDN")
    sector = forms.ModelChoiceField(queryset=Sector.objects.all(), label="Sector")
    accounting_category = forms.ModelChoiceField(queryset=AccountingCategory.objects.all(), label="Categoría Contable")
    title = forms.CharField(max_length=255, label="Título de la Solicitud")
    description = forms.CharField(widget=forms.Textarea, label="Descripción", help_text="Esta descripción se convertirá en el primer mensaje del ticket")
    estimated_amount = forms.DecimalField(max_digits=12, decimal_places=2, required=False, label="Monto Estimado (opcional)")
    
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
            if file.size > 52428800:  # 50MB
                raise forms.ValidationError("El archivo no puede superar los 50MB.")
        return file 