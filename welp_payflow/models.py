import os
import hashlib
import zoneinfo
from datetime import datetime
from django.conf import settings
from django.db import models, transaction
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from .constants import PAYFLOW_STATUSES, STATUS_MAX_LENGTH, PAYFLOW_ROLE_PERMISSIONS
from .utils import get_available_payflow_transitions, get_permissions_for_role_type


class UDN(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")

    class Meta:
        verbose_name = "UDN (Unidad de Negocio)"
        verbose_name_plural = "UDNs"

    def __str__(self):
        return self.name


class Sector(models.Model):
    udn = models.ManyToManyField(UDN, related_name="payflow_sectors", verbose_name="UDNs")
    name = models.CharField(max_length=255, verbose_name="Nombre")

    class Meta:
        verbose_name = "Sector"
        verbose_name_plural = "Sectores"

    def __str__(self):
        return self.name


class AccountingCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    sector = models.ManyToManyField("Sector", related_name="accounting_categories", verbose_name="Sectores")

    class Meta:
        verbose_name = "Categoría Contable"
        verbose_name_plural = "Categorías Contables"

    def __str__(self):
        return self.name


class Roles(models.Model):
    class RoleType(models.TextChoices):
        DIRECTOR = 'director', 'Director'
        MANAGER = 'manager', 'Manager'
        SUPERVISOR = 'supervisor', 'Supervisor'
        PURCHASE_MANAGER = 'purchase_manager', 'Gestor de Compras'
        TECHNICIAN = 'technician', 'Técnico'
        END_USER = 'end_user', 'Usuario Final'

    user = models.ForeignKey('core.User', on_delete=models.CASCADE, related_name='payflow_roles')
    udn = models.ForeignKey(UDN, on_delete=models.CASCADE, null=True, blank=True)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, null=True, blank=True)
    
    role = models.CharField(
        max_length=20,
        choices=RoleType.choices,
        default=RoleType.END_USER,
        verbose_name="Rol Explícito"
    )

    can_open = models.BooleanField(default=False, verbose_name="Puede Abrir")
    can_comment = models.BooleanField(default=False, verbose_name="Puede Comentar")
    can_solve = models.BooleanField(default=False, verbose_name="Puede Gestionar Presupuestos")
    can_authorize = models.BooleanField(default=False, verbose_name="Puede Autorizar")
    can_process_payment = models.BooleanField(default=False, verbose_name="Puede Procesar Pagos")
    can_close = models.BooleanField(default=False, verbose_name="Puede Cerrar")
    
    class Meta:
        verbose_name = "Rol y Permiso"
        verbose_name_plural = "Roles y Permisos"
        unique_together = ['user', 'udn', 'sector']
    
    def __str__(self):
        parts = [self.user.username]
        if self.udn:
            parts.append(self.udn.name)
        if self.sector:
            parts.append(self.sector.name)
        if hasattr(self, 'issue_category') and self.issue_category:
            parts.append(self.issue_category.name)
        
        permissions = []
        if self.can_open: permissions.append("O")
        if self.can_comment: permissions.append("C")
        if self.can_solve: permissions.append("S")
        if self.can_authorize: permissions.append("A")
        if self.can_process_payment: permissions.append("P")
        if self.can_close: permissions.append("X")
        
        perm_str = f"[{'/'.join(permissions)}]" if permissions else "[Sin permisos]"
        return f"{' - '.join(parts)} {perm_str}"
    
    def save(self, *args, **kwargs):
        self.set_permissions_from_role_type(self.role)
        super().save(*args, **kwargs)

    def set_permissions_from_role_type(self, role_type):
        permissions = get_permissions_for_role_type(role_type)
        for perm, value in permissions.items():
            setattr(self, perm, value)
    
    def get_role_type(self):
        return self.role


class TicketManager(models.Manager):
    
    def get_queryset(self, user=None):
        queryset = super().get_queryset()
        if user and not user.is_superuser:
            own_tickets = Q(messages__user=user)
            
            user_roles = user.payflow_roles.all()
            can_view_others = any(PAYFLOW_ROLE_PERMISSIONS.get(role.get_role_type(), {}).get('can_view_others_tickets', False) for role in user_roles)
            if can_view_others:
                role_tickets = Q()
                for role in user_roles:
                    if PAYFLOW_ROLE_PERMISSIONS.get(role.get_role_type(), {}).get('can_view_others_tickets', False):
                        role_filter = Q()
                        if role.udn:
                            role_filter &= Q(udn=role.udn)
                        if role.sector:
                            role_filter &= Q(sector=role.sector)
                        role_tickets |= role_filter
                # Gestores de compra pueden ver tickets en proceso
                if user.payflow_roles.filter(can_process_payment=True).exists():
                    authorized_tickets = Q(messages__status__in=['authorized', 'budgeted', 'payment_authorized', 'processing_payment', 'shipping'])
                    role_tickets |= authorized_tickets
                return queryset.filter(own_tickets | role_tickets).distinct()
            # Otros usuarios: solo sus propios tickets
            return queryset.filter(own_tickets).distinct()
        return queryset


