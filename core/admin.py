from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.html import format_html
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Formulario personalizado para crear usuarios"""
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer campos obligatorios
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True


class CustomUserChangeForm(UserChangeForm):
    """Formulario personalizado para editar usuarios"""
    
    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Configuración del admin para el modelo User personalizado"""
    
    # Formularios personalizados
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    # Campos mostrados en la lista
    list_display = ('username', 'get_full_name', 'email', 'phone', 'avatar_preview', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
    ordering = ('username',)
    
    # Configuración de fieldsets para el formulario de edición
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    # Configuración para agregar usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Información Personal', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar'),
            'description': 'Complete la información personal del usuario'
        }),
        ('Permisos', {
            'classes': ('wide', 'collapse'),
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ('date_joined', 'last_login')
    
    def avatar_preview(self, obj):
        """Mostrar preview del avatar en la lista"""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="30" height="30" style="border-radius: 50%;" />',
                obj.avatar.url
            )
        return "Sin avatar"
    avatar_preview.short_description = "Avatar"
    
    def get_full_name(self, obj):
        """Mostrar nombre completo en la lista"""
        return obj.get_full_name() or obj.username
    get_full_name.short_description = "Nombre Completo"
    
    def save_model(self, request, obj, form, change):
        """Personalizar el guardado del modelo"""
        if not change:  # Si es un nuevo usuario
            # Asegurar que el usuario esté activo por defecto
            if not hasattr(obj, 'is_active') or obj.is_active is None:
                obj.is_active = True
        super().save_model(request, obj, form, change)


