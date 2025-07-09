#!/usr/bin/env python
"""
Script para verificar los precios de los dominios
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'megadominio.settings')
django.setup()

from accounts.models import PurchasableService
from servicios.models import Servicio
from accounts.utils import get_service_prices_for_user, get_purchasable_service_prices

def check_domain_prices():
    """Verificar precios de dominios"""
    print("=== Verificación de Precios de Dominios ===\n")
    
    # Buscar el servicio de dominios
    try:
        dominio_service = Servicio.get_by_slug('dominios')
        print(f"Servicio encontrado: {dominio_service.nombre}")
        print(f"Descripción: {dominio_service.descripcion_corta}")
        print()
        
        # Verificar servicios comprables
        purchasable_services = dominio_service.purchasable_services.filter(is_active=True)
        print(f"Servicios comprables activos: {purchasable_services.count()}")
        
        for service in purchasable_services:
            print(f"\n--- Servicio: {service.name} ---")
            print(f"Slug: {service.slug}")
            print(f"Descripción: {service.short_description}")
            print(f"Activo: {service.is_active}")
            print(f"Requiere dominio: {service.requires_domain}")
            
            # Verificar precios
            print("\nPrecios configurados:")
            print(f"  Mensual: {service.price_monthly}")
            print(f"  Trimestral: {service.price_quarterly}")
            print(f"  Semestral: {service.price_semiannual}")
            print(f"  Anual: {service.price_annual}")
            print(f"  Bienal: {service.price_biennial}")
            print(f"  Único: {service.price_one_time}")
            
            # Verificar precios procesados
            print("\nPrecios procesados (USD):")
            prices = get_purchasable_service_prices(service, 'USD')
            for cycle, price_info in prices.items():
                print(f"  {cycle}: {price_info['formatted']} (original: {price_info['original']})")
            
            # Verificar precios en COP
            print("\nPrecios procesados (COP):")
            prices_cop = get_purchasable_service_prices(service, 'COP')
            for cycle, price_info in prices_cop.items():
                print(f"  {cycle}: {price_info['formatted']} (original: {price_info['original']})")
            
            print("-" * 50)
        
        # Verificar si hay servicios sin precios
        services_without_prices = []
        for service in purchasable_services:
            has_prices = any([
                service.price_monthly,
                service.price_quarterly,
                service.price_semiannual,
                service.price_annual,
                service.price_biennial,
                service.price_one_time
            ])
            if not has_prices:
                services_without_prices.append(service)
        
        if services_without_prices:
            print(f"\n⚠️  SERVICIOS SIN PRECIOS CONFIGURADOS:")
            for service in services_without_prices:
                print(f"  - {service.name} (ID: {service.id})")
        else:
            print("\n✅ Todos los servicios tienen precios configurados")
            
    except Servicio.DoesNotExist:
        print("❌ No se encontró el servicio de dominios")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_cart_items():
    """Verificar items en carritos"""
    print("\n=== Verificación de Items en Carritos ===\n")
    
    from accounts.models import CartItem, Cart
    
    # Verificar carritos con items
    carts_with_items = Cart.objects.filter(items__isnull=False).distinct()
    print(f"Carritos con items: {carts_with_items.count()}")
    
    for cart in carts_with_items:
        print(f"\n--- Carrito ID: {cart.id} ---")
        if cart.user:
            print(f"Usuario: {cart.user.username}")
        else:
            print("Usuario: Anónimo")
        
        for item in cart.items.all():
            print(f"\n  Item: {item.service.name}")
            print(f"  Ciclo: {item.billing_cycle}")
            print(f"  Cantidad: {item.quantity}")
            print(f"  Precio unitario (método): {item.get_unit_price()}")
            print(f"  Total (método): {item.get_total()}")
            
            # Verificar precios procesados
            from django.http import HttpRequest
            request = HttpRequest()
            request.META = {}
            
            service_prices = get_service_prices_for_user(item.service, request, cart.user)
            print(f"  Precios procesados: {service_prices}")

if __name__ == "__main__":
    check_domain_prices()
    check_cart_items() 