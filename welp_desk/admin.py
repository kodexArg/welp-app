from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
from .models import UDN, Sector, IssueCategory, Issue, Roles, Ticket, Message, Attachment


# ========================================
# 📱 CONFIGURACIÓN DE CATEGORÍAS ADMIN
# ========================================

class WelpDeskAdminConfig:
    """Configuración para organizar el admin en categorías: Autenticación, Configuración y Gestión."""
    pass

# Personalizar Group para la categoría de autenticación
from django.contrib.auth.models import Group

# Patch del modelo Group para cambiar su verbose_name_plural
Group._meta.verbose_name_plural = "🔐 AUTENTICACIÓN - Grupos"

# Registrar Group en welp_desk para la categoría de autenticación
admin.site.unregister(Group)

@admin.register(Group)
class WelpGroupAdmin(GroupAdmin):
    """Administración de Grupos de Django. Complementa el sistema granular de roles de Welp Desk."""
    list_display = ['name', 'permissions_count']
    search_fields = ['name']
    filter_horizontal = ['permissions']
    
    def permissions_count(self, obj):
        """Cantidad de permisos asignados al grupo."""
        return obj.permissions.count()
    permissions_count.short_description = 'Permisos'


# ========================================
# 🔐 AUTENTICACIÓN Y AUTORIZACIÓN
# ========================================

@admin.register(Roles)
class RolesAdmin(admin.ModelAdmin):
    """Gestión de roles y permisos granulares por UDN/Sector/Categoría."""
    list_display = ['user', 'udn', 'sector', 'issue_category', 'permissions_summary']
    list_filter = ['udn', 'sector', 'issue_category', 'can_read', 'can_comment', 'can_solve', 'can_authorize', 'can_open', 'can_close']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'udn__name', 'sector__name', 'issue_category__name']
    ordering = ['user__username', 'udn__name']
    autocomplete_fields = ['user']
    
    fieldsets = (
        ('Usuario y Contexto', {
            'fields': ('user', 'udn', 'sector', 'issue_category'),
        }),
        ('Permisos de Lectura', {
            'fields': ('can_read',),
        }),
        ('Permisos de Interacción', {
            'fields': ('can_comment', 'can_solve'),
        }),
        ('Permisos de Gestión', {
            'fields': ('can_authorize', 'can_open', 'can_close'),
        }),
    )
    
    def permissions_summary(self, obj):
        """Resumen visual de permisos activos con colores."""
        perms = []
        if obj.can_read: perms.append('<span style="color: green;">✓ Leer</span>')
        if obj.can_comment: perms.append('<span style="color: blue;">✓ Comentar</span>')
        if obj.can_solve: perms.append('<span style="color: orange;">✓ Solucionar</span>')
        if obj.can_authorize: perms.append('<span style="color: purple;">✓ Autorizar</span>')
        if obj.can_open: perms.append('<span style="color: teal;">✓ Abrir</span>')
        if obj.can_close: perms.append('<span style="color: red;">✓ Cerrar</span>')
        
        if not perms:
            return '<span style="color: gray;">Sin permisos</span>'
        
        return format_html(' | '.join(perms))
    permissions_summary.short_description = 'Permisos Activos'
    
    def get_queryset(self, request):
        """Optimiza consultas con select_related para evitar N+1."""
        return super().get_queryset(request).select_related('user', 'udn', 'sector', 'issue_category')


# ========================================
# 🏢 ESTRUCTURA ORGANIZACIONAL
# ========================================

@admin.register(UDN)
class UDNAdmin(admin.ModelAdmin):
    """Gestión de Unidades de Negocio (nivel organizacional más alto)."""
    list_display = ['name', 'sectors_count']
    search_fields = ['name']
    ordering = ['name']
    
    def sectors_count(self, obj):
        """Cantidad de sectores asociados."""
        return obj.sectors.count()
    sectors_count.short_description = 'Sectores'


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    """Gestión de Sectores (áreas funcionales como TI, RRHH, Finanzas)."""
    list_display = ['name', 'udns_list', 'categories_count']
    list_filter = ['udn']
    search_fields = ['name']
    filter_horizontal = ['udn']
    ordering = ['name']
    
    def udns_list(self, obj):
        """UDN asociadas (máximo 3 para legibilidad)."""
        return ", ".join([udn.name for udn in obj.udn.all()[:3]])
    udns_list.short_description = 'UDNs'
    
    def categories_count(self, obj):
        """Cantidad de categorías de incidencias."""
        return obj.issue_categories.count()
    categories_count.short_description = 'Categorías'


