from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Extiende AbstractUser maximizando campos nativos de Django"""
    
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Avatar")
    
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "🔐 AUTENTICACIÓN - Usuarios"
        ordering = ['username']
    
    def __str__(self):
        return self.get_full_name() or self.username