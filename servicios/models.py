from django.db import models
from django.urls import reverse
from django.utils.text import slugify
import re

# Create your models here.

class Servicio(models.Model):
    ICONO_CHOICES = [
        ('fas fa-globe', '🌐 Páginas Web'),
        ('fas fa-code', '💻 Desarrollo'),
        ('fas fa-shopping-cart', '🛒 Ecommerce'),
        ('fas fa-envelope', '📧 Correos'),
        ('fas fa-server', '🖥️ Hosting'),
        ('fas fa-link', '🔗 Dominios'),
        ('fas fa-lock', '🔒 SSL'),
        ('fas fa-shield-alt', '🛡️ Seguridad'),
        ('fab fa-wordpress', '🟦 WordPress'),
        ('fab fa-woocommerce', '🟪 WooCommerce'),
        ('fas fa-cogs', '⚙️ Servicios'),
        ('fas fa-mobile-alt', '📱 Apps Móviles'),
        ('fas fa-database', '🗄️ Base de Datos'),
        ('fas fa-cloud', '☁️ Cloud'),
        ('fas fa-chart-line', '📊 Analytics'),
        ('fas fa-paint-brush', '🎨 Diseño'),
        ('fas fa-rocket', '🚀 Optimización'),
        ('fas fa-headset', '🎧 Soporte'),
        ('fas fa-search', '🔍 SEO'),
        ('fas fa-tools', '🔧 Mantenimiento'),
        ('fas fa-bullhorn', '📢 Marketing'),
    ]
    
    nombre = models.CharField(max_length=100)
    descripcion_corta = models.TextField(
        max_length=300,
        blank=True,
        help_text='Descripción corta para mostrar en el home (máximo 300 caracteres)'
    )
    descripcion = models.TextField(
        help_text='Descripción completa optimizada para SEO (para página de detalle)'
    )
    precio = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text='Precio del servicio (opcional). Ej: "$999 pesos", "Desde $500", "Cotización"'
    )
    icono = models.CharField(
        max_length=100, 
        choices=ICONO_CHOICES,
        blank=True, 
        help_text='Selecciona un icono de FontAwesome o deja vacío para usar imagen personalizada'
    )
    imagen = models.ImageField(
        upload_to='servicios/', 
        blank=True, 
        null=True,
        help_text='Imagen personalizada (opcional). Si se selecciona, se usará en lugar del icono de FontAwesome'
    )

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def get_slug(self):
        """Genera un slug SEO-friendly a partir del nombre del servicio"""
        # Convertir caracteres especiales y espacios
        slug_map = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'ñ': 'n', 'ü': 'u', 'ç': 'c',
            'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u',
            'Ñ': 'n', 'Ü': 'u', 'Ç': 'c',
            '&': 'y', '+': 'plus', '@': 'at'
        }
        
        nombre_clean = self.nombre
        for char, replacement in slug_map.items():
            nombre_clean = nombre_clean.replace(char, replacement)
        
        # Usar slugify de Django para el resto
        slug = slugify(nombre_clean)
        
        # Limpiezas adicionales específicas para servicios
        slug = slug.replace('y-antivirus-para-empresas', '-antivirus-empresas')
        slug = slug.replace('desarrollo-de-', '')
        slug = slug.replace('asesorias-tecnologicas', 'consultoria-tecnologica')
        slug = slug.replace('redes-y-servidores', 'infraestructura-it')
        slug = slug.replace('soluciones-iot', 'iot-empresarial')
        
        # Corregir dobles guiones
        while '--' in slug:
            slug = slug.replace('--', '-')
        
        return slug

    def get_absolute_url(self):
        """Devuelve la URL absoluta del servicio usando el slug"""
        return reverse('services:servicio_detail', kwargs={'servicio_slug': self.get_slug()})

    def get_icono_display_html(self):
        """Devuelve el HTML para mostrar el icono en el admin"""
        if self.imagen:
            return f'<img src="{self.imagen.url}" style="width: 20px; height: 20px;" alt="{self.nombre}">'
        elif self.icono:
            return f'<i class="{self.icono}" style="color: #ff6600;"></i>'
        else:
            return '<i class="fas fa-cogs" style="color: #ccc;"></i>'
    get_icono_display_html.short_description = 'Icono'
    
    def get_descripcion_para_home(self):
        """Devuelve la descripción apropiada para el home"""
        if self.descripcion_corta:
            return self.descripcion_corta
        else:
            # Si no hay descripción corta, tomar los primeros 250 caracteres de la descripción completa
            if len(self.descripcion) > 250:
                return self.descripcion[:250] + "..."
            return self.descripcion

    @staticmethod
    def get_by_slug(slug):
        """Busca un servicio por su slug"""
        # Mapear slugs conocidos a nombres exactos
        slug_to_name = {
            'desarrollo-web': 'Desarrollo Web',
            'hosting': 'Hosting',
            'dominios': 'Dominios',
            'ssl-antivirus-empresas': 'SSL y Antivirus para Empresas',
            'correo-empresarial': 'Correo Empresarial',
            'ecommerce': 'Ecommerce',
            'software': 'Desarrollo de Software',
            'consultoria-tecnologica': 'Asesorías Tecnológicas',
            'infraestructura-it': 'Redes y Servidores',
            'iot-empresarial': 'Soluciones IoT',
            'wordpress': 'WordPress',
            'aplicaciones-moviles': 'Aplicaciones Móviles',
            'mantenimiento-web': 'Mantenimiento Web',
            'optimizacion-web-y-seo': 'Optimización Web y SEO'
        }
        
        # Primero intentar con mapeo directo
        if slug in slug_to_name:
            try:
                return Servicio.objects.get(nombre=slug_to_name[slug])
            except Servicio.DoesNotExist:
                pass
        
        # Si no encuentra por mapeo directo, buscar por nombre similar
        # Convertir slug a nombre aproximado
        nombre_approx = slug.replace('-', ' ').title()
        
        # Buscar coincidencias flexibles
        servicios = Servicio.objects.all()
        for servicio in servicios:
            if servicio.get_slug() == slug:
                return servicio
        
        # Si no encuentra nada, lanzar excepción
        raise Servicio.DoesNotExist(f"No se encontró servicio con slug: {slug}")
