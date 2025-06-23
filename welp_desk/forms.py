from django import forms
from django.core.exceptions import ValidationError
from .models import UDN, Sector, IssueCategory, Issue


class TicketCreationForm(forms.Form):
    """Formulario para crear tickets."""
    
    udn = forms.ModelChoiceField(queryset=UDN.objects.all(), label="UDN")
    sector = forms.ModelChoiceField(queryset=Sector.objects.all(), label="Sector")
    issue_category = forms.ModelChoiceField(queryset=IssueCategory.objects.all(), label="Categoría")
    issue = forms.ModelChoiceField(queryset=Issue.objects.all(), label="Incidencia")
    body = forms.CharField(widget=forms.Textarea, required=False, label="Descripción")
    
    def clean(self):
        cleaned_data = super().clean()
        udn = cleaned_data.get('udn')
        sector = cleaned_data.get('sector')
        issue_category = cleaned_data.get('issue_category')
        issue = cleaned_data.get('issue')
        
        if not all([udn, sector, issue_category, issue]):
            raise ValidationError("Todos los campos son obligatorios.")
        
        if not sector.udn.filter(id=udn.id).exists():
            raise ValidationError(f"El sector '{sector.name}' no pertenece a la UDN '{udn.name}'.")
        
        if not issue_category.sector.filter(id=sector.id).exists():
            raise ValidationError(f"La categoría '{issue_category.name}' no está disponible para el sector '{sector.name}'.")
        
        if issue.issue_category.id != issue_category.id:
            raise ValidationError(f"La incidencia '{issue.name}' no pertenece a la categoría '{issue_category.name}'.")
        
        return cleaned_data


class AttachmentForm(forms.Form):
    """Formulario para archivos adjuntos a tickets."""
    file = forms.FileField(label="Archivo")
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 52428800:  # 50MB
                raise forms.ValidationError("El archivo no puede superar los 50MB.")
        return file
