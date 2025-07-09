from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from datetime import timedelta

class User(AbstractUser):
    """
    Modelo de usuario personalizado extendiendo AbstractUser
    """
    USER_TYPE_CHOICES = [
        ('admin', 'Administrador'),
        ('client', 'Cliente'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='client')
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True, verbose_name="Empresa")
    address = models.TextField(blank=True, null=True, verbose_name="Dirección")
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ciudad")
    country = models.CharField(max_length=50, blank=True, null=True, verbose_name="País")
    two_factor_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def is_admin(self):
        return self.user_type == 'admin'
    
    def is_client(self):
        return self.user_type == 'client'
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class HostingPlan(models.Model):
    PLAN_TYPES = [
        ('basic', 'Básico'),
        ('standard', 'Estándar'),
        ('premium', 'Premium'),
        ('enterprise', 'Empresarial'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nombre del Plan")
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, verbose_name="Tipo de Plan")
    description = models.TextField(verbose_name="Descripción")
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Mensual")
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Anual")
    
    # Características del plan
    storage_gb = models.IntegerField(verbose_name="Almacenamiento (GB)")
    bandwidth_gb = models.IntegerField(verbose_name="Ancho de Banda (GB)")
    email_accounts = models.IntegerField(verbose_name="Cuentas de Email")
    databases = models.IntegerField(verbose_name="Bases de Datos")
    domains = models.IntegerField(verbose_name="Dominios")
    ssl_included = models.BooleanField(default=True, verbose_name="SSL Incluido")
    backup_daily = models.BooleanField(default=True, verbose_name="Backup Diario")
    support_24_7 = models.BooleanField(default=False, verbose_name="Soporte 24/7")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Plan de Hosting"
        verbose_name_plural = "Planes de Hosting"
    
    def __str__(self):
        return f"{self.name} - ${self.price_monthly}/mes"

class ClientService(models.Model):
    SERVICE_TYPES = [
        ('hosting', 'Hosting'),
        ('domain', 'Dominio'),
        ('email', 'Email'),
        ('ssl', 'Certificado SSL'),
        ('backup', 'Backup'),
        ('maintenance', 'Mantenimiento'),
        ('development', 'Desarrollo Web'),
        ('seo', 'SEO'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('suspended', 'Suspendido'),
        ('expired', 'Vencido'),
        ('cancelled', 'Cancelado'),
    ]
    
    BILLING_CYCLES = [
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('semi_annual', 'Semestral'),
        ('yearly', 'Anual'),
        ('biennial', 'Bienal'),
    ]
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, verbose_name="Tipo de Servicio")
    name = models.CharField(max_length=200, verbose_name="Nombre del Servicio")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    
    # Plan de hosting (si aplica)
    hosting_plan = models.ForeignKey(HostingPlan, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Plan de Hosting")
    
    # Fechas y facturación
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    expiry_date = models.DateField(verbose_name="Fecha de Vencimiento")
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES, verbose_name="Ciclo de Facturación")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    
    # Estado y configuración
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Estado")
    auto_renew = models.BooleanField(default=True, verbose_name="Renovación Automática")
    
    # Detalles técnicos
    domain_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nombre de Dominio")
    server_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP del Servidor")
    cpanel_username = models.CharField(max_length=50, blank=True, null=True, verbose_name="Usuario cPanel")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Servicio de Cliente"
        verbose_name_plural = "Servicios de Clientes"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.client.username} - {self.name}"
    
    def days_until_expiry(self):
        """Días hasta el vencimiento"""
        if self.expiry_date:
            delta = self.expiry_date - timezone.now().date()
            return delta.days
        return None
    
    def is_expiring_soon(self, days=30):
        """Verifica si vence en los próximos X días"""
        days_left = self.days_until_expiry()
        return days_left is not None and 0 <= days_left <= days
    
    def is_expired(self):
        """Verifica si ya venció"""
        return self.expiry_date < timezone.now().date()

