from django.contrib import admin
from django.utils.html import format_html
from .models import UDN, Sector, IssueCategory, Issue, Roles, Ticket, Message, Attachment


@admin.register(UDN)
class UDNAdmin(admin.ModelAdmin):
    """Administración de Unidades de Negocio."""
    list_display = ['name', 'sectors_count']
    search_fields = ['name']
    ordering = ['name']
    
    def sectors_count(self, obj):
        """Muestra la cantidad de sectores asociados."""
        return obj.sectors.count()
    sectors_count.short_description = 'Sectores'


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    """Administración de Sectores."""
    list_display = ['name', 'udns_list', 'categories_count']
    list_filter = ['udn']
    search_fields = ['name']
    filter_horizontal = ['udn']
    ordering = ['name']
    
    def udns_list(self, obj):
        """Muestra las UDNs asociadas."""
        return ", ".join([udn.name for udn in obj.udn.all()[:3]])
    udns_list.short_description = 'UDNs'
    
    def categories_count(self, obj):
        """Muestra la cantidad de categorías."""
        return obj.issue_categories.count()
    categories_count.short_description = 'Categorías'


@admin.register(IssueCategory)
class IssueCategoryAdmin(admin.ModelAdmin):
    """Administración de Categorías de Incidencias."""
    list_display = ['name', 'sectors_list', 'issues_count']
    list_filter = ['sector']
    search_fields = ['name']
    filter_horizontal = ['sector']
    ordering = ['name']
    
    def sectors_list(self, obj):
        """Muestra los sectores asociados."""
        return ", ".join([sector.name for sector in obj.sector.all()[:3]])
    sectors_list.short_description = 'Sectores'
    
    def issues_count(self, obj):
        """Muestra la cantidad de incidencias."""
        return obj.issues.count()
    issues_count.short_description = 'Incidencias'


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    """Administración de Incidencias."""
    list_display = ['name', 'display_name', 'issue_category', 'tickets_count']
    list_filter = ['issue_category', 'issue_category__sector']
    search_fields = ['name', 'display_name', 'description']
    ordering = ['name']
    
    def tickets_count(self, obj):
        """Muestra la cantidad de tickets asociados."""
        return obj.ticket_set.count()
    tickets_count.short_description = 'Tickets'


@admin.register(Roles)
class RolesAdmin(admin.ModelAdmin):
    """
    Administración de Roles y Permisos.
    Permite configurar fácilmente los permisos granulares de los usuarios.
    """
    list_display = ['user', 'udn', 'sector', 'issue_category', 'permissions_summary']
    list_filter = ['udn', 'sector', 'issue_category', 'can_read', 'can_comment', 'can_solve', 'can_authorize', 'can_open', 'can_close']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'udn__name', 'sector__name', 'issue_category__name']
    ordering = ['user__username', 'udn__name']
    autocomplete_fields = ['user']
    
    # Agrupar los permisos para mejor UX
    fieldsets = (
        ('Usuario y Contexto', {
            'fields': ('user', 'udn', 'sector', 'issue_category'),
            'description': 'Define el usuario y el alcance de sus permisos (UDN, Sector, Categoría)'
        }),
        ('Permisos de Lectura', {
            'fields': ('can_read',),
            'description': 'Permiso básico para ver tickets'
        }),
        ('Permisos de Interacción', {
            'fields': ('can_comment', 'can_solve'),
            'description': 'Permisos para interactuar con tickets'
        }),
        ('Permisos de Gestión', {
            'fields': ('can_authorize', 'can_open', 'can_close'),
            'description': 'Permisos avanzados de gestión de tickets'
        }),
    )
    
    def permissions_summary(self, obj):
        """Muestra un resumen visual de los permisos activos."""
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
        """Optimiza las consultas con select_related."""
        return super().get_queryset(request).select_related('user', 'udn', 'sector', 'issue_category')


class MessageInline(admin.TabularInline):
    """Inline para gestionar mensajes dentro de tickets."""
    model = Message
    extra = 0
    fields = ['user', 'status', 'body', 'reported_on']
    readonly_fields = ['created_on']
    ordering = ['created_on']


class AttachmentInline(admin.TabularInline):
    """Inline para gestionar archivos adjuntos."""
    model = Attachment
    extra = 0
    fields = ['filename', 'file']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Administración de Tickets."""
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
        """Muestra el estado del ticket con color."""
        status = obj.status
        if not status:
            return '<span style="color: gray;">Sin estado</span>'
        
        colors = {
            'open': 'blue',
            'solved': 'green', 
            'closed': 'red',
            'feedback': 'orange'
        }
        color = colors.get(status, 'gray')
        return format_html(f'<span style="color: {color};">● {status.title()}</span>')
    status_display.short_description = 'Estado'
    
    def created_by_display(self, obj):
        """Muestra quién creó el ticket."""
        created_by = obj.created_by
        return created_by.username if created_by else 'Sin usuario'
    created_by_display.short_description = 'Creado por'
    
    def messages_count(self, obj):
        """Muestra la cantidad de mensajes."""
        return obj.messages.count()
    messages_count.short_description = 'Mensajes'
    
    def get_queryset(self, request):
        """Optimiza las consultas."""
        return super().get_queryset(request).select_related(
            'udn', 'sector', 'issue_category', 'issue'
        ).prefetch_related('messages__user')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Administración de Mensajes."""
    list_display = ['ticket', 'user', 'status', 'created_on', 'has_attachments']
    list_filter = ['status', 'created_on']
    search_fields = ['ticket__issue__name', 'user__username', 'body']
    ordering = ['-created_on']
    inlines = [AttachmentInline]
    readonly_fields = ['created_on']
    
    def has_attachments(self, obj):
        """Indica si el mensaje tiene archivos adjuntos."""
        count = obj.attachments.count()
        if count > 0:
            return format_html(f'<span style="color: green;">📎 {count}</span>')
        return '—'
    has_attachments.short_description = 'Adjuntos'


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    """Administración de Archivos Adjuntos."""
    list_display = ['filename', 'message', 'file_size']
    list_filter = ['message__ticket__udn']
    search_fields = ['filename', 'message__ticket__issue__name']
    ordering = ['-id']
    
    def file_size(self, obj):
        """Muestra el tamaño del archivo."""
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


# Configuración del sitio admin
admin.site.site_header = 'Welp Desk - Administración'
admin.site.site_title = 'Welp Desk Admin'
admin.site.index_title = 'Panel de Administración - Mesa de Ayuda' 