class Ticket(models.Model):
    udn = models.ForeignKey(UDN, on_delete=models.CASCADE, verbose_name="UDN")
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, verbose_name="Sector")
    accounting_category = models.ForeignKey(AccountingCategory, on_delete=models.CASCADE, verbose_name="Categoría Contable")
    
    title = models.CharField(max_length=255, verbose_name="Título de la Solicitud")
    estimated_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto Estimado", null=True, blank=True)
    
    created_on = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    objects = TicketManager()

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"

    def __str__(self):
        return f"{self.title} - {self.udn.name}"

    def get_absolute_url(self):
        return reverse('welp_payflow:list')

    def get_close_url(self):
        return reverse('welp_payflow:confirm-close', kwargs={'ticket_id': self.id})

    @property
    def created_by(self):
        first_message = self.messages.order_by('created_on').first()
        return first_message.user if first_message else None

    @property
    def status(self):
        # Buscar el último mensaje cuyo status sea un estado válido (no comentario)
        valid_statuses = [key for key, value in PAYFLOW_STATUSES.items() if 'is_final' in value]
        last_valid = self.messages.filter(status__in=valid_statuses).order_by('-created_on').first()
        return last_valid.status if last_valid else 'unknown'

    @property
    def start_date(self):
        """Devuelve la fecha de creación del primer mensaje."""
        try:
            return self.messages.earliest('created_on').created_on
        except self.messages.model.DoesNotExist:
            return None

    @property
    def last_updated_date(self):
        """Devuelve la fecha de creación del último mensaje."""
        try:
            return self.messages.latest('created_on').created_on
        except self.messages.model.DoesNotExist:
            return None

    @property
    def status_history(self):
        """
        Devuelve una lista única de todos los estados por los que ha pasado el ticket,
        ordenada según la definición en PAYFLOW_STATUSES.
        """
        message_statuses = set(self.messages.values_list('status', flat=True))
        
        ordered_statuses = [
            status for status in PAYFLOW_STATUSES
            if status in message_statuses
        ]
        
        return ordered_statuses

    def can_transition_to_status(self, new_status):
        current_status = self.status
        if not current_status:
            return new_status == 'open'
        available_transitions = PAYFLOW_STATUSES.get(current_status, {}).get('transitions', [])
        return new_status in available_transitions
    
    def get_available_status_transitions(self):
        current_status = self.status
        return get_available_payflow_transitions(current_status) if current_status else ['open']
    
    @property
    def is_active(self):
        return PAYFLOW_STATUSES.get(self.status, {}).get('is_active', True) if self.status else True
    
    @property
    def is_final(self):
        return PAYFLOW_STATUSES.get(self.status, {}).get('is_final', False) if self.status else False


class Message(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="messages", verbose_name="Ticket")
    status = models.CharField(
        max_length=STATUS_MAX_LENGTH,
        choices=[(key, value['label']) for key, value in PAYFLOW_STATUSES.items() if key != 'comment'],
        default='open',
        verbose_name="Estado"
    )
    message_type = models.CharField(
        max_length=20,
        choices=[
            ('status', 'Cambio de Estado'),
            ('feedback', 'Comentario/Feedback'),
            ('system', 'Sistema'),
        ],
        default='status',
        verbose_name="Tipo de Mensaje"
    )
    reported_on = models.DateTimeField(null=True, blank=True, verbose_name="Fecha Reportada")
    created_on = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Creación")
    user = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="payflow_messages", verbose_name="Usuario")
    body = models.TextField(verbose_name="Cuerpo del Mensaje", blank=True, null=True)

    class Meta:
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        ordering = ['created_on']

    def __str__(self):
        username = self.user.username if self.user else "Usuario eliminado"
        return f"Mensaje de {username} en {self.ticket.title}"

    def save(self, *args, **kwargs):
        # Primero, guardar el mensaje para que forme parte del queryset del ticket
        super().save(*args, **kwargs)

        # La lógica de transición automática solo se aplica a estos estados
        if self.status in ['authorized_by_manager', 'authorized_by_director']:
            with transaction.atomic():
                # Bloquear el ticket para evitar condiciones de carrera
                ticket = Ticket.objects.select_for_update().get(pk=self.ticket.pk)
                
                # Obtener el historial de estados del ticket. Se recalcula aquí,
                # incluyendo el mensaje que acabamos de guardar.
                ticket_statuses = ticket.status_history
                
                # Comprobar si ya existe una autorización de pago para no duplicarla
                if 'payment_authorized' in ticket_statuses:
                    return

                # Comprobar si ambas firmas están presentes
                required_statuses = {'authorized_by_manager', 'authorized_by_director'}
                if required_statuses.issubset(set(ticket_statuses)):
                    # Crear el mensaje de transición automática a 'payment_authorized'
                    Message.objects.create(
                        ticket=ticket,
                        status='payment_authorized',
                        message_type='system',
                        user=None  # Mensaje generado por el sistema
                    )


def attachment_upload_path(instance, filename):
    now = datetime.now()
    date_path = f"{now.year}/{now.month:02d}/{now.day:02d}"
    
    ticket_id = instance.message.ticket.id if instance.message else "unknown"
    
    extension = os.path.splitext(filename)[1]
    hash_input = f"{ticket_id}_{now.strftime('%Y%m%d_%H%M%S')}"
    file_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
    
    new_filename = f"payflow_ticket_{ticket_id}_{file_hash}{extension}"
    
    return f"payflow_attachments/{date_path}/{new_filename}"


class Attachment(models.Model):
    file = models.FileField(upload_to=attachment_upload_path, verbose_name="Archivo")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="attachments", verbose_name="Mensaje")
    attachment_type = models.CharField(
        max_length=50, 
        choices=[
            ('document', 'Documento'),
            ('image', 'Imagen'),
            ('other', 'Otro'),
        ],
        default='other',
        verbose_name="Tipo de Archivo"
    )

    class Meta:
        verbose_name = "Archivo Adjunto"
        verbose_name_plural = "Archivos Adjuntos"

    def __str__(self):
        return f"Archivo {self.get_attachment_type_display()} - Ticket #{self.message.ticket.id}" 


# Eliminar la función can_user_close_ticket de este archivo 