class EmailAccount(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_accounts')
    service = models.ForeignKey(ClientService, on_delete=models.CASCADE, related_name='email_accounts')
    
    email_address = models.EmailField(verbose_name="Dirección de Email")
    password = models.CharField(max_length=100, verbose_name="Contraseña")
    quota_mb = models.IntegerField(default=1000, verbose_name="Cuota (MB)")
    used_mb = models.IntegerField(default=0, verbose_name="Espacio Usado (MB)")
    
    # Configuración
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    forward_to = models.EmailField(blank=True, null=True, verbose_name="Reenviar a")
    autoresponder_enabled = models.BooleanField(default=False, verbose_name="Autorespuesta Habilitada")
    autoresponder_message = models.TextField(blank=True, null=True, verbose_name="Mensaje de Autorespuesta")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cuenta de Email"
        verbose_name_plural = "Cuentas de Email"
        unique_together = ['email_address']
    
    def __str__(self):
        return self.email_address
    
    def usage_percentage(self):
        """Porcentaje de uso de la cuota"""
        if self.quota_mb > 0:
            return (self.used_mb / self.quota_mb) * 100
        return 0

class ServiceNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('expiry_warning', 'Aviso de Vencimiento'),
        ('expired', 'Servicio Vencido'),
        ('suspended', 'Servicio Suspendido'),
        ('renewed', 'Servicio Renovado'),
        ('invoice', 'Factura Generada'),
    ]
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    service = models.ForeignKey(ClientService, on_delete=models.CASCADE, related_name='notifications')
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, verbose_name="Tipo de Notificación")
    title = models.CharField(max_length=200, verbose_name="Título")
    message = models.TextField(verbose_name="Mensaje")
    
    is_read = models.BooleanField(default=False, verbose_name="Leído")
    sent_via_email = models.BooleanField(default=False, verbose_name="Enviado por Email")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Notificación de Servicio"
        verbose_name_plural = "Notificaciones de Servicios"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.client.username} - {self.title}"

class TwoFactorCode(models.Model):
    """
    Modelo para códigos de verificación 2FA
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuario'
    )
    
    code = models.CharField(
        max_length=6,
        verbose_name='Código'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    
    is_used = models.BooleanField(
        default=False,
        verbose_name='Código usado'
    )
    
    expires_at = models.DateTimeField(
        verbose_name='Expira en'
    )
    
    class Meta:
        verbose_name = 'Código 2FA'
        verbose_name_plural = 'Códigos 2FA'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.code}"
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def generate_code(self):
        """Generar código de 6 dígitos"""
        return ''.join(random.choices(string.digits, k=6))
    
    def is_valid(self):
        """Verificar si el código es válido"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def send_code(self):
        """Enviar código por email"""
        try:
            subject = 'Código de verificación - megadominio.co'
            message = f"""
            Hola {self.user.first_name or self.user.username},
            
            Tu código de verificación es: {self.code}
            
            Este código expira en 10 minutos.
            
            Si no solicitaste este código, ignora este mensaje.
            
            Saludos,
            Equipo de megadominio.co
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.user.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error enviando email: {e}")
            return False


class LoginAttempt(models.Model):
    """
    Modelo para rastrear intentos de login
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Usuario'
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name='Dirección IP'
    )
    
    username_attempted = models.CharField(
        max_length=150,
        verbose_name='Usuario intentado'
    )
    
    success = models.BooleanField(
        default=False,
        verbose_name='Exitoso'
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y hora'
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    
    class Meta:
        verbose_name = 'Intento de login'
        verbose_name_plural = 'Intentos de login'
        ordering = ['-timestamp']
    
    def __str__(self):
        status = 'Exitoso' if self.success else 'Fallido'
        return f"{self.username_attempted} - {status} - {self.timestamp}"

class ServiceCategory(models.Model):
    """Categorías de servicios"""
    name = models.CharField(max_length=100, verbose_name="Nombre")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(verbose_name="Descripción")
    icon = models.CharField(max_length=50, default="fas fa-cog", verbose_name="Icono FontAwesome")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    order = models.IntegerField(default=0, verbose_name="Orden")
    
    class Meta:
        verbose_name = "Categoría de Servicio"
        verbose_name_plural = "Categorías de Servicios"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class PurchasableService(models.Model):
    """Servicios que los clientes pueden comprar"""
    BILLING_CYCLES = [
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('semiannual', 'Semestral'),
        ('annual', 'Anual'),
        ('biennial', 'Bienal'),
        ('one_time', 'Pago Único'),
    ]
    
    # Cambiar la relación de ServiceCategory a Servicio del home
    home_service = models.ForeignKey('servicios.Servicio', on_delete=models.CASCADE, verbose_name="Servicio del Home", related_name="purchasable_services")
    name = models.CharField(max_length=200, verbose_name="Nombre del Servicio")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(verbose_name="Descripción")
    short_description = models.CharField(max_length=255, verbose_name="Descripción Corta")
    
    # Precios
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio Mensual")
    price_quarterly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio Trimestral")
    price_semiannual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio Semestral")
    price_annual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio Anual")
    price_biennial = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio Bienal")
    price_one_time = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Precio Único")
    
    # Características
    features = models.JSONField(default=list, verbose_name="Características", help_text="Lista de características del servicio")
    specifications = models.JSONField(default=dict, verbose_name="Especificaciones", help_text="Especificaciones técnicas")
    
    # Configuración
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_featured = models.BooleanField(default=False, verbose_name="Destacado")
    requires_domain = models.BooleanField(default=False, verbose_name="Requiere Dominio")
    setup_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Costo de Configuración")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    class Meta:
        verbose_name = "Servicio Comprable"
        verbose_name_plural = "Servicios Comprables"
        ordering = ['-is_featured', 'home_service', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.home_service.nombre})"
    
    def get_price(self, billing_cycle):
        """Obtiene el precio para un ciclo de facturación específico"""
        price_field = f'price_{billing_cycle}'
        return getattr(self, price_field, None)
    
    def get_available_billing_cycles(self):
        """Obtiene los ciclos de facturación disponibles"""
        cycles = []
        for cycle, label in self.BILLING_CYCLES:
            if self.get_price(cycle):
                cycles.append((cycle, label))
        return cycles

