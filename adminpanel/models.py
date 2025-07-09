from django.db import models
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta
import requests
import json

# Create your models here.

# No se requieren modelos aquí por ahora.

class Visita(models.Model):
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    referrer = models.URLField(blank=True, null=True)
    referrer_source = models.CharField(max_length=50, default='directo')
    page_visited = models.CharField(max_length=255, default='/')
    
    # Información geográfica
    country = models.CharField(max_length=100, blank=True, null=True)
    country_code = models.CharField(max_length=3, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['referrer_source']),
            models.Index(fields=['page_visited']),
            models.Index(fields=['country_code']),
        ]
    
    def __str__(self):
        return f"{self.ip_address} - {self.country or 'Unknown'} - {self.page_visited} - {self.timestamp}"

    @staticmethod
    def get_geo_info(ip_address):
        """Obtener información geográfica de una IP"""
        try:
            # Evitar consultas para IPs locales
            if ip_address in ['127.0.0.1', '::1'] or ip_address.startswith('192.168.') or ip_address.startswith('10.') or ip_address.startswith('172.'):
                return {
                    'country': 'Local',
                    'country_code': 'LC',
                    'city': 'Local',
                    'region': 'Local Network'
                }
            
            # Usar API gratuita para obtener geolocalización
            response = requests.get(f'http://ipapi.co/{ip_address}/json/', timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'country': data.get('country_name', ''),
                    'country_code': data.get('country_code', ''),
                    'city': data.get('city', ''),
                    'region': data.get('region', '')
                }
            else:
                return None
                
        except Exception as e:
            # Si hay error, no bloquear la creación de la visita
            return None

class EstadisticaDiaria(models.Model):
    fecha = models.DateField(unique=True)
    visitas_totales = models.IntegerField(default=0)
    visitas_unicas = models.IntegerField(default=0)
    paginas_vistas = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Estadística Diaria'
        verbose_name_plural = 'Estadísticas Diarias'
    
    def __str__(self):
        return f"Estadísticas {self.fecha}"
    
    @classmethod
    def obtener_datos_grafico(cls, dias=7):
        """Obtiene datos para el gráfico de visitas"""
        fechas = []
        visitas = []
        visitas_unicas = []
        
        for i in range(dias):
            fecha = timezone.now().date() - timedelta(days=dias-1-i)
            fechas.append(fecha.strftime('%d/%m'))
            
            try:
                stat = cls.objects.get(fecha=fecha)
                visitas.append(stat.visitas_totales)
                visitas_unicas.append(stat.visitas_unicas)
            except cls.DoesNotExist:
                visitas.append(0)
                visitas_unicas.append(0)
        
        return fechas, visitas, visitas_unicas

    @classmethod
    def obtener_fuentes_trafico(cls, dias=30):
        """Obtiene datos de fuentes de tráfico"""
        fecha_inicio = timezone.now().date() - timedelta(days=dias)
        
        fuentes = Visita.objects.filter(
            timestamp__date__gte=fecha_inicio
        ).values('referrer_source').annotate(
            total=Count('id')
        ).order_by('-total')[:10]
        
        labels = []
        datos = []
        colores = [
            '#ff6600', '#28a745', '#17a2b8', '#6f42c1', '#ffc107',
            '#dc3545', '#20c997', '#fd7e14', '#e83e8c', '#6c757d'
        ]
        
        for i, fuente in enumerate(fuentes):
            source = fuente['referrer_source']
            
            # Nombres amigables para las fuentes
            nombres_fuentes = {
                'directo': 'Directo',
                'busqueda_google': 'Google',
                'busqueda_bing': 'Bing',
                'social_facebook': 'Facebook',
                'social_instagram': 'Instagram',
                'social_twitter': 'Twitter',
                'social_linkedin': 'LinkedIn',
                'social_youtube': 'YouTube',
                'social_whatsapp': 'WhatsApp',
                'social_telegram': 'Telegram',
                'email': 'Email',
                'referral': 'Otros sitios'
            }
            
            nombre_amigable = nombres_fuentes.get(source, source.title())
            labels.append(nombre_amigable)
            datos.append(fuente['total'])
        
        return labels, datos, colores[:len(labels)]

    @classmethod
    def obtener_paginas_populares(cls, dias=30):
        """Obtiene páginas más visitadas"""
        fecha_inicio = timezone.now().date() - timedelta(days=dias)
        
        paginas = Visita.objects.filter(
            timestamp__date__gte=fecha_inicio
        ).values('page_visited').annotate(
            total=Count('id')
        ).order_by('-total')[:10]
        
        # Nombres amigables para las páginas
        nombres_paginas = {
            '/': 'Inicio',
            '/servicios/': 'Servicios',
            '/proyectos/': 'Proyectos',
            '/contacto/': 'Contacto',
            '/sobre-nosotros/': 'Sobre Nosotros',
            '/blog/': 'Blog'
        }
        
        data = []
        for pagina in paginas:
            path = pagina['page_visited']
            nombre = nombres_paginas.get(path, path)
            data.append({
                'path': path,
                'nombre': nombre,
                'visitas': pagina['total']
            })
        
        return data

    @classmethod
    def obtener_paises_visitantes(cls, dias=30):
        """Obtiene países de visitantes"""
        fecha_inicio = timezone.now().date() - timedelta(days=dias)
        
        paises = Visita.objects.filter(
            timestamp__date__gte=fecha_inicio,
            country__isnull=False
        ).exclude(country='').values('country', 'country_code').annotate(
            total=Count('id')
        ).order_by('-total')[:15]
        
        data = []
        colores = [
            '#ff6600', '#28a745', '#17a2b8', '#6f42c1', '#ffc107',
            '#dc3545', '#20c997', '#fd7e14', '#e83e8c', '#6c757d',
            '#007bff', '#6610f2', '#e91e63', '#00bcd4', '#795548'
        ]
        
        for i, pais in enumerate(paises):
            data.append({
                'pais': pais['country'],
                'codigo': pais['country_code'],
                'visitas': pais['total'],
                'color': colores[i % len(colores)]
            })
        
        return data

    @classmethod
    def obtener_estadisticas_geograficas(cls, dias=30):
        """Obtiene estadísticas geográficas resumidas"""
        fecha_inicio = timezone.now().date() - timedelta(days=dias)
        
        # Total de países únicos
        total_paises = Visita.objects.filter(
            timestamp__date__gte=fecha_inicio,
            country__isnull=False
        ).exclude(country='').values('country').distinct().count()
        
        # País con más visitas
        pais_top = Visita.objects.filter(
            timestamp__date__gte=fecha_inicio,
            country__isnull=False
        ).exclude(country='').values('country').annotate(
            total=Count('id')
        ).order_by('-total').first()
        
        # Total de ciudades únicas
        total_ciudades = Visita.objects.filter(
            timestamp__date__gte=fecha_inicio,
            city__isnull=False
        ).exclude(city='').values('city').distinct().count()
        
        return {
            'total_paises': total_paises,
            'pais_top': pais_top['country'] if pais_top else 'Sin datos',
            'pais_top_visitas': pais_top['total'] if pais_top else 0,
            'total_ciudades': total_ciudades
        }

