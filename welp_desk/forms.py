from django import forms
from django.core.exceptions import ValidationError
from .models import UDN, Sector, IssueCategory, Issue
from .constants import MAX_FILE_SIZE


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
            if file.size > MAX_FILE_SIZE:
                raise forms.ValidationError("El archivo no puede superar los 50MB.")
        return file


class CreateIssueForm(forms.ModelForm):
    
    attachments = forms.FileField(
        required=False, 
        widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True}),
        help_text="Puedes adjuntar múltiples archivos"
    )
    
    class Meta:
        model = Issue
        fields = ['name', 'description', 'issue_category']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Título del ticket'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Describe el problema...',
                'rows': 4
            }),
            'issue_category': forms.Select(attrs={
                'class': 'form-select'
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user and hasattr(self.user, 'role_set'):
            pass

    def clean_attachments(self):
        files = self.files.getlist('attachments')
        
        for file in files:
            if file.size > MAX_FILE_SIZE:
                raise ValidationError(f'El archivo {file.name} es demasiado grande. Máximo permitido: 50MB')
                
        return files


class CommentForm(forms.Form):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Escribe tu comentario...',
            'rows': 3,
            'class': 'form-textarea'
        }),
        max_length=1000,
        required=True,
        help_text="Máximo 1000 caracteres"
    )
    
    attachments = forms.FileField(
        required=False, 
        widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True}),
        help_text="Puedes adjuntar múltiples archivos"
    )

    def clean_attachments(self):
        files = self.files.getlist('attachments')
        
        for file in files:
            if file.size > MAX_FILE_SIZE:
                raise ValidationError(f'El archivo {file.name} es demasiado grande. Máximo permitido: 50MB')
                
        return files
