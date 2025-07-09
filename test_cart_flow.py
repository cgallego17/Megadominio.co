#!/usr/bin/env python
"""
Script de prueba para verificar el flujo completo del carrito
"""
import os
import sys
import django
import requests
from urllib.parse import urljoin

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'megadominio.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from accounts.models import PurchasableService, Cart, CartItem

def test_cart_flow():
    """Prueba el flujo completo del carrito"""
    print("=== PRUEBA DEL FLUJO DEL CARRITO ===")
    
    # Crear cliente de prueba
    client = Client()
    
    # URL base
    base_url = "http://testserver"
    
    # 1. Verificar que el catálogo funciona
    print("\n1. Probando acceso al catálogo...")
    response = client.get('/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Catálogo accesible")
    else:
        print("   ❌ Error en catálogo")
        return False
    
    # 2. Obtener un servicio para agregar al carrito
    print("\n2. Buscando servicios disponibles...")
    try:
        service = PurchasableService.objects.filter(is_active=True).first()
        if not service:
            print("   ❌ No hay servicios activos disponibles")
            return False
        
        print(f"   ✅ Servicio encontrado: {service.name} (ID: {service.id})")
        
        # Obtener un ciclo de facturación disponible
        billing_cycles = service.get_available_billing_cycles()
        if not billing_cycles:
            print("   ❌ No hay ciclos de facturación disponibles")
            return False
        
        billing_cycle = billing_cycles[0]
        # Si es una tupla, tomar solo el primer valor
        if isinstance(billing_cycle, tuple):
            billing_cycle = billing_cycle[0]
        print(f"   ✅ Ciclo de facturación: {billing_cycle}")
        
    except Exception as e:
        print(f"   ❌ Error obteniendo servicio: {e}")
        return False
    
    # 3. Agregar producto al carrito
    print("\n3. Agregando producto al carrito...")
    add_to_cart_data = {
        'service_id': service.id,
        'billing_cycle': billing_cycle,
        'quantity': '1',
        'csrfmiddlewaretoken': client.cookies.get('csrftoken', '').value
    }
    
    response = client.post('/cart/add/', data=add_to_cart_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"   Response: {data}")
            if data.get('success'):
                print("   ✅ Producto agregado al carrito")
                cart_items_count = data.get('cart_items_count', 0)
                print(f"   Items en carrito: {cart_items_count}")
            else:
                print(f"   ❌ Error: {data.get('message', 'Error desconocido')}")
                return False
        except Exception as e:
            print(f"   ❌ Error parseando respuesta JSON: {e}")
            return False
    else:
        print(f"   ❌ Error en request: {response.content}")
        return False
    
    # 4. Verificar carrito
    print("\n4. Verificando carrito...")
    response = client.get('/cart/')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Carrito accesible")
        
        # Verificar si hay items en el carrito
        try:
            cart_id = client.session.get('cart_id')
            if cart_id:
                cart = Cart.objects.get(id=cart_id, user__isnull=True)
                items_count = cart.get_items_count()
                print(f"   Items en carrito (DB): {items_count}")
                
                if items_count > 0:
                    print("   ✅ Carrito tiene productos")
                    
                    # Mostrar detalles de los items
                    for item in cart.items.all():
                        print(f"     - {item.service.name} ({item.billing_cycle}) x{item.quantity}")
                else:
                    print("   ❌ Carrito vacío en la base de datos")
                    return False
            else:
                print("   ❌ No hay cart_id en la sesión")
                return False
                
        except Exception as e:
            print(f"   ❌ Error verificando carrito: {e}")
            return False
    else:
        print("   ❌ Error accediendo al carrito")
        return False
    
    # 5. Verificar contador del carrito
    print("\n5. Verificando contador del carrito...")
    response = client.get('/cart/counter/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            cart_items_count = data.get('cart_items_count', 0)
            print(f"   Contador del carrito: {cart_items_count}")
            
            if cart_items_count > 0:
                print("   ✅ Contador del carrito funciona")
            else:
                print("   ❌ Contador del carrito muestra 0")
                return False
        except Exception as e:
            print(f"   ❌ Error parseando contador: {e}")
            return False
    else:
        print("   ❌ Error en contador del carrito")
        return False
    
    # 6. Probar el flujo de checkout
    print("\n6. Probando flujo de checkout...")
    response = client.get('/checkout/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Checkout accesible")
        # Simular envío de formulario de checkout (simplificado)
        # Buscar campos requeridos en el contexto de la respuesta
        # Aquí asumimos que el formulario requiere al menos nombre y email
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        form = soup.find('form')
        if not form:
            print("   ❌ No se encontró el formulario de checkout")
            return False
        # Buscar campos
        name_input = form.find('input', {'name': 'billing_name'})
        email_input = form.find('input', {'name': 'billing_email'})
        if not name_input or not email_input:
            print("   ❌ Faltan campos obligatorios en el formulario de checkout")
            return False
        # Preparar datos de checkout
        checkout_data = {
            'billing_name': 'Cliente de Prueba',
            'billing_email': 'cliente@prueba.com',
            'billing_address': 'Calle Falsa 123',
            'notes': 'Prueba de checkout automatizado',
            'csrfmiddlewaretoken': client.cookies.get('csrftoken', '').value
        }
        # Enviar POST para crear la orden
        response_post = client.post('/checkout/', data=checkout_data, follow=True)
        print(f"   POST Status: {response_post.status_code}")
        if response_post.status_code == 200 and b'Orden Confirmada' in response_post.content:
            print("   ✅ Orden confirmada y página de confirmación mostrada")
            # Extraer número de orden
            soup_conf = BeautifulSoup(response_post.content, 'html.parser')
            h2 = soup_conf.find('h2')
            if h2:
                print(f"   Número de orden mostrado: {h2.text.strip()}")
        else:
            print("   ❌ No se mostró la confirmación de orden")
            return False
    else:
        print("   ❌ Error accediendo al checkout")
        return False
    
    print("\n=== PRUEBA COMPLETADA EXITOSAMENTE ===")
    return True

def test_cart_debug():
    """Función de debug para verificar el estado del carrito"""
    print("\n=== DEBUG DEL CARRITO ===")
    
    # Verificar carritos en la base de datos
    carts = Cart.objects.all()
    print(f"Total de carritos en DB: {carts.count()}")
    
    for cart in carts:
        print(f"  Carrito ID: {cart.id}, Usuario: {cart.user}, Items: {cart.get_items_count()}")
        for item in cart.items.all():
            print(f"    - {item.service.name} ({item.billing_cycle}) x{item.quantity}")
    
    # Verificar servicios disponibles
    services = PurchasableService.objects.filter(is_active=True)
    print(f"\nServicios activos: {services.count()}")
    for service in services[:5]:  # Mostrar solo los primeros 5
        print(f"  - {service.name} (ID: {service.id})")
        cycles = service.get_available_billing_cycles()
        print(f"    Ciclos disponibles: {cycles}")

if __name__ == "__main__":
    print("Iniciando pruebas del carrito...")
    
    # Debug inicial
    test_cart_debug()
    
    # Prueba del flujo
    success = test_cart_flow()
    
    if success:
        print("\n🎉 Todas las pruebas pasaron exitosamente!")
    else:
        print("\n❌ Algunas pruebas fallaron")
        sys.exit(1) 