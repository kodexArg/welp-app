from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Configuración del admin para el modelo User personalizado"""
    
    # Campos mostrados en la lista
    list_display = ('username', 'get_full_name', 'email', 'phone', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
    
    # Configuración de fieldsets para el formulario de edición
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('phone', 'avatar')
        }),
    )
    
    # Configuración para agregar usuario
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')
        }),
    )


