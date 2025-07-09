#!/usr/bin/env python
"""
Script para agregar nuevos servicios a Megadominio.co
Ejecutar con: python add_new_services.py
"""

import os
import sys
import django
from django.utils.text import slugify

# Add project path
sys.path.append('/c:/Users/crisn/Documents/Megadominio.co')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'megadominio.settings')
django.setup()

from servicios.models import Servicio
from accounts.models import ServiceCategory, PurchasableService

def create_ssl_antivirus_service():
    # Create or get SSL & Antivirus category
    ssl_category, created = ServiceCategory.objects.get_or_create(
        name="SSL & Antivirus",
        defaults={
            'slug': 'ssl-antivirus',
            'description': "Certificados SSL y soluciones antivirus para empresas",
            'icon': 'fas fa-shield-alt'
        }
    )
    
    # Create SSL & Antivirus service
    ssl_service = Servicio.objects.create(
        nombre="SSL y Antivirus para Empresas",
        descripcion="Protección completa con certificados SSL y soluciones antivirus empresariales para mantener tu negocio seguro",
        precio="Desde $29.99",
        icono="fas fa-shield-alt"
    )
    
    # Create purchasable service plans for SSL & Antivirus
    ssl_plans = [
        {
            'name': 'SSL Básico',
            'price_annual': 29.99,
            'description': 'Certificado SSL básico para un dominio',
            'short_description': 'Certificado SSL básico para un dominio',
            'features': [
                'Certificado SSL DV (Domain Validated)',
                'Protección para 1 dominio',
                'Cifrado de 256 bits',
                'Sello de confianza',
                'Soporte 24/7',
                'Instalación gratuita',
                'Garantía de $10,000 USD'
            ]
        },
        {
            'name': 'SSL Profesional + Antivirus',
            'price_annual': 89.99,
            'description': 'SSL avanzado con protección antivirus básica',
            'short_description': 'SSL avanzado con protección antivirus básica',
            'features': [
                'Certificado SSL OV (Organization Validated)',
                'Protección para múltiples subdominios',
                'Antivirus básico para 5 dispositivos',
                'Firewall personal',
                'Monitoreo de amenazas',
                'Actualizaciones automáticas',
                'Soporte prioritario 24/7',
                'Garantía de $100,000 USD'
            ]
        },
        {
            'name': 'SSL Enterprise + Antivirus Pro',
            'price_annual': 199.99,
            'description': 'Solución completa SSL y antivirus para empresas',
            'short_description': 'Solución completa SSL y antivirus para empresas',
            'features': [
                'Certificado SSL EV (Extended Validation)',
                'Certificado comodín (wildcard)',
                'Antivirus empresarial para 25 dispositivos',
                'Firewall empresarial avanzado',
                'Protección contra ransomware',
                'Análisis de vulnerabilidades',
                'Dashboard de seguridad',
                'Gestión centralizada',
                'Soporte dedicado 24/7',
                'Garantía de $1,000,000 USD'
            ]
        }
    ]
    
    for plan in ssl_plans:
        slug = slugify(plan['name'])
        # Check if slug already exists
        counter = 1
        original_slug = slug
        while PurchasableService.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1
            
        PurchasableService.objects.create(
            home_service=ssl_service,
            name=plan['name'],
            slug=slug,
            description=plan['description'],
            short_description=plan['short_description'],
            price_annual=plan['price_annual'],
            features=plan['features'],
            is_active=True,
            is_featured=False
        )
    
    print(f"✓ Servicio SSL y Antivirus creado con {len(ssl_plans)} planes")
    return ssl_service