@admin.register(IssueCategory)
class IssueCategoryAdmin(admin.ModelAdmin):
    """Gestión de Categorías de Incidencias (tipos de problemas por sector)."""
    list_display = ['name', 'sectors_list', 'issues_count']
    list_filter = ['sector']
    search_fields = ['name']
    filter_horizontal = ['sector']
    ordering = ['name']
    
    def sectors_list(self, obj):
        """Sectores asociados (máximo 3)."""
        return ", ".join([sector.name for sector in obj.sector.all()[:3]])
    sectors_list.short_description = 'Sectores'
    
    def issues_count(self, obj):
        """Cantidad de incidencias específicas."""
        return obj.issues.count()
    issues_count.short_description = 'Incidencias'


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    """Gestión de Incidencias Específicas (problemas concretos reportables)."""
    list_display = ['name', 'display_name', 'issue_category', 'tickets_count']
    list_filter = ['issue_category', 'issue_category__sector']
    search_fields = ['name', 'display_name', 'description']
    ordering = ['name']
    
    def tickets_count(self, obj):
        """Cantidad de tickets creados para esta incidencia."""
        return obj.ticket_set.count()
    tickets_count.short_description = 'Tickets'


# ========================================
#  GESTIÓN DE TICKETS Y CONTENIDO
# ========================================

class MessageInline(admin.TabularInline):
    """Gestión inline de mensajes dentro de tickets."""
    model = Message
    extra = 0
    fields = ['user', 'status', 'body', 'reported_on']
    readonly_fields = ['created_on']
    ordering = ['created_on']


class AttachmentInline(admin.TabularInline):
    """Gestión inline de archivos adjuntos."""
    model = Attachment
    extra = 0
    fields = ['filename', 'file']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Gestión principal de tickets. Estado y creador se calculan desde mensajes."""
    list_display = ['id', 'issue', 'udn', 'sector', 'status_display', 'created_by_display', 'messages_count']
    list_filter = ['udn', 'sector', 'issue_category', 'messages__status']
    search_fields = ['issue__name', 'udn__name', 'sector__name', 'messages__body']
    ordering = ['-id']
    inlines = [MessageInline]
    
    fieldsets = (
        ('Información del Ticket', {
            'fields': ('udn', 'sector', 'issue_category', 'issue'),
        }),
    )
    
    def status_display(self, obj):
        """Estado actual con color: rojo=abierto, azul=feedback, verde=solucionado, verde claro=autorizado, amarillo=rechazado, gris=cerrado."""
        status = obj.status
        if not status:
            return '<span style="color: gray;">Sin estado</span>'
        
        colors = {
            'open': '#dc2626',      # rojo (casi naranja)
            'feedback': '#2563eb',  # azul
            'solved': '#16a34a',    # verde
            'authorized': '#22c55e', # verde claro
            'rejected': '#eab308',  # naranja (casi amarillo)
            'closed': '#6b7280'     # gris
        }
        color = colors.get(status, 'gray')
        return format_html(f'<span style="color: {color};">● {status.title()}</span>')
    status_display.short_description = 'Estado'
    
    def created_by_display(self, obj):
        """Usuario que escribió el primer mensaje."""
        created_by = obj.created_by
        return created_by.username if created_by else 'Sin usuario'
    created_by_display.short_description = 'Creado por'
    
    def messages_count(self, obj):
        """Cantidad total de mensajes en la conversación."""
        return obj.messages.count()
    messages_count.short_description = 'Mensajes'
    
    def get_queryset(self, request):
        """Optimiza consultas para evitar N+1 (select_related + prefetch_related)."""
        return super().get_queryset(request).select_related(
            'udn', 'sector', 'issue_category', 'issue'
        ).prefetch_related('messages__user')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Gestión de mensajes individuales. Cada mensaje define el estado del ticket."""
    list_display = ['ticket', 'user', 'status', 'created_on', 'has_attachments']
    list_filter = ['status', 'created_on']
    search_fields = ['ticket__issue__name', 'user__username', 'body']
    ordering = ['-created_on']
    inlines = [AttachmentInline]
    readonly_fields = ['created_on']
    
    def has_attachments(self, obj):
        """Indicador visual de archivos adjuntos."""
        count = obj.attachments.count()
        if count > 0:
            return format_html(f'<span style="color: green;">📎 {count}</span>')
        return '—'
    has_attachments.short_description = 'Adjuntos'


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    """Gestión de archivos adjuntos (evidencia, documentación, capturas)."""
    list_display = ['filename', 'message', 'file_size']
    list_filter = ['message__ticket__udn']
    search_fields = ['filename', 'message__ticket__issue__name']
    ordering = ['-id']
    
    def file_size(self, obj):
        """Tamaño del archivo en unidades legibles (B, KB, MB)."""
        try:
            size = obj.file.size
            if size < 1024:
                return f'{size} B'
            elif size < 1024 * 1024:
                return f'{size / 1024:.1f} KB'
            else:
                return f'{size / (1024 * 1024):.1f} MB'
        except:
            return 'N/A'
    file_size.short_description = 'Tamaño'


# ========================================
# CONFIGURACIÓN GLOBAL DEL SITIO ADMIN
# ========================================

admin.site.site_header = 'Welp Desk - Administración'
admin.site.site_title = 'Welp Desk Admin'
admin.site.index_title = 'Panel de Administración - Mesa de Ayuda' 