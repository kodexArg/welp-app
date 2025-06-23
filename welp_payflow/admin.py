from django.contrib import admin
from django.utils.html import format_html
from .models import UDN, Sector, AccountingCategory, Roles, Ticket, Message, Attachment
from .constants import PAYFLOW_STATUSES


@admin.register(Roles)
class RolesAdmin(admin.ModelAdmin):
    list_display = ('user', 'udn', 'sector', 'permissions_summary', 'role_type')
    list_filter = ('udn', 'sector', 'can_open', 'can_authorize', 'can_process_payment')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    autocomplete_fields = ['user']
    ordering = ('user__username',)
    
    fieldsets = (
        ('Usuario y Contexto', {
            'fields': ('user', 'udn', 'sector')
        }),
        ('Permisos', {
            'fields': ('can_open', 'can_comment', 'can_solve', 'can_authorize', 'can_process_payment', 'can_close'),
            'classes': ('wide',)
        }),
    )
    
    def permissions_summary(self, obj):
        permissions = []
        if obj.can_open: permissions.append("🆕 Abrir")
        if obj.can_comment: permissions.append("💬 Comentar")
        if obj.can_solve: permissions.append("📋 Presupuestos")
        if obj.can_authorize: permissions.append("✅ Autorizar")
        if obj.can_process_payment: permissions.append("💰 Procesar")
        if obj.can_close: permissions.append("🔒 Cerrar")
        return " | ".join(permissions) if permissions else "Sin permisos"
    permissions_summary.short_description = "Permisos"
    
    def role_type(self, obj):
        if obj.can_process_payment and not obj.can_authorize:
            return "🛒 Gestor de Compras"
        elif obj.can_authorize and obj.can_close:
            return "👔 Supervisor/Gerente"
        elif obj.can_solve and obj.can_comment:
            return "🔧 Técnico"
        elif obj.can_open and not obj.can_comment:
            return "👤 Usuario Final"
        else:
            return "🔧 Personalizado"
    role_type.short_description = "Tipo de Rol"


@admin.register(UDN)
class UDNAdmin(admin.ModelAdmin):
    list_display = ('name', 'sector_count')
    search_fields = ('name',)
    ordering = ('name',)
    
    def sector_count(self, obj):
        return obj.payflow_sectors.count()
    sector_count.short_description = "Sectores"


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'udn_list', 'category_count')
    list_filter = ('udn',)
    search_fields = ('name',)
    filter_horizontal = ('udn',)
    ordering = ('name',)
    
    def udn_list(self, obj):
        return ", ".join([udn.name for udn in obj.udn.all()])
    udn_list.short_description = "UDNs"
    
    def category_count(self, obj):
        return obj.accounting_categories.count()
    category_count.short_description = "Categorías"


@admin.register(AccountingCategory)
class AccountingCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'sector_list', 'ticket_count')
    list_filter = ('sector',)
    search_fields = ('name',)
    filter_horizontal = ('sector',)
    ordering = ('name',)
    
    def sector_list(self, obj):
        return ", ".join([sector.name for sector in obj.sector.all()])
    sector_list.short_description = "Sectores"
    
    def ticket_count(self, obj):
        return obj.ticket_set.count()
    ticket_count.short_description = "Solicitudes"


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    readonly_fields = ('file',)


class MessageInline(admin.StackedInline):
    model = Message
    extra = 0
    readonly_fields = ('created_on', 'reported_on')
    inlines = [AttachmentInline]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'udn', 'sector', 'accounting_category', 'status_badge', 'estimated_amount', 'created_by', 'created_on')
    list_filter = ('udn', 'sector', 'accounting_category', 'created_on')
    search_fields = ('title', 'description')
    readonly_fields = ('created_on', 'created_by', 'status', 'is_active', 'is_final')
    inlines = [MessageInline]
    date_hierarchy = 'created_on'
    ordering = ('-created_on',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'description', 'estimated_amount')
        }),
        ('Clasificación', {
            'fields': ('udn', 'sector', 'accounting_category')
        }),
        ('Estado del Sistema', {
            'fields': ('created_on', 'created_by', 'status', 'is_active', 'is_final'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        status = obj.status
        color = PAYFLOW_STATUSES.get(status, {}).get('color', '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            status.upper() if status else 'OPEN'
        )
    status_badge.short_description = "Estado"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'user', 'status_badge', 'created_on', 'has_attachments')
    list_filter = ('status', 'created_on')
    search_fields = ('ticket__title', 'user__username', 'body')
    readonly_fields = ('created_on', 'reported_on')
    inlines = [AttachmentInline]
    date_hierarchy = 'created_on'
    ordering = ('-created_on',)
    
    def status_badge(self, obj):
        color = PAYFLOW_STATUSES.get(obj.status, {}).get('color', '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = "Estado"
    
    def has_attachments(self, obj):
        count = obj.attachments.count()
        if count > 0:
            return format_html('📎 {} archivo(s)', count)
        return '—'
    has_attachments.short_description = "Adjuntos"


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'attachment_type', 'file_name', 'file_size')
    list_filter = ('attachment_type', 'message__created_on')
    search_fields = ('file', 'message__ticket__title')
    readonly_fields = ('file_name', 'file_size')
    date_hierarchy = 'message__created_on'
    ordering = ('-message__created_on',)
    
    def file_name(self, obj):
        return obj.file.name.split('/')[-1] if obj.file else '—'
    file_name.short_description = "Nombre del Archivo"
    
    def file_size(self, obj):
        if obj.file:
            try:
                size = obj.file.size
                if size < 1024:
                    return f"{size} B"
                elif size < 1024 * 1024:
                    return f"{size / 1024:.1f} KB"
                else:
                    return f"{size / (1024 * 1024):.1f} MB"
            except:
                return "—"
        return "—"
    file_size.short_description = "Tamaño"


admin.site.site_header = 'Welp PayFlow - Administración'
admin.site.site_title = 'Welp PayFlow Admin'
admin.site.index_title = 'Panel de Administración' 