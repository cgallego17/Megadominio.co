from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import (TwoFactorCode, LoginAttempt, ClientService, EmailAccount, ServiceNotification, 
                     HostingPlan, ServiceCategory, PurchasableService, Cart, CartItem, Order, OrderItem,
                     WompiConfiguration, WompiTransaction, WompiWebhookEvent, TermsAcceptance)
from .utils import (get_client_ip, verify_recaptcha_v3, get_user_country, 
                     get_currency_for_country, get_service_prices_for_user, convert_price_to_currency, format_price)
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models import Q, Count
from datetime import datetime, timedelta
import requests
from django.conf import settings
from adminpanel.views import verify_recaptcha_v3  # Importar función unificada
from adminpanel.models import Cliente, Venta, DetalleVenta  # Importar modelos de clientes y ventas
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import random
import string
import logging
import json
from django.urls import reverse # Added for password reset

User = get_user_model()

# Configurar logger
logger = logging.getLogger(__name__)

# Importar el servicio de Wompi
try:
    from .services import WompiService
except ImportError:
    WompiService = None

def create_or_update_client_from_order(order):
    """
    Crea o actualiza un cliente en el sistema de clientes cuando se completa una orden
    """
    try:
        # Si la orden tiene un usuario asociado
        if order.user:
            # Buscar si ya existe un cliente con este email
            cliente, created = Cliente.objects.get_or_create(
                email=order.user.email,
                defaults={
                    'nombre': order.user.get_full_name() or order.user.username,
                    'telefono': order.user.phone or '',
                    'empresa': order.user.company or '',
                    'direccion': order.user.address or '',
                    'estado': 'activo',
                    'notas': f'Cliente creado automáticamente desde orden #{order.order_number}'
                }
            )
            
            # Si el cliente ya existía, actualizar información si es necesario
            if not created:
                if not cliente.nombre and order.user.get_full_name():
                    cliente.nombre = order.user.get_full_name()
                if not cliente.telefono and order.user.phone:
                    cliente.telefono = order.user.phone
                if not cliente.empresa and order.user.company:
                    cliente.empresa = order.user.company
                if not cliente.direccion and order.user.address:
                    cliente.direccion = order.user.address
                cliente.save()
        else:
            # Para órdenes anónimas, crear cliente con datos de facturación
            cliente, created = Cliente.objects.get_or_create(
                email=order.billing_email,
                defaults={
                    'nombre': order.billing_name,
                    'telefono': '',
                    'empresa': '',
                    'direccion': order.billing_address,
                    'estado': 'activo',
                    'notas': f'Cliente creado automáticamente desde orden #{order.order_number} (compra anónima)'
                }
            )
        
        # Crear la venta correspondiente
        venta, venta_created = Venta.objects.get_or_create(
            numero_factura=order.order_number,
            defaults={
                'cliente': cliente,
                'estado': 'completada' if order.status == 'completed' else 'pendiente',
                'metodo_pago': 'tarjeta',  # Por defecto, se puede actualizar según el método real
                'subtotal': float(order.subtotal),
                'impuestos': float(order.tax_amount),
                'descuento': 0,
                'valor_total': float(order.total_amount),
                'descripcion': f'Orden #{order.order_number}',
                'notas': order.notes or ''
            }
        )
        
        # Crear detalles de venta para cada item de la orden
        for order_item in order.items.all():
            DetalleVenta.objects.get_or_create(
                venta=venta,
                servicio=order_item.service_name,
                defaults={
                    'descripcion': f'{order_item.service_name} - {order_item.billing_cycle}',
                    'cantidad': order_item.quantity,
                    'precio_unitario': float(order_item.unit_price),
                    'subtotal': float(order_item.total_price)
                }
            )
        
        # Actualizar estadísticas del cliente
        cliente.actualizar_estadisticas()
        
        logger.info(f"Cliente creado/actualizado: {cliente.nombre} (ID: {cliente.id}) desde orden #{order.order_number}")
        return cliente
        
    except Exception as e:
        logger.error(f"Error creando cliente desde orden #{order.order_number}: {e}")
        return None

def process_existing_orders_to_clients():
    """
    Procesa órdenes existentes completadas para crear clientes automáticamente
    Esta función es útil para migrar datos existentes
    """
    try:
        # Obtener órdenes completadas que no tienen cliente asociado
        completed_orders = Order.objects.filter(status='completed')
        
        created_clients = 0
        updated_clients = 0
        
        for order in completed_orders:
            try:
                cliente = create_or_update_client_from_order(order)
                if cliente:
                    # Verificar si el cliente fue creado o actualizado
                    if cliente.created_at == cliente.updated_at:
                        created_clients += 1
                    else:
                        updated_clients += 1
                        
            except Exception as e:
                logger.error(f"Error procesando orden #{order.order_number}: {e}")
                continue
        
        logger.info(f"Procesamiento completado: {created_clients} clientes creados, {updated_clients} actualizados")
        return {
            'created': created_clients,
            'updated': updated_clients,
            'total_processed': len(completed_orders)
        }
        
    except Exception as e:
        logger.error(f"Error en procesamiento masivo de órdenes: {e}")
        return None

