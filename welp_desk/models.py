from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from .constants import DESK_STATUSES, STATUS_MAX_LENGTH, DESK_ROLE_PERMISSIONS
from .utils import get_available_desk_transitions, get_permissions_for_role_type


class UDN(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")

    class Meta:
        verbose_name = "UDN (Unidad de Negocio)"
        verbose_name_plural = "UDNs"

    def __str__(self):
        return self.name


class Sector(models.Model):
    udn = models.ManyToManyField(UDN, related_name="sectors", verbose_name="UDNs")
    name = models.CharField(max_length=255, verbose_name="Nombre")

    class Meta:
        verbose_name = "Sector"
        verbose_name_plural = "Sectores"

    def __str__(self):
        return self.name


class IssueCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    sector = models.ManyToManyField("Sector", related_name="issue_categories", verbose_name="Sectores")

    class Meta:
        verbose_name = "Categoría de Incidencia"
        verbose_name_plural = "Categorías de Incidencias"

    def __str__(self):
        return self.name


class Issue(models.Model):
    issue_category = models.ForeignKey(IssueCategory, on_delete=models.CASCADE, related_name="issues", verbose_name="Categoría")
    name = models.CharField(max_length=255, verbose_name="Nombre")
    display_name = models.CharField(max_length=255, verbose_name="Nombre a Mostrar", blank=True, null=True)
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Incidencia"
        verbose_name_plural = "Incidencias"

    def __str__(self):
        return self.name


class Roles(models.Model):
    user = models.ForeignKey('core.User', on_delete=models.CASCADE, related_name='welp_roles')
    udn = models.ForeignKey(UDN, on_delete=models.CASCADE)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, null=True, blank=True)
    issue_category = models.ForeignKey(IssueCategory, on_delete=models.CASCADE, null=True, blank=True)
    
    can_read = models.BooleanField(default=False, verbose_name="Puede Leer")
    can_comment = models.BooleanField(default=False, verbose_name="Puede Comentar")
    can_solve = models.BooleanField(default=False, verbose_name="Puede Solucionar")
    can_authorize = models.BooleanField(default=False, verbose_name="Puede Autorizar")
    can_open = models.BooleanField(default=False, verbose_name="Puede Abrir")
    can_close = models.BooleanField(default=False, verbose_name="Puede Cerrar")
    
    class Meta:
        verbose_name = "Rol y Permiso"
        verbose_name_plural = "Roles y Permisos"
        unique_together = ['user', 'udn', 'sector', 'issue_category']
    
    def __str__(self):
        parts = [self.user.username]
        if self.udn:
            parts.append(self.udn.name)
        if self.sector:
            parts.append(self.sector.name)
        if hasattr(self, 'issue_category') and self.issue_category:
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
    
    def set_permissions_from_role_type(self, role_type):
        permissions = get_permissions_for_role_type(role_type)
        for perm, value in permissions.items():
            setattr(self, perm, value)
    
    def get_role_type(self):
        if self.can_authorize and self.can_close:
            return 'admin'
        elif self.can_solve and self.can_comment:
            if self.can_authorize:
                return 'supervisor'
            else:
                return 'technician'
        elif self.can_read and self.can_open:
            return 'end_user'
        else:
            return 'custom'


class TicketManager(models.Manager):
    def get_queryset(self, user=None):
        queryset = super().get_queryset()
        if user and not user.is_superuser:
            own_tickets = Q(messages__user=user)
            user_roles = user.welp_roles.all()
            can_view_others = any(DESK_ROLE_PERMISSIONS.get(role.get_role_type(), {}).get('can_view_others_tickets', False) for role in user_roles)
            if can_view_others:
                ticket_filters = Q()
                for role in user_roles:
                    if DESK_ROLE_PERMISSIONS.get(role.get_role_type(), {}).get('can_view_others_tickets', False):
                        role_filter = Q(udn=role.udn)
                        if role.sector:
                            role_filter &= Q(sector=role.sector)
                        if hasattr(role, 'issue_category') and role.issue_category:
                            role_filter &= Q(issue_category=role.issue_category)
                        ticket_filters |= role_filter
                return queryset.filter(own_tickets | ticket_filters).distinct()
            # Otros usuarios: solo sus propios tickets
            return queryset.filter(own_tickets).distinct()
        return queryset


class Ticket(models.Model):
    udn = models.ForeignKey(UDN, on_delete=models.CASCADE, verbose_name="UDN")
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, verbose_name="Sector")
    issue_category = models.ForeignKey(IssueCategory, on_delete=models.CASCADE, verbose_name="Categoría")
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, verbose_name="Incidencia")

    objects = TicketManager()

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"

    def __str__(self):
        return f"{self.issue.name} - {self.udn.name}"

    def get_absolute_url(self):
        return reverse('welp_desk:ticket-view', kwargs={'ticket_id': self.id})

    def get_close_url(self):
        return reverse('welp_desk:htmx-confirm-close', kwargs={'ticket_id': self.id})

    @property
    def created_by(self):
        first_message = self.messages.order_by('created_on').first()
        return first_message.user if first_message else None

    @property
    def status(self):
        last_message = self.messages.order_by('-created_on').first()
        return last_message.status if last_message else 'open'

    def can_transition_to_status(self, new_status):
        current_status = self.status
        if not current_status:
            return new_status == 'open'
        available_transitions = DESK_STATUSES.get(current_status, {}).get('transitions', [])
        return new_status in available_transitions
    
    def get_available_status_transitions(self):
        current_status = self.status
        return get_available_desk_transitions(current_status) if current_status else ['open']
    
    @property
    def is_active(self):
        return DESK_STATUSES.get(self.status, {}).get('is_active', True) if self.status else True
    
    @property
    def is_final(self):
        return DESK_STATUSES.get(self.status, {}).get('is_final', False) if self.status else False


class Message(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="messages", verbose_name="Ticket")
    status = models.CharField(max_length=STATUS_MAX_LENGTH, choices=[(key, value['label']) for key, value in DESK_STATUSES.items()], default='open', verbose_name="Estado")
    reported_on = models.DateTimeField(null=True, blank=True, verbose_name="Fecha Reportada")
    created_on = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    user = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="welp_messages", verbose_name="Usuario")
    body = models.TextField(verbose_name="Cuerpo del Mensaje", blank=True, null=True)

    class Meta:
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
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


def attachment_upload_path(instance, filename):
    import os
    import hashlib
    from datetime import datetime
    
    now = datetime.now()
    date_path = f"{now.year}/{now.month:02d}/{now.day:02d}"
    
    ticket_id = instance.message.ticket.id if instance.message else "unknown"
    
    extension = os.path.splitext(filename)[1]
    hash_input = f"{ticket_id}_{now.strftime('%Y%m%d_%H%M%S')}"
    file_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
    
    new_filename = f"desk_ticket_{ticket_id}_{file_hash}{extension}"
    
    return f"attachments/{date_path}/{new_filename}"


class Attachment(models.Model):
    file = models.FileField(upload_to=attachment_upload_path, verbose_name="Archivo")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="attachments", verbose_name="Mensaje")

    class Meta:
        verbose_name = "Archivo Adjunto"
        verbose_name_plural = "Archivos Adjuntos"

    def __str__(self):
        return f"Archivo #{self.id} - Ticket #{self.message.ticket.id}" 