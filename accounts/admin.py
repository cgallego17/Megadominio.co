from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (User, TwoFactorCode, LoginAttempt, HostingPlan, ClientService, EmailAccount, 
                     ServiceNotification, ServiceCategory, PurchasableService, Cart, CartItem, Order, OrderItem,
                     WompiConfiguration, WompiTransaction, WompiWebhookEvent, TermsAcceptance, ExchangeRate)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin personalizado para el modelo User
    """
    list_display = ('username', 'email', 'user_type', 'company', 'is_active', 'created_at')
    list_filter = ('user_type', 'is_active', 'two_factor_enabled', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'company')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('user_type', 'phone', 'company', 'address', 'city', 'country')
        }),
        ('Configuración de Seguridad', {
            'fields': ('two_factor_enabled',)
        }),
    )

@admin.register(HostingPlan)
class HostingPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price_monthly', 'price_yearly', 'storage_gb', 'email_accounts', 'is_active')
    list_filter = ('plan_type', 'is_active', 'ssl_included', 'backup_daily', 'support_24_7')
    search_fields = ('name', 'description')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'plan_type', 'description', 'is_active')
        }),
        ('Precios', {
            'fields': ('price_monthly', 'price_yearly')
        }),
        ('Características', {
            'fields': ('storage_gb', 'bandwidth_gb', 'email_accounts', 'databases', 'domains')
        }),
        ('Servicios Incluidos', {
            'fields': ('ssl_included', 'backup_daily', 'support_24_7')
        }),
    )

@admin.register(ClientService)
class ClientServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'service_type', 'status', 'expiry_date', 'days_until_expiry', 'price')
    list_filter = ('service_type', 'status', 'billing_cycle', 'auto_renew', 'hosting_plan')
    search_fields = ('name', 'client__username', 'client__email', 'domain_name')
    date_hierarchy = 'expiry_date'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('client', 'service_type', 'name', 'description', 'hosting_plan')
        }),
        ('Fechas y Facturación', {
            'fields': ('start_date', 'expiry_date', 'billing_cycle', 'price', 'auto_renew')
        }),
        ('Estado', {
            'fields': ('status',)
        }),
        ('Detalles Técnicos', {
            'fields': ('domain_name', 'server_ip', 'cpanel_username'),
            'classes': ('collapse',)
        }),
    )
    
    def days_until_expiry(self, obj):
        days = obj.days_until_expiry()
        if days is not None:
            if days < 0:
                return f"Vencido hace {abs(days)} días"
            elif days == 0:
                return "Vence hoy"
            else:
                return f"{days} días"
        return "No definido"
    days_until_expiry.short_description = "Días hasta vencimiento"

@admin.register(EmailAccount)
class EmailAccountAdmin(admin.ModelAdmin):
    list_display = ('email_address', 'client', 'quota_mb', 'used_mb', 'usage_percentage', 'is_active')
    list_filter = ('is_active', 'autoresponder_enabled', 'service__service_type')
    search_fields = ('email_address', 'client__username', 'client__email')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('client', 'service', 'email_address', 'password')
        }),
        ('Cuota y Uso', {
            'fields': ('quota_mb', 'used_mb')
        }),
        ('Configuración', {
            'fields': ('is_active', 'forward_to', 'autoresponder_enabled', 'autoresponder_message')
        }),
    )
    
    def usage_percentage(self, obj):
        return f"{obj.usage_percentage():.1f}%"
    usage_percentage.short_description = "% Uso"

@admin.register(ServiceNotification)
class ServiceNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'notification_type', 'is_read', 'sent_via_email', 'created_at')
    list_filter = ('notification_type', 'is_read', 'sent_via_email', 'created_at')
    search_fields = ('title', 'message', 'client__username')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('client', 'service', 'notification_type', 'title', 'message')
        }),
        ('Estado', {
            'fields': ('is_read', 'sent_via_email')
        }),
    )

@admin.register(TwoFactorCode)
class TwoFactorCodeAdmin(admin.ModelAdmin):
    """
    Admin para códigos 2FA
    """
    list_display = ('user', 'code', 'is_used', 'created_at', 'expires_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('code', 'created_at', 'expires_at')

@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """
    Admin para intentos de login
    """
    list_display = ('username_attempted', 'user', 'ip_address', 'success', 'timestamp')
    list_filter = ('success', 'timestamp')
    search_fields = ('username_attempted', 'user__username', 'ip_address')
    readonly_fields = ('timestamp',)

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']

@admin.register(PurchasableService)
class PurchasableServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'home_service', 'is_active', 'is_featured', 'price_monthly', 'price_annual']
    list_filter = ['home_service', 'is_active', 'is_featured', 'requires_domain']
    search_fields = ['name', 'description', 'short_description']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'home_service', 'short_description', 'description')
        }),
        ('Precios', {
            'fields': ('price_monthly', 'price_quarterly', 'price_semiannual', 
                      'price_annual', 'price_biennial', 'price_one_time', 'setup_fee')
        }),
        ('Características', {
            'fields': ('features', 'specifications')
        }),
        ('Configuración', {
            'fields': ('is_active', 'is_featured', 'requires_domain')
        }),
    )

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['created_at']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_items_count', 'get_total', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['service_name', 'unit_price', 'total_price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email', 'billing_email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Información de la Orden', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('Totales', {
            'fields': ('subtotal', 'tax_amount', 'total_amount')
        }),
        ('Información de Facturación', {
            'fields': ('billing_name', 'billing_email', 'billing_address')
        }),
        ('Metadata', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )

@admin.register(WompiConfiguration)
class WompiConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_sandbox', 'is_active', 'created_at']
    list_filter = ['is_sandbox', 'is_active']
    search_fields = ['name']
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'is_active', 'is_sandbox')
        }),
        ('Credenciales', {
            'fields': ('public_key', 'private_key', 'events_secret'),
            'classes': ('collapse',)
        }),
        ('URLs de Redirección', {
            'fields': ('success_url', 'failure_url', 'pending_url'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

@admin.register(WompiTransaction)
class WompiTransactionAdmin(admin.ModelAdmin):
    list_display = ['wompi_id', 'order', 'status', 'payment_method', 'get_amount_in_currency', 'customer_email', 'created_at']
    list_filter = ['status', 'payment_method', 'currency', 'created_at']
    search_fields = ['wompi_id', 'reference', 'customer_email', 'order__order_number']
    readonly_fields = ['wompi_id', 'created_at', 'updated_at', 'paid_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información de la Transacción', {
            'fields': ('order', 'wompi_id', 'reference', 'status')
        }),
        ('Detalles del Pago', {
            'fields': ('amount_in_cents', 'currency', 'payment_method')
        }),
        ('Información del Cliente', {
            'fields': ('customer_email', 'customer_phone')
        }),
        ('URLs', {
            'fields': ('redirect_url',),
            'classes': ('collapse',)
        }),
        ('Respuesta de Wompi', {
            'fields': ('wompi_response',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_amount_in_currency(self, obj):
        return f"${obj.get_amount_in_currency():.2f} {obj.currency}"
    get_amount_in_currency.short_description = "Monto"

@admin.register(WompiWebhookEvent)
class WompiWebhookEventAdmin(admin.ModelAdmin):
    list_display = ['event_id', 'event_type', 'transaction', 'processed', 'created_at']
    list_filter = ['event_type', 'processed', 'created_at']
    search_fields = ['event_id', 'transaction__wompi_id']
    readonly_fields = ['event_id', 'created_at', 'processed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información del Evento', {
            'fields': ('event_id', 'event_type', 'transaction')
        }),
        ('Datos del Evento', {
            'fields': ('data', 'signature'),
            'classes': ('collapse',)
        }),
        ('Procesamiento', {
            'fields': ('processed', 'processed_at', 'error_message')
        }),
        ('Fechas', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(TermsAcceptance)
class TermsAcceptanceAdmin(admin.ModelAdmin):
    list_display = ['user', 'terms_version', 'accepted_at', 'ip_address']
    list_filter = ['terms_version', 'accepted_at']
    search_fields = ['user__username', 'user__email', 'ip_address']
    readonly_fields = ['user', 'terms_version', 'accepted_at', 'ip_address', 'user_agent']
    date_hierarchy = 'accepted_at'
    
    fieldsets = (
        ('Información de Aceptación', {
            'fields': ('user', 'terms_version', 'accepted_at')
        }),
        ('Información Técnica', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """No permitir agregar manualmente registros de aceptación"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir modificar registros de aceptación"""
        return False

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['from_currency', 'to_currency', 'rate', 'source', 'updated_at']
    list_filter = ['from_currency', 'to_currency', 'source', 'updated_at']
    search_fields = ['from_currency', 'to_currency']
    readonly_fields = ['updated_at']
    ordering = ['-updated_at']
    
    fieldsets = (
        ('Información de Cambio', {
            'fields': ('from_currency', 'to_currency', 'rate', 'source')
        }),
        ('Metadatos', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
