from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from .constants import (
    TICKET_STATUS_CHOICES, 
    STATUS_MAX_LENGTH,
    can_transition_to,
    get_available_transitions, 
    ACTIVE_STATUSES,
    FINAL_STATUSES
)


class UDN(models.Model):
    """Divisiones principales: sucursales, departamentos, etc."""
    name = models.CharField(max_length=255, verbose_name="Nombre")

    class Meta:
        verbose_name = "UDN (Unidad de Negocio)"
        verbose_name_plural = "📋 CONFIGURACIÓN - UDNs"

    def __str__(self):
        return self.name


class Sector(models.Model):
    """Áreas funcionales dentro de UDNs. Relación M2M permite sectores transversales."""
    udn = models.ManyToManyField(UDN, related_name="sectors", verbose_name="UDNs")
    name = models.CharField(max_length=255, verbose_name="Nombre")

    class Meta:
        verbose_name = "Sector"
        verbose_name_plural = "📋 CONFIGURACIÓN - Sectores"

    def __str__(self):
        return self.name


class IssueCategory(models.Model):
    """Categorías específicas por sector (ej: TI->Hardware, RRHH->Vacaciones)"""
    name = models.CharField(max_length=255, verbose_name="Nombre")
    sector = models.ManyToManyField("Sector", related_name="issue_categories", verbose_name="Sectores")

    class Meta:
        verbose_name = "Categoría de Incidencia"
        verbose_name_plural = "📋 CONFIGURACIÓN - Categorías"

    def __str__(self):
        return self.name


class Issue(models.Model):
    """Incidencias específicas dentro de categorías. display_name para UX customizable."""
    issue_category = models.ForeignKey(IssueCategory, on_delete=models.CASCADE, related_name="issues", verbose_name="Categoría")
    name = models.CharField(max_length=255, verbose_name="Nombre")
    display_name = models.CharField(max_length=255, verbose_name="Nombre a Mostrar", blank=True, null=True)
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Incidencia"
        verbose_name_plural = "📋 CONFIGURACIÓN - Incidencias"

    def __str__(self):
        return self.name


class Roles(models.Model):
    """Sistema de permisos granular por UDN/Sector/Categoría. Superusuarios bypass automático."""
    user = models.ForeignKey('core.User', on_delete=models.CASCADE, related_name='welp_roles')
    udn = models.ForeignKey(UDN, on_delete=models.CASCADE)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, null=True, blank=True)
    issue_category = models.ForeignKey(IssueCategory, on_delete=models.CASCADE, null=True, blank=True)
    
    # Permisos granulares independientes
    can_read = models.BooleanField(default=False, verbose_name="Puede Leer")
    can_comment = models.BooleanField(default=False, verbose_name="Puede Comentar")
    can_solve = models.BooleanField(default=False, verbose_name="Puede Solucionar")
    can_authorize = models.BooleanField(default=False, verbose_name="Puede Autorizar")
    can_open = models.BooleanField(default=False, verbose_name="Puede Abrir")
    can_close = models.BooleanField(default=False, verbose_name="Puede Cerrar")
    
    class Meta:
        verbose_name = "Rol y Permiso"
        verbose_name_plural = "🔐 AUTENTICACIÓN - Roles y Permisos"
        unique_together = ['user', 'udn', 'sector', 'issue_category']
    
    def __str__(self):
        parts = [self.user.username, self.udn.name]
        if self.sector:
            parts.append(self.sector.name)
        if self.issue_category:
            parts.append(self.issue_category.name)
        
        permissions = []
        if self.can_read: permissions.append("R")
        if self.can_comment: permissions.append("C")
        if self.can_solve: permissions.append("S")
        if self.can_authorize: permissions.append("A")
        if self.can_open: permissions.append("O")
        if self.can_close: permissions.append("X")
        
        perm_str = f"[{'/'.join(permissions)}]" if permissions else "[Sin permisos]"
        return f"{' - '.join(parts)} {perm_str}"