class ContactoFormulario(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)
    servicio_interes = models.CharField(max_length=100, blank=True)
    mensaje = models.TextField()
    fecha_contacto = models.DateTimeField(auto_now_add=True)
    atendido = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-fecha_contacto']
        verbose_name = 'Contacto'
        verbose_name_plural = 'Contactos'
    
    def __str__(self):
        return f"{self.nombre} - {self.servicio_interes}"

class PaginaVisitada(models.Model):
    """Modelo para trackear páginas específicas"""
    path = models.CharField(max_length=255, unique=True)
    nombre_amigable = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    visitas_totales = models.IntegerField(default=0)
    ultima_visita = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-visitas_totales']
        verbose_name = 'Página Visitada'
        verbose_name_plural = 'Páginas Visitadas'
    
    def __str__(self):
        return f"{self.nombre_amigable} ({self.visitas_totales} visitas)"

class AnalyticsResumen(models.Model):
    """Modelo para resúmenes de analytics"""
    fecha = models.DateField(auto_now_add=True)
    total_visitas = models.IntegerField(default=0)
    visitantes_unicos = models.IntegerField(default=0)
    paginas_vistas = models.IntegerField(default=0)
    tiempo_promedio_sitio = models.FloatField(default=0.0)  # En minutos
    tasa_rebote = models.FloatField(default=0.0)  # Porcentaje
    fuente_principal = models.CharField(max_length=50, blank=True)
    pagina_mas_visitada = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Resumen Analytics'
        verbose_name_plural = 'Resúmenes Analytics'
    
    def __str__(self):
        return f"Resumen Analytics {self.fecha}"

class Cliente(models.Model):
    """Modelo para gestionar clientes"""
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('prospecto', 'Prospecto'),
        ('vip', 'VIP'),
    ]
    
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    empresa = models.CharField(max_length=100, blank=True)
    direccion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='prospecto')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultima_actividad = models.DateTimeField(auto_now=True)
    notas = models.TextField(blank=True)
    valor_total_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_ventas = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-fecha_registro']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
    
    def __str__(self):
        return f"{self.nombre} - {self.email}"
    
    def actualizar_estadisticas(self):
        """Actualizar estadísticas del cliente basadas en sus ventas"""
        ventas = self.venta_set.all()
        self.total_ventas = ventas.count()
        self.valor_total_ventas = sum(venta.valor_total for venta in ventas)
        self.save(update_fields=['total_ventas', 'valor_total_ventas'])

class Venta(models.Model):
    """Modelo para gestionar ventas"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('reembolsada', 'Reembolsada'),
    ]
    
    METODO_PAGO_CHOICES = [
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('transferencia', 'Transferencia Bancaria'),
        ('paypal', 'PayPal'),
        ('efectivo', 'Efectivo'),
        ('crypto', 'Criptomonedas'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    numero_factura = models.CharField(max_length=20, unique=True)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True)
    notas = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-fecha_venta']
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
    
    def __str__(self):
        return f"Venta {self.numero_factura} - {self.cliente.nombre}"
    
    def save(self, *args, **kwargs):
        # Calcular valor total si no está establecido
        if not self.valor_total:
            self.valor_total = self.subtotal + self.impuestos - self.descuento
        super().save(*args, **kwargs)
        
        # Actualizar estadísticas del cliente
        self.cliente.actualizar_estadisticas()

class DetalleVenta(models.Model):
    """Modelo para los detalles de cada venta"""
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    servicio = models.CharField(max_length=100)
    descripcion = models.TextField()
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'
    
    def __str__(self):
        return f"{self.servicio} - {self.venta.numero_factura}"
    
    def save(self, *args, **kwargs):
        # Calcular subtotal si no está establecido
        if not self.subtotal:
            self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