class Cart(models.Model):
    """Carrito de compras"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    class Meta:
        verbose_name = "Carrito"
        verbose_name_plural = "Carritos"
    
    def __str__(self):
        if self.user:
            return f"Carrito de {self.user.username}"
        else:
            return f"Carrito anónimo (ID: {self.id})"
    
    def get_total(self):
        """Calcula el total del carrito"""
        return sum(item.get_total() for item in self.items.all())
    
    def get_items_count(self):
        """Obtiene el número de items en el carrito"""
        return self.items.count()

class CartItem(models.Model):
    """Items del carrito de compras"""
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE, verbose_name="Carrito")
    service = models.ForeignKey(PurchasableService, on_delete=models.CASCADE, verbose_name="Servicio")
    billing_cycle = models.CharField(max_length=20, choices=PurchasableService.BILLING_CYCLES, verbose_name="Ciclo de Facturación")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    domain_name = models.CharField(max_length=255, blank=True, verbose_name="Nombre de Dominio")
    notes = models.TextField(blank=True, verbose_name="Notas")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Item del Carrito"
        verbose_name_plural = "Items del Carrito"
        unique_together = ['cart', 'service', 'billing_cycle']
    
    def __str__(self):
        return f"{self.service.name} - {self.get_billing_cycle_display()}"
    
    def get_unit_price(self):
        """Obtiene el precio unitario"""
        return self.service.get_price(self.billing_cycle) or 0
    
    def get_total(self):
        """Calcula el total del item"""
        return self.get_unit_price() * self.quantity

class Order(models.Model):
    """Órdenes de compra"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
        ('failed', 'Fallida'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario", null=True, blank=True)
    order_number = models.CharField(max_length=20, unique=True, verbose_name="Número de Orden")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    
    # Totales
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Impuestos")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total")
    
    # Información de facturación
    billing_name = models.CharField(max_length=200, verbose_name="Nombre de Facturación")
    billing_email = models.EmailField(verbose_name="Email de Facturación")
    billing_address = models.TextField(verbose_name="Dirección de Facturación")
    
    # Metadata
    notes = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
        ordering = ['-created_at']
    
    def __str__(self):
        if self.user:
            return f"Orden #{self.order_number} - {self.user.username}"
        else:
            return f"Orden #{self.order_number} - Usuario anónimo"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Genera un número de orden único"""
        import random
        import string
        while True:
            number = ''.join(random.choices(string.digits, k=8))
            if not Order.objects.filter(order_number=number).exists():
                return number

class OrderItem(models.Model):
    """Items de una orden"""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Orden")
    service = models.ForeignKey(PurchasableService, on_delete=models.CASCADE, verbose_name="Servicio")
    service_name = models.CharField(max_length=200, verbose_name="Nombre del Servicio")
    billing_cycle = models.CharField(max_length=20, choices=PurchasableService.BILLING_CYCLES, verbose_name="Ciclo de Facturación")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Total")
    domain_name = models.CharField(max_length=255, blank=True, verbose_name="Nombre de Dominio")
    notes = models.TextField(blank=True, verbose_name="Notas")
    
    class Meta:
        verbose_name = "Item de Orden"
        verbose_name_plural = "Items de Orden"
    
    def __str__(self):
        return f"{self.service_name} - {self.get_billing_cycle_display()}"

class WompiConfiguration(models.Model):
    """Configuración de Wompi para pagos"""
    name = models.CharField(max_length=100, verbose_name="Nombre de Configuración", default="Wompi Principal")
    public_key = models.CharField(max_length=200, verbose_name="Clave Pública")
    private_key = models.CharField(max_length=200, verbose_name="Clave Privada")
    events_secret = models.CharField(max_length=200, verbose_name="Secret de Eventos", blank=True)
    is_sandbox = models.BooleanField(default=True, verbose_name="Modo Sandbox")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    # URLs de configuración
    success_url = models.URLField(verbose_name="URL de Éxito", blank=True)
    failure_url = models.URLField(verbose_name="URL de Fallo", blank=True)
    pending_url = models.URLField(verbose_name="URL de Pendiente", blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    class Meta:
        verbose_name = "Configuración de Wompi"
        verbose_name_plural = "Configuraciones de Wompi"
    
    def __str__(self):
        env = "Sandbox" if self.is_sandbox else "Producción"
        return f"{self.name} ({env})"
    
    def get_base_url(self):
        """Obtiene la URL base según el ambiente"""
        if self.is_sandbox:
            return "https://sandbox.wompi.co/v1"
        return "https://production.wompi.co/v1"

class WompiTransaction(models.Model):
    """Transacciones de Wompi"""
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('APPROVED', 'Aprobada'),
        ('DECLINED', 'Rechazada'),
        ('VOIDED', 'Anulada'),
        ('ERROR', 'Error'),
    ]
    
    PAYMENT_METHODS = [
        ('CARD', 'Tarjeta de Crédito/Débito'),
        ('NEQUI', 'Nequi'),
        ('PSE', 'PSE'),
        ('BANCOLOMBIA_TRANSFER', 'Transferencia Bancolombia'),
        ('BANCOLOMBIA_COLLECT', 'Botón Bancolombia'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name="Orden", related_name="wompi_transaction")
    wompi_id = models.CharField(max_length=100, unique=True, verbose_name="ID de Wompi")
    reference = models.CharField(max_length=100, verbose_name="Referencia")
    
    # Información del pago
    amount_in_cents = models.BigIntegerField(verbose_name="Monto en Centavos")
    currency = models.CharField(max_length=3, default='COP', verbose_name="Moneda")
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS, verbose_name="Método de Pago")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Estado")
    
    # Información del cliente
    customer_email = models.EmailField(verbose_name="Email del Cliente")
    customer_phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono del Cliente")
    
    # URLs de redirección
    redirect_url = models.URLField(blank=True, verbose_name="URL de Redirección")
    
    # Metadatos de respuesta de Wompi
    wompi_response = models.JSONField(default=dict, verbose_name="Respuesta de Wompi")
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Pago")
    
    class Meta:
        verbose_name = "Transacción de Wompi"
        verbose_name_plural = "Transacciones de Wompi"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Transacción {self.wompi_id} - {self.get_status_display()}"
    
    def is_successful(self):
        """Verifica si la transacción fue exitosa"""
        return self.status == 'APPROVED'
    
    def get_amount_in_currency(self):
        """Obtiene el monto en la moneda original"""
        return self.amount_in_cents / 100

class WompiWebhookEvent(models.Model):
    """Eventos de webhook de Wompi"""
    EVENT_TYPES = [
        ('transaction.updated', 'Transacción Actualizada'),
        ('payment_link.paid', 'Enlace de Pago Pagado'),
        ('payment_source.created', 'Fuente de Pago Creada'),
    ]
    
    event_id = models.CharField(max_length=100, unique=True, verbose_name="ID del Evento")
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, verbose_name="Tipo de Evento")
    
    # Datos del evento
    data = models.JSONField(verbose_name="Datos del Evento")
    signature = models.TextField(verbose_name="Firma del Evento")
    
    # Procesamiento
    processed = models.BooleanField(default=False, verbose_name="Procesado")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Procesamiento")
    error_message = models.TextField(blank=True, verbose_name="Mensaje de Error")
    
    # Relación con transacción (si aplica)
    transaction = models.ForeignKey(WompiTransaction, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Transacción")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Evento de Webhook Wompi"
        verbose_name_plural = "Eventos de Webhook Wompi"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Evento {self.event_type} - {self.event_id}"

class TermsAcceptance(models.Model):
    """Registro de aceptación de términos y condiciones"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    terms_version = models.CharField(max_length=10, default="1.0", verbose_name="Versión de Términos")
    accepted_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Aceptación")
    ip_address = models.GenericIPAddressField(verbose_name="Dirección IP")
    user_agent = models.TextField(verbose_name="User Agent")
    
    class Meta:
        verbose_name = "Aceptación de Términos"
        verbose_name_plural = "Aceptaciones de Términos"
        ordering = ['-accepted_at']
        unique_together = ['user', 'terms_version']
    
    def __str__(self):
        return f"{self.user.username} - v{self.terms_version} - {self.accepted_at.strftime('%Y-%m-%d %H:%M')}"