def create_all_new_services():
    """Create all new services including SSL & Antivirus"""
    
    # Create SSL & Antivirus service
    ssl_service = create_ssl_antivirus_service()
    
    # Create Software Development service
    software_category, created = ServiceCategory.objects.get_or_create(
        name="Desarrollo de Software",
        defaults={
            'description': "Desarrollo de aplicaciones y software personalizado"
        }
    )
    
    software_service = Servicio.objects.create(
        nombre="Desarrollo de Software Personalizado",
        descripcion="Creamos aplicaciones y software a medida para tu empresa, desde aplicaciones móviles hasta sistemas ERP",
        image_url="https://via.placeholder.com/400x300?text=Software+Development",
        category=software_category,
        is_active=True
    )
    
    # Create purchasable service plans for Software Development
    software_plans = [
        {
            'nombre': 'Aplicación Móvil Básica',
            'precio_usd': 2999.99,
            'descripcion': 'Aplicación móvil simple para iOS o Android',
            'features': [
                'Desarrollo para iOS o Android',
                'Hasta 5 pantallas',
                'Diseño UI/UX básico',
                'Integración con API básica',
                'Documentación técnica',
                'Soporte post-lanzamiento (30 días)',
                'Entrega en 8-12 semanas'
            ]
        },
        {
            'nombre': 'Sistema Web Personalizado',
            'precio_usd': 4999.99,
            'descripcion': 'Sistema web completo para gestión empresarial',
            'features': [
                'Aplicación web responsive',
                'Panel de administración',
                'Gestión de usuarios y roles',
                'Base de datos personalizada',
                'Integración con servicios externos',
                'Reportes y analytics',
                'Soporte post-lanzamiento (60 días)',
                'Entrega en 12-16 semanas'
            ]
        }
    ]
    
    for plan in software_plans:
        PurchasableService.objects.create(
            service=software_service,
            name=plan['nombre'],
            price_usd=plan['precio_usd'],
            description=plan['descripcion'],
            features=plan['features']
        )
    
    # Create Tech Consulting service
    consulting_category, created = ServiceCategory.objects.get_or_create(
        name="Consultoría Tecnológica",
        defaults={
            'description': "Asesoramiento y consultoría en tecnología"
        }
    )
    
    consulting_service = Servicio.objects.create(
        nombre="Asesorías en Tecnología",
        descripcion="Consultoría experta en tecnología para optimizar tus procesos empresariales y tomar decisiones informadas",
        image_url="https://via.placeholder.com/400x300?text=Tech+Consulting",
        category=consulting_category,
        is_active=True
    )
    
    # Create purchasable service plans for Tech Consulting
    consulting_plans = [
        {
            'nombre': 'Consultoría Básica',
            'precio_usd': 299.99,
            'descripcion': 'Sesión de consultoría tecnológica de 4 horas',
            'features': [
                '4 horas de consultoría',
                'Evaluación de infraestructura actual',
                'Recomendaciones básicas',
                'Informe de diagnóstico',
                'Seguimiento por email (30 días)'
            ]
        },
        {
            'nombre': 'Consultoría Avanzada',
            'precio_usd': 899.99,
            'descripcion': 'Análisis completo y plan estratégico tecnológico',
            'features': [
                '16 horas de consultoría',
                'Análisis profundo de sistemas',
                'Plan estratégico tecnológico',
                'Roadmap de implementación',
                'Evaluación de ROI',
                'Seguimiento mensual (3 meses)',
                'Soporte prioritario'
            ]
        }
    ]
    
    for plan in consulting_plans:
        PurchasableService.objects.create(
            service=consulting_service,
            name=plan['nombre'],
            price_usd=plan['precio_usd'],
            description=plan['descripcion'],
            features=plan['features']
        )
    
    # Create Networks & Servers service
    networks_category, created = ServiceCategory.objects.get_or_create(
        name="Redes y Servidores",
        defaults={
            'description': "Servicios de infraestructura de red y servidores"
        }
    )
    
    networks_service = Servicio.objects.create(
        nombre="Servicios de Redes y Servidores Locales",
        descripcion="Configuración y mantenimiento de redes empresariales y servidores locales para tu organización",
        image_url="https://via.placeholder.com/400x300?text=Networks+%26+Servers",
        category=networks_category,
        is_active=True
    )
    
    # Create purchasable service plans for Networks & Servers
    networks_plans = [
        {
            'nombre': 'Configuración de Red Básica',
            'precio_usd': 599.99,
            'descripcion': 'Configuración de red local para pequeñas empresas',
            'features': [
                'Configuración de router/switch',
                'Red WiFi empresarial',
                'Hasta 20 dispositivos',
                'Seguridad básica de red',
                'Documentación de red',
                'Soporte remoto (30 días)'
            ]
        },
        {
            'nombre': 'Servidor Local + Red Avanzada',
            'precio_usd': 1299.99,
            'descripcion': 'Servidor local con red empresarial completa',
            'features': [
                'Servidor Windows/Linux',
                'Active Directory',
                'Backup automático',
                'Monitoreo de red',
                'Firewall empresarial',
                'VPN empresarial',
                'Soporte on-site (60 días)',
                'Mantenimiento mensual'
            ]
        }
    ]
    
    for plan in networks_plans:
        PurchasableService.objects.create(
            service=networks_service,
            name=plan['nombre'],
            price_usd=plan['precio_usd'],
            description=plan['descripcion'],
            features=plan['features']
        )
    
    # Create IoT Solutions service
    iot_category, created = ServiceCategory.objects.get_or_create(
        name="Soluciones IoT",
        defaults={
            'description': "Internet de las cosas y dispositivos conectados"
        }
    )
    
    iot_service = Servicio.objects.create(
        nombre="Soluciones IoT",
        descripcion="Implementación de soluciones IoT para automatización y monitoreo empresarial inteligente",
        image_url="https://via.placeholder.com/400x300?text=IoT+Solutions",
        category=iot_category,
        is_active=True
    )
    
    # Create purchasable service plans for IoT Solutions
    iot_plans = [
        {
            'nombre': 'IoT Básico',
            'precio_usd': 799.99,
            'descripcion': 'Solución IoT básica para monitoreo',
            'features': [
                'Hasta 10 sensores IoT',
                'Dashboard básico',
                'Alertas por email',
                'Aplicación móvil',
                'Almacenamiento de datos (1 año)',
                'Soporte técnico básico'
            ]
        },
        {
            'nombre': 'IoT Empresarial',
            'precio_usd': 1999.99,
            'descripcion': 'Solución IoT avanzada para empresas',
            'features': [
                'Hasta 50 sensores IoT',
                'Dashboard avanzado con BI',
                'Automatización inteligente',
                'Integración con sistemas ERP',
                'Machine Learning básico',
                'API personalizada',
                'Soporte 24/7',
                'Mantenimiento incluido'
            ]
        }
    ]
    
    for plan in iot_plans:
        PurchasableService.objects.create(
            service=iot_service,
            name=plan['nombre'],
            price_usd=plan['precio_usd'],
            description=plan['descripcion'],
            features=plan['features']
        )
    
    print(f"✓ Servicio de Desarrollo de Software creado con {len(software_plans)} planes")
    print(f"✓ Servicio de Asesorías en Tecnología creado con {len(consulting_plans)} planes")
    print(f"✓ Servicio de Redes y Servidores creado con {len(networks_plans)} planes")
    print(f"✓ Servicio de Soluciones IoT creado con {len(iot_plans)} planes")
    
    return [ssl_service, software_service, consulting_service, networks_service, iot_service]

def main():
    """Función principal"""
    print("🚀 Agregando nuevos servicios a Megadominio.co...")
    print("\n📋 Creando servicios principales...")
    new_services = create_all_new_services()
    
    print("\n✅ ¡Todos los servicios han sido agregados exitosamente!")
    print("\n📊 Resumen de servicios creados:")
    for service in new_services:
        plans_count = service.purchasable_services.count()
        print(f"• {service.nombre}: {plans_count} planes")

if __name__ == "__main__":
    print("Creando servicio SSL y Antivirus...")
    ssl_service = create_ssl_antivirus_service()
    print(f"\n✅ ¡Servicio SSL y Antivirus creado exitosamente!")
    print(f"Nombre: {ssl_service.nombre}")
    print(f"Planes: {ssl_service.purchasable_services.count()}") 