def log_login_attempt(request, username, user=None, success=False):
    """Registrar intento de login"""
    LoginAttempt.objects.create(
        user=user,
        ip_address=get_client_ip(request),
        username_attempted=username,
        success=success,
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

@csrf_protect
def login_view(request):
    """Vista de login con reCAPTCHA y 2FA"""
    if request.user.is_authenticated:
        if request.user.is_admin():
            return redirect('/panel/dashboard/')  # Usar el dashboard de adminpanel
        else:
            return redirect('accounts:client_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        recaptcha_token = request.POST.get('g-recaptcha-response')
        
        # Verificar reCAPTCHA usando función unificada (solo si está habilitado)
        recaptcha_enabled = getattr(settings, 'RECAPTCHA_ENABLED', True)
        if recaptcha_enabled:
            if not recaptcha_token or not verify_recaptcha_v3(recaptcha_token):
                messages.error(request, "Por favor, completa la verificación de seguridad al hacer login.")
                return render(request, 'accounts/login.html')
        else:
            print("[DEBUG] reCAPTCHA deshabilitado en desarrollo")
        
        # Autenticar usuario
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                # Registrar intento exitoso
                log_login_attempt(request, username, user, True)
                
                # Verificar si tiene 2FA habilitado
                if user.two_factor_enabled:
                    # Crear código 2FA
                    code = TwoFactorCode.objects.create(user=user)
                    if code.send_code():
                        request.session['pending_2fa_user_id'] = user.id
                        return redirect('accounts:verify_2fa')
                    else:
                        messages.error(request, 'Error enviando código de verificación')
                else:
                    # Login directo
                    login(request, user)
                    if user.is_admin():
                        return redirect('/panel/dashboard/')  # Usar el dashboard de adminpanel
                    else:
                        return redirect('accounts:client_dashboard')
            else:
                messages.error(request, 'Tu cuenta está desactivada')
                log_login_attempt(request, username, user, False)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
            log_login_attempt(request, username, None, False)
    
    return render(request, 'accounts/login.html')

def verify_2fa(request):
    """Vista para verificar código 2FA"""
    if not request.session.get('pending_2fa_user_id'):
        return redirect('accounts:login')
    
    user_id = request.session.get('pending_2fa_user_id')
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        code = request.POST.get('code')
        
        if code:
            # Buscar código válido
            two_factor_code = TwoFactorCode.objects.filter(
                user=user,
                code=code,
                is_used=False
            ).first()
            
            if two_factor_code and two_factor_code.is_valid():
                # Marcar código como usado
                two_factor_code.is_used = True
                two_factor_code.save()
                
                # Limpiar sesión
                del request.session['pending_2fa_user_id']
                
                # Hacer login
                login(request, user)
                
                if user.is_admin():
                    return redirect('/panel/dashboard/')  # Usar el dashboard de adminpanel
                else:
                    return redirect('accounts:client_dashboard')
            else:
                messages.error(request, 'Código inválido o expirado')
        else:
            messages.error(request, 'Por favor, ingresa el código')
    
    return render(request, 'accounts/verify_2fa.html', {'user': user})

@login_required
def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente')
    return redirect('accounts:login')

@login_required
def admin_dashboard(request):
    """Dashboard para administradores"""
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder a esta área')
        return redirect('accounts:client_dashboard')
    
    # Importar modelos necesarios
    from servicios.models import Servicio
    from proyectos.models import Proyecto
    from adminpanel.models import EstadisticaDiaria, ContactoFormulario
    
    # Estadísticas
    total_usuarios = User.objects.count()
    total_clientes = User.objects.filter(user_type='client').count()
    total_admins = User.objects.filter(user_type='admin').count()
    total_servicios = Servicio.objects.count()
    total_proyectos = Proyecto.objects.count()
    total_contactos = ContactoFormulario.objects.count()
    
    # Intentos de login recientes
    recent_login_attempts = LoginAttempt.objects.all()[:10]
    
    # Usuarios recientes
    recent_users = User.objects.filter(user_type='client').order_by('-date_joined')[:5]
    
    context = {
        'total_usuarios': total_usuarios,
        'total_clientes': total_clientes,
        'total_admins': total_admins,
        'total_servicios': total_servicios,
        'total_proyectos': total_proyectos,
        'total_contactos': total_contactos,
        'recent_login_attempts': recent_login_attempts,
        'recent_users': recent_users,
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)

@login_required
def client_dashboard(request):
    """Dashboard principal para clientes"""
    if not request.user.is_client():
        return redirect('adminpanel:admin_dashboard')
    
    # Obtener servicios del cliente
    services = ClientService.objects.filter(client=request.user).order_by('-created_at')
    
    # Servicios que vencen pronto (próximos 30 días)
    expiring_services = services.filter(
        expiry_date__gte=timezone.now().date(),
        expiry_date__lte=timezone.now().date() + timedelta(days=30)
    ).order_by('expiry_date')
    
    # Servicios vencidos
    expired_services = services.filter(
        expiry_date__lt=timezone.now().date(),
        status='active'
    ).order_by('expiry_date')
    
    # Notificaciones no leídas
    unread_notifications = ServiceNotification.objects.filter(
        client=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    # Estadísticas
    stats = {
        'total_services': services.count(),
        'active_services': services.filter(status='active').count(),
        'expiring_services': expiring_services.count(),
        'expired_services': expired_services.count(),
    }
    
    context = {
        'services': services[:10],  # Últimos 10 servicios
        'expiring_services': expiring_services,
        'expired_services': expired_services,
        'notifications': unread_notifications,
        'stats': stats,
    }
    
    return render(request, 'accounts/client_dashboard.html', context)

@login_required
def client_services(request):
    """Lista completa de servicios del cliente"""
    if not request.user.is_client():
        return redirect('adminpanel:admin_dashboard')
    
    services = ClientService.objects.filter(client=request.user).order_by('-created_at')
    
    # Filtros
    service_type = request.GET.get('type')
    status = request.GET.get('status')
    
    if service_type:
        services = services.filter(service_type=service_type)
    if status:
        services = services.filter(status=status)
    
    context = {
        'services': services,
        'service_types': ClientService.SERVICE_TYPES,
        'status_choices': ClientService.STATUS_CHOICES,
        'current_type': service_type,
        'current_status': status,
    }
    
    return render(request, 'accounts/client_services.html', context)

@login_required
def service_detail(request, service_id):
    """Detalle de un servicio específico"""
    service = get_object_or_404(ClientService, id=service_id, client=request.user)
    
    # Cuentas de email asociadas
    email_accounts = EmailAccount.objects.filter(service=service)
    
    # Notificaciones del servicio
    notifications = ServiceNotification.objects.filter(
        service=service
    ).order_by('-created_at')[:10]
    
    context = {
        'service': service,
        'email_accounts': email_accounts,
        'notifications': notifications,
    }
    
    return render(request, 'accounts/service_detail.html', context)



@login_required
def client_notifications(request):
    """Centro de notificaciones del cliente"""
    if not request.user.is_client():
        return redirect('adminpanel:admin_dashboard')
    
    notifications = ServiceNotification.objects.filter(
        client=request.user
    ).order_by('-created_at')
    
    # Marcar como leídas
    if request.method == 'POST':
        notification_ids = request.POST.getlist('notification_ids')
        ServiceNotification.objects.filter(
            id__in=notification_ids,
            client=request.user
        ).update(is_read=True)
        messages.success(request, 'Notificaciones marcadas como leídas.')
        return redirect('accounts:client_notifications')
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'accounts/client_notifications.html', context)

@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Marcar notificación como leída (AJAX)"""
    try:
        notification = ServiceNotification.objects.get(
            id=notification_id,
            client=request.user
        )
        notification.is_read = True
        notification.save()
        
        return JsonResponse({'success': True})
    except ServiceNotification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notificación no encontrada'})

@login_required
def client_profile(request):
    """Perfil del cliente"""
    if not request.user.is_client():
        return redirect('adminpanel:admin_dashboard')
    
    if request.method == 'POST':
        # Actualizar perfil
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.phone = request.POST.get('phone', '')
        request.user.company = request.POST.get('company', '')
        request.user.address = request.POST.get('address', '')
        request.user.city = request.POST.get('city', '')
        request.user.country = request.POST.get('country', '')
        
        request.user.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('accounts:client_profile')
    
    context = {
        'user': request.user,
    }
    
    return render(request, 'accounts/client_profile.html', context)



@login_required
def resend_2fa_code(request):
    """Reenviar código 2FA"""
    if not request.session.get('pending_2fa_user_id'):
        return JsonResponse({'success': False, 'message': 'Sesión inválida'})
    
    user_id = request.session.get('pending_2fa_user_id')
    user = get_object_or_404(User, id=user_id)
    
    # Crear nuevo código
    code = TwoFactorCode.objects.create(user=user)
    
    if code.send_code():
        return JsonResponse({'success': True, 'message': 'Código reenviado'})
    else:
        return JsonResponse({'success': False, 'message': 'Error enviando código'})

# ===============================
# VISTAS DEL CATÁLOGO DE SERVICIOS
# ===============================











@require_http_methods(["POST"])
def update_cart_item(request):
    """Actualizar cantidad de item en carrito (AJAX) - ahora público para usuarios anónimos"""
    # Solo verificar si es cliente si está autenticado
    if request.user.is_authenticated and not request.user.is_client():
        return JsonResponse({'success': False, 'message': 'Acceso denegado'})
    
    try:
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        # Obtener cart_item según usuario autenticado o anónimo
        if request.user.is_authenticated:
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        else:
            cart_id = request.session.get('cart_id')
            if not cart_id:
                return JsonResponse({'success': False, 'message': 'Carrito no encontrado'})
            cart_item = get_object_or_404(CartItem, id=item_id, cart__id=cart_id, cart__user__isnull=True)
        
        # Obtener información de moneda del usuario
        if request.user.is_authenticated:
            user_country = get_user_country(request, request.user)
            user_currency = get_currency_for_country(user_country)
            service_prices = get_service_prices_for_user(cart_item.service, request, request.user)
        else:
            user_country = get_user_country(request)
            user_currency = get_currency_for_country(user_country)
            service_prices = get_service_prices_for_user(cart_item.service, request, None)
        
        # Obtener precio unitario convertido
        unit_price_key = cart_item.billing_cycle
        if unit_price_key in service_prices:
            unit_price_converted = service_prices[unit_price_key]['amount']
        else:
            # Fallback al precio original si no hay conversión
            unit_price_original = cart_item.get_unit_price()
            unit_price_converted = convert_price_to_currency(unit_price_original, user_currency)
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            item_total_converted = unit_price_converted * quantity
        else:
            cart_item.delete()
            item_total_converted = 0
        
        # Recalcular total del carrito
        cart = cart_item.cart
        cart_items = cart.items.all()
        cart_total_converted = 0
        
        for item in cart_items:
            item_service_prices = get_service_prices_for_user(item.service, request, request.user)
            item_unit_price_key = item.billing_cycle
            if item_unit_price_key in item_service_prices:
                item_unit_price_converted = item_service_prices[item_unit_price_key]['amount']
            else:
                item_unit_price_original = item.get_unit_price()
                item_unit_price_converted = convert_price_to_currency(item_unit_price_original, user_currency)
            
            cart_total_converted += item_unit_price_converted * item.quantity
        
        return JsonResponse({
            'success': True,
            'cart_items_count': cart.get_items_count(),
            'cart_total': float(cart_total_converted),
            'item_total': float(item_total_converted)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_http_methods(["POST"])
def remove_from_cart(request):
    """Remover item del carrito (AJAX) - ahora público para usuarios anónimos"""
    # Solo verificar si es cliente si está autenticado
    if request.user.is_authenticated and not request.user.is_client():
        return JsonResponse({'success': False, 'message': 'Acceso denegado'})
    
    try:
        item_id = request.POST.get('item_id')
        
        # Obtener cart_item según usuario autenticado o anónimo
        if request.user.is_authenticated:
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        else:
            cart_id = request.session.get('cart_id')
            if not cart_id:
                return JsonResponse({'success': False, 'message': 'Carrito no encontrado'})
            cart_item = get_object_or_404(CartItem, id=item_id, cart__id=cart_id, cart__user__isnull=True)
        
        cart = cart_item.cart
        
        # Obtener información de moneda del usuario
        user_country = get_user_country(request, request.user)
        user_currency = get_currency_for_country(user_country)
        
        cart_item.delete()
        
        # Recalcular total del carrito
        cart_items = cart.items.all()
        cart_total_converted = 0
        
        for item in cart_items:
            item_service_prices = get_service_prices_for_user(item.service, request, request.user)
            item_unit_price_key = item.billing_cycle
            if item_unit_price_key in item_service_prices:
                item_unit_price_converted = item_service_prices[item_unit_price_key]['amount']
            else:
                item_unit_price_original = item.get_unit_price()
                item_unit_price_converted = convert_price_to_currency(item_unit_price_original, user_currency)
            
            cart_total_converted += item_unit_price_converted * item.quantity
        
        return JsonResponse({
            'success': True,
            'message': 'Servicio removido del carrito',
            'cart_items_count': cart.get_items_count(),
            'cart_total': float(cart_total_converted)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

def checkout(request):
    """Proceso de checkout con integración de Wompi, ahora público y soporta usuarios anónimos"""
    # Obtener carrito según usuario autenticado o sesión
    if request.user.is_authenticated:
        if not request.user.is_client():
            return redirect('adminpanel:admin_dashboard')
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        cart = None
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id, user__isnull=True)
            except Cart.DoesNotExist:
                cart = None
        if not cart:
            # En lugar de redirigir inmediatamente, mostrar un mensaje más amigable
            messages.warning(request, 'Tu carrito está vacío. Agrega algunos productos antes de proceder al checkout.')
            return redirect('accounts:cart')  # Redirigir al carrito en lugar del catálogo
    
    cart_items = cart.items.all()
    if not cart_items:
        # En lugar de redirigir inmediatamente, mostrar un mensaje más amigable
        messages.warning(request, 'Tu carrito está vacío. Agrega algunos productos antes de proceder al checkout.')
        return redirect('accounts:cart')  # Redirigir al carrito en lugar del catálogo
    
    # Obtener información de moneda del usuario
    if request.user.is_authenticated:
        user_country = get_user_country(request, request.user)
        user_currency = get_currency_for_country(user_country)
    else:
        user_country = get_user_country(request)
        user_currency = get_currency_for_country(user_country)
    
    # Procesar precios de items del carrito para mostrar en checkout
    cart_items_with_prices = []
    cart_total_converted = 0
    
    for item in cart_items:
        service_prices = get_service_prices_for_user(item.service, request, request.user if request.user.is_authenticated else None)
        unit_price_key = item.billing_cycle
        if unit_price_key in service_prices:
            unit_price_converted = service_prices[unit_price_key]['amount']
            unit_price_formatted = service_prices[unit_price_key]['formatted']
        else:
            unit_price_original = item.get_unit_price()
            unit_price_converted = convert_price_to_currency(unit_price_original, user_currency)
            unit_price_formatted = format_price(unit_price_converted, user_currency)
        
        item_total_converted = unit_price_converted * item.quantity
        item_total_formatted = format_price(item_total_converted, user_currency)
        
        item.unit_price_converted = unit_price_converted
        item.unit_price_formatted = unit_price_formatted
        item.total_converted = item_total_converted
        item.total_formatted = item_total_formatted
        item.user_currency = user_currency
        
        cart_items_with_prices.append(item)
        cart_total_converted += item_total_converted
    
    cart_total_formatted = format_price(cart_total_converted, user_currency)
    
    # No verificar órdenes pendientes para anónimos
    if request.user.is_authenticated:
        pending_orders = Order.objects.filter(
            user=request.user,
            status__in=['pending', 'processing']
        ).prefetch_related('items__service')
        if pending_orders.exists():
            cart_service_ids = set(item.service.id for item in cart_items)
            for pending_order in pending_orders:
                order_service_ids = set(item.service.id for item in pending_order.items.all())
                if cart_service_ids.intersection(order_service_ids):
                    from django.utils.safestring import mark_safe
                    messages.warning(
                        request, 
                        mark_safe(f'Ya tienes una orden pendiente <strong>#{pending_order.order_number}</strong> con algunos de estos servicios. '
                        f'<a href="/accounts/orders/{pending_order.order_number}/" class="alert-link">Ver orden y pagar</a> '
                        f'o espera a que se complete antes de crear una nueva.')
                    )
                    return redirect('accounts:cart')
    
    wompi_config = WompiConfiguration.objects.filter(is_active=True).first()
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'manual')
        try:
            with transaction.atomic():
                # Crear orden con precios convertidos
                if request.user.is_authenticated:
                    order = Order.objects.create(
                        user=request.user,
                        subtotal=cart_total_converted,
                        tax_amount=0,
                        total_amount=cart_total_converted,
                        billing_name=request.POST.get('billing_name', f"{request.user.first_name} {request.user.last_name}"),
                        billing_email=request.POST.get('billing_email', request.user.email),
                        billing_address=request.POST.get('billing_address', request.user.address or ''),
                        notes=request.POST.get('notes', '')
                    )
                else:
                    # Para anónimos, pedir datos de facturación en el formulario
                    order = Order.objects.create(
                        user=None,  # O crear un usuario temporal si lo deseas
                        subtotal=cart_total_converted,
                        tax_amount=0,
                        total_amount=cart_total_converted,
                        billing_name=request.POST.get('billing_name', ''),
                        billing_email=request.POST.get('billing_email', ''),
                        billing_address=request.POST.get('billing_address', ''),
                        notes=request.POST.get('notes', '')
                    )
                
                for cart_item in cart_items_with_prices:
                    OrderItem.objects.create(
                        order=order,
                        service=cart_item.service,
                        service_name=cart_item.service.name,
                        billing_cycle=cart_item.billing_cycle,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.unit_price_converted,
                        total_price=cart_item.total_converted,
                        domain_name=cart_item.domain_name,
                        notes=cart_item.notes
                    )
                
                if payment_method == 'wompi' and wompi_config and WompiService:
                    try:
                        wompi_service = WompiService(wompi_config)
                        wompi_payment_method = request.POST.get('wompi_payment_method', 'CARD')
                        payment_kwargs = {}
                        if wompi_payment_method == 'NEQUI':
                            payment_kwargs['phone_number'] = request.POST.get('nequi_phone')
                        elif wompi_payment_method == 'PSE':
                            payment_kwargs.update({
                                'bank_code': request.POST.get('pse_bank'),
                                'user_type': request.POST.get('pse_user_type', '0'),
                                'user_legal_id_type': request.POST.get('pse_id_type', 'CC'),
                                'user_legal_id': request.POST.get('pse_id_number')
                            })
                        wompi_transaction = wompi_service.create_transaction(
                            order=order,
                            payment_method=wompi_payment_method,
                            **payment_kwargs
                        )
                        cart_items.delete()
                        payment_url = wompi_transaction.wompi_response.get('data', {}).get('payment_link', {}).get('permalink')
                        if payment_url:
                            return redirect(payment_url)
                        else:
                            messages.success(request, f'Orden #{order.order_number} creada. Procesando pago...')
                            return redirect('accounts:order_confirmation', order_number=order.order_number)
                    except Exception as e:
                        logger.error(f"Error procesando pago con Wompi: {e}")
                        messages.error(request, f'Error procesando el pago: {str(e)}')
                        return render(request, 'accounts/checkout.html', {
                            'cart': cart,
                            'cart_items': cart_items_with_prices,
                            'cart_total': cart_total_converted,
                            'cart_total_formatted': cart_total_formatted,
                            'user_country': user_country,
                            'user_currency': user_currency,
                            'user': request.user,
                            'wompi_config': wompi_config,
                            'error': str(e)
                        })
                else:
                    order.status = 'pending'
                    order.save()
                    cart_items.delete()
                    
                    # Crear cliente automáticamente cuando se completa la orden
                    try:
                        create_or_update_client_from_order(order)
                    except Exception as e:
                        logger.error(f"Error creando cliente desde orden #{order.order_number}: {e}")
                    
                    messages.success(request, f'Orden #{order.order_number} creada exitosamente.')
                    return redirect('accounts:order_confirmation', order_number=order.order_number)
        except Exception as e:
            logger.error(f"Error en checkout: {e}")
            messages.error(request, f'Error procesando la orden: {str(e)}')
    
    payment_methods = []
    pse_banks = []
    if wompi_config and WompiService:
        try:
            wompi_service = WompiService(wompi_config)
            payment_methods_data = wompi_service.get_payment_methods()
            payment_methods = payment_methods_data.get('data', [])
            pse_banks_data = wompi_service.get_pse_banks()
            pse_banks = pse_banks_data.get('data', [])
        except Exception as e:
            logger.error(f"Error obteniendo métodos de pago: {e}")
    
    context = {
        'cart': cart,
        'cart_items': cart_items_with_prices,
        'cart_total': cart_total_converted,
        'cart_total_formatted': cart_total_formatted,
        'user_country': user_country,
        'user_currency': user_currency,
        'user': request.user,
        'wompi_config': wompi_config,
        'payment_methods': payment_methods,
        'pse_banks': pse_banks,
    }
    
    return render(request, 'accounts/checkout.html', context)

@login_required
def order_confirmation(request, order_number):
    """Confirmación de orden, ahora pública y soporta órdenes de usuarios anónimos"""
    # Buscar la orden por número
    order = get_object_or_404(Order, order_number=order_number)
    # Si la orden es de usuario autenticado, verificar que sea el dueño
    if order.user is not None and request.user.is_authenticated:
        if order.user != request.user:
            return redirect('accounts:login')
    # Obtener información de moneda del usuario
    if request.user.is_authenticated:
        user_country = get_user_country(request, request.user)
        user_currency = get_currency_for_country(user_country)
    else:
        user_country = get_user_country(request)
        user_currency = get_currency_for_country(user_country)
    # Procesar precios de la orden para formatear correctamente
    if order.total_amount > 1000 and user_currency == 'COP':
        order.total_formatted = format_price(order.total_amount, 'COP')
        order.subtotal_formatted = format_price(order.subtotal, 'COP')
        order.tax_formatted = format_price(order.tax_amount, 'COP')
        order.currency = 'COP'
    elif order.total_amount <= 1000 and user_currency == 'COP':
        total_converted = convert_price_to_currency(order.total_amount, 'COP')
        subtotal_converted = convert_price_to_currency(order.subtotal, 'COP')
        tax_converted = convert_price_to_currency(order.tax_amount, 'COP')
        order.total_formatted = format_price(total_converted, 'COP')
        order.subtotal_formatted = format_price(subtotal_converted, 'COP')
        order.tax_formatted = format_price(tax_converted, 'COP')
        order.currency = 'COP'
    else:
        order.total_formatted = format_price(order.total_amount, 'USD')
        order.subtotal_formatted = format_price(order.subtotal, 'USD')
        order.tax_formatted = format_price(order.tax_amount, 'USD')
        order.currency = 'USD'
    for item in order.items.all():
        if order.currency == 'COP' and item.total_price <= 1000:
            item.total_formatted = format_price(convert_price_to_currency(item.total_price, 'COP'), 'COP')
            item.unit_formatted = format_price(convert_price_to_currency(item.unit_price, 'COP'), 'COP')
        else:
            item.total_formatted = format_price(item.total_price, order.currency)
            item.unit_formatted = format_price(item.unit_price, order.currency)
    context = {
        'order': order,
        'user_country': user_country,
        'user_currency': user_currency,
    }
    return render(request, 'accounts/order_confirmation.html', context)

@login_required
def my_orders(request):
    """Mis órdenes"""
    if not request.user.is_client():
        return redirect('adminpanel:admin_dashboard')
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Obtener información de moneda del usuario
    user_country = get_user_country(request, request.user)
    user_currency = get_currency_for_country(user_country)
    
    # Procesar órdenes para formatear precios
    orders_with_formatted_prices = []
    for order in orders:
        # Para órdenes nuevas (creadas después de la implementación), los precios ya están convertidos
        # Para órdenes antiguas, necesitamos convertir desde USD
        
        # Detectar si la orden fue creada con el nuevo sistema (aproximadamente)
        # Si el total está en un rango típico de COP (> 1000), probablemente ya está convertido
        if order.total_amount > 1000 and user_currency == 'COP':
            # Probablemente ya está en COP
            order.total_formatted = format_price(order.total_amount, 'COP')
            order.subtotal_formatted = format_price(order.subtotal, 'COP')
            order.currency = 'COP'
        elif order.total_amount <= 1000 and user_currency == 'COP':
            # Probablemente está en USD, convertir
            total_converted = convert_price_to_currency(order.total_amount, 'COP')
            subtotal_converted = convert_price_to_currency(order.subtotal, 'COP')
            order.total_formatted = format_price(total_converted, 'COP')
            order.subtotal_formatted = format_price(subtotal_converted, 'COP')
            order.currency = 'COP'
        else:
            # Mostrar en USD
            order.total_formatted = format_price(order.total_amount, 'USD')
            order.subtotal_formatted = format_price(order.subtotal, 'USD')
            order.currency = 'USD'
        
        # Procesar items de la orden
        for item in order.items.all():
            if order.currency == 'COP' and item.total_price <= 1000:
                # Convertir precio del item si es necesario
                item.total_formatted = format_price(convert_price_to_currency(item.total_price, 'COP'), 'COP')
                item.unit_formatted = format_price(convert_price_to_currency(item.unit_price, 'COP'), 'COP')
            else:
                item.total_formatted = format_price(item.total_price, order.currency)
                item.unit_formatted = format_price(item.unit_price, order.currency)
        
        orders_with_formatted_prices.append(order)
    
    context = {
        'orders': orders_with_formatted_prices,
        'user_country': user_country,
        'user_currency': user_currency,
    }
    
    return render(request, 'accounts/my_orders.html', context)

@login_required
def order_detail(request, order_number):
    """Detalle de orden"""
    if not request.user.is_client():
        return redirect('adminpanel:admin_dashboard')
    
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    # Obtener información de moneda del usuario
    user_country = get_user_country(request, request.user)
    user_currency = get_currency_for_country(user_country)
    
    # Procesar precios de la orden para formatear correctamente
    # Detectar si la orden fue creada con el nuevo sistema
    if order.total_amount > 1000 and user_currency == 'COP':
        # Probablemente ya está en COP
        order.total_formatted = format_price(order.total_amount, 'COP')
        order.subtotal_formatted = format_price(order.subtotal, 'COP')
        order.tax_formatted = format_price(order.tax_amount, 'COP')
        order.currency = 'COP'
    elif order.total_amount <= 1000 and user_currency == 'COP':
        # Probablemente está en USD, convertir
        total_converted = convert_price_to_currency(order.total_amount, 'COP')
        subtotal_converted = convert_price_to_currency(order.subtotal, 'COP')
        tax_converted = convert_price_to_currency(order.tax_amount, 'COP')
        order.total_formatted = format_price(total_converted, 'COP')
        order.subtotal_formatted = format_price(subtotal_converted, 'COP')
        order.tax_formatted = format_price(tax_converted, 'COP')
        order.currency = 'COP'
    else:
        # Mostrar en USD
        order.total_formatted = format_price(order.total_amount, 'USD')
        order.subtotal_formatted = format_price(order.subtotal, 'USD')
        order.tax_formatted = format_price(order.tax_amount, 'USD')
        order.currency = 'USD'
    
    # Procesar items de la orden
    for item in order.items.all():
        if order.currency == 'COP' and item.total_price <= 1000:
            # Convertir precio del item si es necesario
            item.total_formatted = format_price(convert_price_to_currency(item.total_price, 'COP'), 'COP')
            item.unit_formatted = format_price(convert_price_to_currency(item.unit_price, 'COP'), 'COP')
        else:
            item.total_formatted = format_price(item.total_price, order.currency)
            item.unit_formatted = format_price(item.unit_price, order.currency)
    
    context = {
        'order': order,
        'user_country': user_country,
        'user_currency': user_currency,
    }
    
    return render(request, 'accounts/order_detail.html', context)

@login_required
@require_http_methods(["POST"])
def retry_payment(request, order_number):
    """Reintentar pago de una orden"""
    if not request.user.is_client():
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    try:
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        
        # Verificar que la orden pueda ser re-pagada
        if order.status not in ['pending', 'failed']:
            return JsonResponse({'error': 'Esta orden no puede ser re-pagada'}, status=400)
        
        # Verificar si ya tiene una transacción pendiente
        if hasattr(order, 'wompi_transaction') and order.wompi_transaction.status == 'PENDING':
            return JsonResponse({'error': 'Ya existe una transacción pendiente para esta orden'}, status=400)
        
        # Verificar configuración de Wompi
        wompi_config = WompiConfiguration.objects.filter(is_active=True).first()
        if not wompi_config or not WompiService:
            return JsonResponse({'error': 'Wompi no está configurado'}, status=500)
        
        # Obtener parámetros del método de pago
        wompi_payment_method = request.POST.get('wompi_payment_method', 'CARD')
        
        payment_kwargs = {}
        if wompi_payment_method == 'NEQUI':
            payment_kwargs['phone_number'] = request.POST.get('nequi_phone')
        elif wompi_payment_method == 'PSE':
            payment_kwargs.update({
                'bank_code': request.POST.get('pse_bank'),
                'user_type': request.POST.get('pse_user_type', '0'),
                'user_legal_id_type': request.POST.get('pse_id_type', 'CC'),
                'user_legal_id': request.POST.get('pse_id_number')
            })
        
        # Crear nueva transacción en Wompi
        wompi_service = WompiService(wompi_config)
        
        # Si ya existe una transacción, eliminarla
        if hasattr(order, 'wompi_transaction'):
            order.wompi_transaction.delete()
        
        wompi_transaction = wompi_service.create_transaction(
            order=order,
            payment_method=wompi_payment_method,
            **payment_kwargs
        )
        
        # Actualizar estado de la orden
        order.status = 'pending'
        order.save()
        
        # Obtener URL de pago
        payment_url = wompi_transaction.wompi_response.get('data', {}).get('payment_link', {}).get('permalink')
        
        if payment_url:
            return JsonResponse({
                'success': True,
                'payment_url': payment_url,
                'message': 'Transacción creada exitosamente'
            })
        else:
            return JsonResponse({
                'success': True,
                'message': 'Transacción creada. Procesando pago...',
                'redirect_url': f'/accounts/orders/{order.order_number}/'
            })
        
    except Exception as e:
        logger.error(f"Error reintentando pago: {e}")
        return JsonResponse({'error': f'Error procesando el pago: {str(e)}'}, status=500)

# Vistas para Wompi
@csrf_exempt
@require_http_methods(["POST"])
def wompi_webhook(request):
    """Webhook para recibir notificaciones de Wompi"""
    try:
        # Obtener datos del webhook
        body = request.body.decode('utf-8')
        event_data = json.loads(body)
        
        # Obtener headers de seguridad
        signature = request.META.get('HTTP_X_SIGNATURE', '')
        timestamp = request.META.get('HTTP_X_TIMESTAMP', '')
        
        # Obtener configuración de Wompi
        wompi_config = WompiConfiguration.objects.filter(is_active=True).first()
        if not wompi_config:
            logger.error("No hay configuración de Wompi activa")
            return JsonResponse({'status': 'error', 'message': 'No config'}, status=400)
        
        # Procesar evento
        if WompiService:
            wompi_service = WompiService(wompi_config)
            result = wompi_service.process_webhook_event(event_data, signature, timestamp)
            
            return JsonResponse({'status': 'success', 'processed': True})
        else:
            logger.error("WompiService no disponible")
            return JsonResponse({'status': 'error', 'message': 'Service unavailable'}, status=500)
        
    except json.JSONDecodeError:
        logger.error("JSON inválido en webhook de Wompi")
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error procesando webhook de Wompi: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def wompi_return(request):
    """URL de retorno después del pago en Wompi"""
    if not request.user.is_client():
        return redirect('adminpanel:admin_dashboard')
    
    # Obtener parámetros de la URL
    transaction_id = request.GET.get('id')
    status = request.GET.get('status')
    
    if transaction_id:
        try:
            # Buscar la transacción
            wompi_transaction = WompiTransaction.objects.get(wompi_id=transaction_id)
            
            # Actualizar estado si es necesario
            if WompiService:
                wompi_config = WompiConfiguration.objects.filter(is_active=True).first()
                if wompi_config:
                    wompi_service = WompiService(wompi_config)
                    wompi_service.update_transaction_status(transaction_id)
            
            # Redireccionar según el estado
            if wompi_transaction.status == 'APPROVED':
                messages.success(request, '¡Pago procesado exitosamente!')
                return redirect('accounts:order_confirmation', order_number=wompi_transaction.order.order_number)
            elif wompi_transaction.status == 'DECLINED':
                messages.error(request, 'El pago fue rechazado. Por favor, intenta con otro método de pago.')
                return redirect('accounts:order_detail', order_number=wompi_transaction.order.order_number)
            else:
                messages.info(request, 'Tu pago está siendo procesado. Te notificaremos cuando esté confirmado.')
                return redirect('accounts:order_detail', order_number=wompi_transaction.order.order_number)
                
        except WompiTransaction.DoesNotExist:
            messages.error(request, 'Transacción no encontrada.')
            return redirect('accounts:my_orders')
        except Exception as e:
            logger.error(f"Error procesando retorno de Wompi: {e}")
            messages.error(request, 'Error procesando el resultado del pago.')
            return redirect('accounts:my_orders')
    else:
        messages.error(request, 'Información de transacción incompleta.')
        return redirect('accounts:my_orders')

@login_required
def wompi_payment_methods(request):
    """API para obtener métodos de pago de Wompi (AJAX)"""
    if not request.user.is_client():
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    try:
        wompi_config = WompiConfiguration.objects.filter(is_active=True).first()
        if not wompi_config or not WompiService:
            return JsonResponse({'error': 'Wompi no configurado'}, status=400)
        
        wompi_service = WompiService(wompi_config)
        
        # Obtener métodos de pago
        payment_methods = wompi_service.get_payment_methods()
        
        # Obtener bancos PSE
        pse_banks = wompi_service.get_pse_banks()
        
        return JsonResponse({
            'payment_methods': payment_methods.get('data', []),
            'pse_banks': pse_banks.get('data', []),
            'public_key': wompi_config.public_key,
            'is_sandbox': wompi_config.is_sandbox
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo métodos de pago: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def wompi_transaction_status(request, transaction_id):
    """Obtener estado de transacción de Wompi (AJAX)"""
    if not request.user.is_client():
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    try:
        # Buscar transacción del usuario
        wompi_transaction = WompiTransaction.objects.get(
            wompi_id=transaction_id,
            order__user=request.user
        )
        
        # Actualizar estado desde Wompi
        if WompiService:
            wompi_config = WompiConfiguration.objects.filter(is_active=True).first()
            if wompi_config:
                wompi_service = WompiService(wompi_config)
                wompi_service.update_transaction_status(transaction_id)
                wompi_transaction.refresh_from_db()
        
        return JsonResponse({
            'status': wompi_transaction.status,
            'payment_method': wompi_transaction.payment_method,
            'amount': wompi_transaction.get_amount_in_currency(),
            'currency': wompi_transaction.currency,
            'order_number': wompi_transaction.order.order_number,
            'created_at': wompi_transaction.created_at.isoformat(),
            'paid_at': wompi_transaction.paid_at.isoformat() if wompi_transaction.paid_at else None
        })
        
    except WompiTransaction.DoesNotExist:
        return JsonResponse({'error': 'Transacción no encontrada'}, status=404)
    except Exception as e:
        logger.error(f"Error obteniendo estado de transacción: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def terms_and_conditions(request):
    """Página de términos y condiciones"""
    return render(request, 'accounts/terms_and_conditions.html')

@login_required
@require_http_methods(["POST"])
def accept_terms(request):
    """Aceptar términos y condiciones"""
    if not request.user.is_client():
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    try:
        terms_version = request.POST.get('terms_version', '1.0')
        
        # Verificar si ya aceptó esta versión
        existing_acceptance = TermsAcceptance.objects.filter(
            user=request.user,
            terms_version=terms_version
        ).first()
        
        if existing_acceptance:
            return JsonResponse({
                'status': 'already_accepted',
                'message': 'Ya has aceptado esta versión de los términos y condiciones.',
                'accepted_at': existing_acceptance.accepted_at.isoformat()
            })
        
        # Crear registro de aceptación
        acceptance = TermsAcceptance.objects.create(
            user=request.user,
            terms_version=terms_version,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Términos y condiciones aceptados correctamente.',
            'accepted_at': acceptance.accepted_at.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error aceptando términos: {e}")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)

@login_required
def check_terms_acceptance(request):
    """Verificar si el usuario ha aceptado los términos"""
    if not request.user.is_client():
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    
    try:
        terms_version = request.GET.get('terms_version', '1.0')
        
        acceptance = TermsAcceptance.objects.filter(
            user=request.user,
            terms_version=terms_version
        ).first()
        
        if acceptance:
            return JsonResponse({
                'accepted': True,
                'accepted_at': acceptance.accepted_at.isoformat()
            })
        else:
            return JsonResponse({
                'accepted': False
            })
            
    except Exception as e:
        logger.error(f"Error verificando aceptación de términos: {e}")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)

def password_reset_request(request):
    """Vista para solicitar restablecimiento de contraseña"""
    if request.user.is_authenticated:
        return redirect('accounts:client_dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if email:
            try:
                user = User.objects.get(email=email)
                if user.is_active:
                    # Generar token de restablecimiento
                    from django.contrib.auth.tokens import default_token_generator
                    from django.utils.http import urlsafe_base64_encode
                    from django.utils.encoding import force_bytes
                    from django.core.mail import send_mail
                    from django.conf import settings
                    
                    # Crear token
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    
                    # URL de restablecimiento
                    reset_url = request.build_absolute_uri(
                        reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                    )
                    
                    # Enviar email
                    subject = 'Restablecer contraseña - Megadominio.co'
                    message = f'''
Hola {user.first_name or user.username},

Has solicitado restablecer tu contraseña en Megadominio.co.

Para restablecer tu contraseña, haz clic en el siguiente enlace:

{reset_url}

Si no solicitaste este cambio, puedes ignorar este email.

Este enlace expirará en 24 horas.

Saludos,
El equipo de Megadominio.co
                    '''
                    
                    try:
                        send_mail(
                            subject,
                            message,
                            'noreply@megadominio.co',
                            [user.email],
                            fail_silently=False,
                        )
                        messages.success(request, 'Se ha enviado un enlace de restablecimiento a tu correo electrónico.')
                    except Exception as e:
                        messages.error(request, f'Error enviando el email: {str(e)}')
                else:
                    messages.error(request, 'Esta cuenta está desactivada.')
            except User.DoesNotExist:
                messages.error(request, 'No existe una cuenta con este correo electrónico.')
        else:
            messages.error(request, 'Por favor, ingresa tu correo electrónico.')
    
    return render(request, 'accounts/password_reset_request.html')

def password_reset_confirm(request, uidb64, token):
    """Vista para confirmar restablecimiento de contraseña"""
    if request.user.is_authenticated:
        return redirect('accounts:client_dashboard')
    
    try:
        from django.utils.http import urlsafe_base64_decode
        from django.contrib.auth.tokens import default_token_generator
        
        # Decodificar uid
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        
        # Verificar token
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                password1 = request.POST.get('password1')
                password2 = request.POST.get('password2')
                
                if password1 and password2:
                    if password1 == password2:
                        if len(password1) >= 8:
                            # Cambiar contraseña
                            user.set_password(password1)
                            user.save()
                            
                            messages.success(request, 'Tu contraseña ha sido restablecida exitosamente. Puedes iniciar sesión ahora.')
                            return redirect('accounts:login')
                        else:
                            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
                    else:
                        messages.error(request, 'Las contraseñas no coinciden.')
                else:
                    messages.error(request, 'Por favor, completa todos los campos.')
            
            return render(request, 'accounts/password_reset_confirm.html')
        else:
            messages.error(request, 'El enlace de restablecimiento es inválido o ha expirado.')
            return redirect('accounts:password_reset_request')
            
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'El enlace de restablecimiento es inválido.')
        return redirect('accounts:password_reset_request')