class ExchangeRate(models.Model):
    """Tasas de cambio para conversión de monedas"""
    from_currency = models.CharField(max_length=3, verbose_name="Moneda Origen")
    to_currency = models.CharField(max_length=3, verbose_name="Moneda Destino")
    rate = models.DecimalField(max_digits=15, decimal_places=6, verbose_name="Tasa de Cambio")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    source = models.CharField(max_length=50, default="exchangerate-api", verbose_name="Fuente")
    
    class Meta:
        verbose_name = "Tasa de Cambio"
        verbose_name_plural = "Tasas de Cambio"
        unique_together = ['from_currency', 'to_currency']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.from_currency} -> {self.to_currency}: {self.rate}"
    
    @classmethod
    def get_rate(cls, from_currency, to_currency, hours=24):
        """Obtiene la tasa de cambio entre dos monedas con cache configurable"""
        if from_currency == to_currency:
            return 1.0
        
        try:
            exchange_rate = cls.objects.get(
                from_currency=from_currency,
                to_currency=to_currency
            )
            # Verificar si la tasa es reciente (por defecto 24 horas para optimizar API)
            if timezone.now() - exchange_rate.updated_at < timedelta(hours=hours):
                return exchange_rate.rate
        except cls.DoesNotExist:
            pass
        
        # Si no existe o es muy antigua, usar tasa por defecto
        if from_currency == 'USD' and to_currency == 'COP':
            return 4000  # Tasa por defecto
        elif from_currency == 'COP' and to_currency == 'USD':
            return 0.00025  # Tasa por defecto inversa
        
        return 1.0
