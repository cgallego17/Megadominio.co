#!/usr/bin/env python
"""
Script de prueba para verificar el flujo completo de checkout con registro de usuario
"""

import os
import sys
import django

# Configurar Django antes de importar modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'megadominio.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import PurchasableService, Cart, CartItem, Order, TermsAcceptance

def test_checkout_flow():
    """Prueba el flujo completo de checkout con registro de usuario"""
    client = Client()
    
    print("🔄 Iniciando prueba de flujo de checkout con registro...")
    
    # 1. Ir a la página principal
    print("\n1. Accediendo a la página principal...")
    response = client.get('/')
    assert response.status_code == 200, f"Error: {response.status_code}"
    print("✅ Página principal cargada correctamente")
    
    # 2. Ir a un servicio específico
    print("\n2. Accediendo a un servicio...")
    response = client.get('/servicio/desarrollo-web/')
    assert response.status_code == 200, f"Error: {response.status_code}"
    print("✅ Página de servicio cargada correctamente")
    
    # 3. Ir a un servicio comprable específico
    print("\n3. Accediendo a un servicio comprable...")
    response = client.get('/servicio/desarrollo-web/web-dev-3-2025/')
    assert response.status_code == 200, f"Error: {response.status_code}"
    print("✅ Página de servicio comprable cargada correctamente")
    
    # 4. Agregar al carrito
    print("\n4. Agregando producto al carrito...")
    response = client.post('/cart/add/', {
        'service_id': '1',  # Asumiendo que existe un servicio con ID 1
        'billing_cycle': 'monthly',
        'quantity': '1',
        'domain_name': '',
        'notes': ''
    })
    assert response.status_code == 200, f"Error: {response.status_code}"
    print("✅ Producto agregado al carrito")
    
    # 5. Ver carrito
    print("\n5. Verificando carrito...")
    response = client.get('/cart/')
    assert response.status_code == 200, f"Error: {response.status_code}"
    print("✅ Carrito cargado correctamente")
    
    # 6. Ir al checkout
    print("\n6. Accediendo al checkout...")
    response = client.get('/checkout/')
    assert response.status_code == 200, f"Error: {response.status_code}"
    print("✅ Checkout cargado correctamente")
    
    # 7. Completar checkout con registro de usuario
    print("\n7. Completando checkout con registro de usuario...")
    checkout_data = {
        'billing_name': 'Juan Pérez',
        'billing_email': 'juan.perez@test.com',
        'phone': '+57 300 123 4567',
        'company': 'Empresa Test',
        'billing_address': 'Calle 123 #45-67, Bogotá',
        'notes': 'Prueba de checkout con registro',
        'terms_accepted': 'on'
    }
    
    response = client.post('/checkout/', checkout_data)
    print(f"Respuesta del checkout: {response.status_code}")
    
    if response.status_code == 302:  # Redirect a confirmación
        print("✅ Checkout completado exitosamente")
        
        # Verificar que se creó el usuario
        try:
            user = User.objects.get(email='juan.perez@test.com')
            print(f"✅ Usuario creado: {user.username}")
            
            # Verificar que se registró la aceptación de términos
            terms_acceptance = TermsAcceptance.objects.filter(user=user).first()
            if terms_acceptance:
                print(f"✅ Términos aceptados: {terms_acceptance.accepted_at}")
            else:
                print("⚠️ No se encontró registro de aceptación de términos")
                
            # Verificar que se creó la orden
            orders = Order.objects.filter(user=user)
            if orders.exists():
                order = orders.latest('created_at')
                print(f"✅ Orden creada: #{order.order_number}")
            else:
                print("⚠️ No se encontró la orden")
                
        except User.DoesNotExist:
            print("❌ No se creó el usuario")
            
    else:
        print(f"❌ Error en checkout: {response.status_code}")
        if hasattr(response, 'content'):
            print(f"Contenido: {response.content.decode()[:200]}")
    
    print("\n🎉 Prueba completada!")

if __name__ == '__main__':
    test_checkout_flow() 