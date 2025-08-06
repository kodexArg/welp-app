from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ChangePasswordForm(forms.Form):
    """
    Formulario para cambiar la contraseña de un usuario.
    
    Utilizado en la página de usuarios de prueba para permitir
    a los superusuarios cambiar contraseñas de usuarios de prueba.
    """
    user_id = forms.IntegerField(widget=forms.HiddenInput())
    new_password = forms.CharField(
        max_length=128,
        widget=forms.HiddenInput(),
        help_text="Nueva contraseña generada aleatoriamente"
    )
    
    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        try:
            user = User.objects.get(id=user_id)
            return user_id
        except User.DoesNotExist:
            raise forms.ValidationError("Usuario no encontrado")
    
    def save(self):
        """
        Cambia la contraseña del usuario especificado.
        
        Returns:
            User: El usuario con la contraseña actualizada
        """
        user_id = self.cleaned_data['user_id']
        new_password = self.cleaned_data['new_password']
        
        user = User.objects.get(id=user_id)
        user.set_password(new_password)
        user.save()
        
        return user