class TicketManager(models.Manager):
    """Filtrado automático de tickets por roles. Superusuarios ven todo."""
    
    def get_queryset(self, user=None):
        queryset = super().get_queryset()
        if user and not user.is_superuser:
            user_roles = user.welp_roles.filter(can_read=True)
            
            if not user_roles.exists():
                return queryset.none()
            
            ticket_filters = Q()
            for role in user_roles:
                role_filter = Q(udn=role.udn)
                if role.sector:
                    role_filter &= Q(sector=role.sector)
                if role.issue_category:
                    role_filter &= Q(issue_category=role.issue_category)
                ticket_filters |= role_filter
            
            return queryset.filter(ticket_filters).distinct()
        return queryset


class Ticket(models.Model):
    udn = models.ForeignKey(UDN, on_delete=models.CASCADE, verbose_name="UDN")
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, verbose_name="Sector")
    issue_category = models.ForeignKey(IssueCategory, on_delete=models.CASCADE, verbose_name="Categoría")
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, verbose_name="Incidencia")

    objects = TicketManager()

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "🎫 GESTIÓN - Tickets"

    def __str__(self):
        return f"{self.issue.name} - {self.udn.name}"

    def get_absolute_url(self):
        return reverse('welp_desk:ticket-view', kwargs={'ticket_id': self.id})

    def get_close_url(self):
        return reverse('welp_desk:htmx-confirm-close', kwargs={'ticket_id': self.id})

    @property
    def created_by(self):
        """Usuario del primer mensaje."""
        first_message = self.messages.order_by('created_on').first()
        return first_message.user if first_message else None

    @property
    def status(self):
        """Estado del último mensaje."""
        last_message = self.messages.order_by('-created_on').first()
        return last_message.status if last_message else None

    def can_transition_to_status(self, new_status):
        """Valida transiciones de estado según business rules."""
        current_status = self.status
        if not current_status:
            return new_status == 'open'
        return can_transition_to(current_status, new_status)
    
    def get_available_status_transitions(self):
        """Estados disponibles desde estado actual."""
        current_status = self.status
        return get_available_transitions(current_status) if current_status else ['open']
    
    @property
    def is_active(self):
        """True si ticket no está en estado final."""
        return self.status in ACTIVE_STATUSES if self.status else True
    
    @property
    def is_final(self):
        """True si ticket está en estado final."""
        return self.status in FINAL_STATUSES if self.status else False


class Message(models.Model):
    STATUS_CHOICES = TICKET_STATUS_CHOICES
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="messages", verbose_name="Ticket")
    status = models.CharField(max_length=STATUS_MAX_LENGTH, choices=STATUS_CHOICES, default='open', verbose_name="Estado")
    reported_on = models.DateTimeField(null=True, blank=True, verbose_name="Fecha Reportada")
    created_on = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    user = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="welp_messages", verbose_name="Usuario")
    body = models.TextField(verbose_name="Cuerpo del Mensaje", blank=True, null=True)

    class Meta:
        verbose_name = "Mensaje"
        verbose_name_plural = "🎫 GESTIÓN - Mensajes"
        ordering = ['created_on']

    def __str__(self):
        username = self.user.username if self.user else "Usuario eliminado"
        return f"Mensaje de {username} en {self.ticket.issue.name}"

    def save(self, *args, **kwargs):
        if self.reported_on is None:
            from django.conf import settings
            import zoneinfo
            tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)
            self.reported_on = timezone.now().astimezone(tz)
        super().save(*args, **kwargs)


class Attachment(models.Model):
    """Archivos adjuntos vinculados a mensajes específicos."""
    file = models.FileField(upload_to="attachments/", verbose_name="Archivo")
    filename = models.CharField(max_length=255, verbose_name="Nombre del Archivo")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="attachments", verbose_name="Mensaje", blank=True, null=True)

    class Meta:
        verbose_name = "Archivo Adjunto"
        verbose_name_plural = "🎫 GESTIÓN - Adjuntos"

    def __str__(self):
        return self.filename 