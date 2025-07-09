#!/usr/bin/env python3
"""
Script de Verificación - Servicios Actualizados 2025
Megadominio.co
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'megadominio.settings')
django.setup()

from accounts.models import PurchasableService
from servicios.models import Servicio

def verificar_actualizacion():
    print('🔍 VERIFICACIÓN FINAL - SERVICIOS ACTUALIZADOS 2025')
    print('='*60)

    # Obtener estadísticas
    total_services = PurchasableService.objects.filter(is_active=True).count()
    featured_services = PurchasableService.objects.filter(is_featured=True).count()

    print(f'📊 ESTADÍSTICAS GENERALES:')
    print(f'   Total servicios activos: {total_services}')
    print(f'   Servicios destacados: {featured_services}')

    # Mostrar servicios por categoría de home service
    print(f'\n🎯 SERVICIOS POR CATEGORÍA:')
    for home_service in Servicio.objects.all():
        count = home_service.purchasable_services.filter(is_active=True).count()
        if count > 0:
            print(f'   📁 {home_service.nombre}: {count} servicios')
            
            # Mostrar algunos precios de ejemplo
            services = home_service.purchasable_services.filter(is_active=True)[:2]
            for service in services:
                prices = []
                if service.price_monthly:
                    prices.append(f'${service.price_monthly}/mes')
                if service.price_annual:
                    prices.append(f'${service.price_annual}/año')
                if service.price_one_time:
                    prices.append(f'${service.price_one_time} único')
                
                if prices:
                    price_str = ', '.join(prices)
                    print(f'      💰 {service.name}: {price_str}')

    print(f'\n🎯 SERVICIOS DESTACADOS (FEATURED):')
    featured = PurchasableService.objects.filter(is_featured=True, is_active=True)
    for service in featured:
        print(f'   ⭐ {service.name} ({service.home_service.nombre})')

    print(f'\n💰 RANGOS DE PRECIOS POR CATEGORÍA:')
    
    # Hosting
    hosting_services = PurchasableService.objects.filter(
        home_service__nombre__icontains='Hosting', 
        is_active=True
    )
    if hosting_services.exists():
        prices = [s.price_monthly for s in hosting_services if s.price_monthly]
        if prices:
            print(f'   🌐 Hosting: ${min(prices)} - ${max(prices)}/mes')
    
    # Dominios
    domain_services = PurchasableService.objects.filter(
        home_service__nombre__icontains='Dominio', 
        is_active=True
    )
    if domain_services.exists():
        prices = [s.price_annual for s in domain_services if s.price_annual]
        if prices:
            print(f'   🔗 Dominios: ${min(prices)} - ${max(prices)}/año')
    
    # SSL
    ssl_services = PurchasableService.objects.filter(
        home_service__nombre__icontains='SSL', 
        is_active=True
    )
    if ssl_services.exists():
        prices = [s.price_annual for s in ssl_services if s.price_annual]
        if prices:
            print(f'   🔒 SSL: ${min(prices)} - ${max(prices)}/año')
    
    # Desarrollo Web
    web_services = PurchasableService.objects.filter(
        home_service__nombre__icontains='Desarrollo', 
        is_active=True
    )
    if web_services.exists():
        prices = [s.price_one_time for s in web_services if s.price_one_time]
        if prices:
            print(f'   🎨 Desarrollo Web: ${min(prices)} - ${max(prices)} (único)')
    
    # Apps Móviles
    mobile_services = PurchasableService.objects.filter(
        home_service__nombre__icontains='Aplicaciones', 
        is_active=True
    )
    if mobile_services.exists():
        prices = [s.price_one_time for s in mobile_services if s.price_one_time]
        if prices:
            print(f'   📱 Apps Móviles: ${min(prices)} - ${max(prices)} (único)')
    
    # SEO
    seo_services = PurchasableService.objects.filter(
        home_service__nombre__icontains='SEO', 
        is_active=True
    )
    if seo_services.exists():
        prices = [s.price_monthly for s in seo_services if s.price_monthly]
        if prices:
            print(f'   🔍 SEO/Marketing: ${min(prices)} - ${max(prices)}/mes')

    print(f'\n✅ ACTUALIZACIÓN COMPLETADA EXITOSAMENTE!')
    print(f'🚀 Precios competitivos listos para el mercado 2025!')

if __name__ == '__main__':
    verificar_actualizacion() 