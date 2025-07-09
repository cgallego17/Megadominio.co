from django.contrib import admin
from .models import Visita, EstadisticaDiaria, ContactoFormulario, PaginaVisitada, AnalyticsResumen, Cliente, Venta, DetalleVenta

# Register your models here.

@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'country', 'city', 'page_visited', 'timestamp']
    list_filter = ['timestamp', 'country', 'referrer_source']
    search_fields = ['ip_address', 'country', 'city']
    readonly_fields = ['timestamp']

@admin.register(EstadisticaDiaria)
class EstadisticaDiariaAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'visitas_totales', 'visitas_unicas', 'paginas_vistas']
    list_filter = ['fecha']
    readonly_fields = ['fecha']

@admin.register(ContactoFormulario)
class ContactoFormularioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'servicio_interes', 'fecha_contacto', 'atendido']
    list_filter = ['atendido', 'fecha_contacto', 'servicio_interes']
    search_fields = ['nombre', 'email', 'mensaje']
    readonly_fields = ['fecha_contacto']

@admin.register(PaginaVisitada)
class PaginaVisitadaAdmin(admin.ModelAdmin):
    list_display = ['path', 'nombre_amigable', 'visitas_totales', 'ultima_visita', 'activo']
    list_filter = ['activo', 'ultima_visita']
    search_fields = ['path', 'nombre_amigable']

@admin.register(AnalyticsResumen)
class AnalyticsResumenAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'total_visitas', 'visitantes_unicos', 'paginas_vistas', 'tiempo_promedio_sitio']
    list_filter = ['fecha']
    readonly_fields = ['fecha']

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    fields = ['servicio', 'descripcion', 'cantidad', 'precio_unitario', 'subtotal']

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'empresa', 'estado', 'total_ventas', 'valor_total_ventas', 'fecha_registro']
    list_filter = ['estado', 'fecha_registro']
    search_fields = ['nombre', 'email', 'empresa']
    readonly_fields = ['fecha_registro', 'ultima_actividad', 'total_ventas', 'valor_total_ventas']
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'email', 'telefono')
        }),
        ('Información Empresarial', {
            'fields': ('empresa', 'direccion')
        }),
        ('Estado y Seguimiento', {
            'fields': ('estado', 'notas')
        }),
        ('Estadísticas', {
            'fields': ('total_ventas', 'valor_total_ventas', 'fecha_registro', 'ultima_actividad'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['numero_factura', 'cliente', 'fecha_venta', 'estado', 'valor_total', 'metodo_pago']
    list_filter = ['estado', 'fecha_venta', 'metodo_pago']
    search_fields = ['numero_factura', 'cliente__nombre', 'cliente__email']
    readonly_fields = ['fecha_venta']
    inlines = [DetalleVentaInline]
    fieldsets = (
        ('Información de la Venta', {
            'fields': ('numero_factura', 'cliente', 'estado', 'fecha_venta')
        }),
        ('Detalles de Pago', {
            'fields': ('metodo_pago', 'subtotal', 'impuestos', 'descuento', 'valor_total', 'fecha_pago')
        }),
        ('Información Adicional', {
            'fields': ('descripcion', 'notas')
        }),
    )

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ['venta', 'servicio', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['venta__fecha_venta']
    search_fields = ['servicio', 'venta__numero_factura']
