from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import Servicio
from proyectos.models import Proyecto
from accounts.models import PurchasableService, ServiceCategory, Cart, CartItem, Order, OrderItem
from accounts.utils import get_user_country, get_currency_for_country, get_service_prices_for_user, convert_price_to_currency, format_price

# Create your views here.

def home(request):
    '''Vista principal del home'''
    # Definir orden de vendibilidad basado en análisis del mercado colombiano 2024
    # Orden actualizado según demanda real del mercado tecnológico con nombres exactos
    popularity_order = [
        'Desarrollo Web',                            # 95% demanda - Más vendible
        'Hosting',                                   # 90% demanda - Servicio recurrente
        'Dominios',                                  # 85% demanda - Esencial
        'SSL y Antivirus para Empresas',             # 80% demanda - Seguridad crítica
        'Correo Empresarial',                        # 75% demanda - Profesionalismo (nombre corregido)
        'Ecommerce',                                 # 60% demanda - Crecimiento digital
        'Desarrollo de Software',                    # 40% demanda - Empresas medianas/grandes (nombre corregido)
        'Asesorías Tecnológicas',                    # 35% demanda - Consultoría (nombre corregido)
        'Redes y Servidores',                        # 25% demanda - Empresas establecidas (nombre corregido)
        'Soluciones IoT',                            # 15% demanda - Sector emergente
        'WordPress'                                  # Servicio complementario (si existe)
    ]
    
    # Obtener todos los servicios
    all_services = Servicio.objects.all()
    
    # Ordenar servicios según popularidad
    ordered_services = []
    
    # Primero agregar servicios según el orden de popularidad
    for service_name in popularity_order:
        matching_services = all_services.filter(nombre=service_name)
        if matching_services.exists():
            ordered_services.extend(matching_services)
    
    # Luego agregar cualquier servicio restante que no esté en la lista
    for service in all_services:
        if service not in ordered_services:
            ordered_services.append(service)
    
    # Obtener precios para cada servicio según el usuario
    services_with_prices = []
    for servicio in ordered_services:
        try:
            prices = get_service_prices_for_user(servicio, request, request.user if request.user.is_authenticated else None)
            services_with_prices.append({
                'servicio': servicio,
                'prices': prices
            })
        except Exception as e:
            # Si hay error con precios, usar servicio sin precios
            services_with_prices.append({
                'servicio': servicio,
                'prices': []
            })
    
    # Obtener proyectos para mostrar en el home
    proyectos = Proyecto.objects.all()[:6]  # Mostrar solo 6 proyectos
    
    context = {
        'services_with_prices': services_with_prices,
        'proyectos': proyectos,
        'market_analysis': {
            'total_services': len(ordered_services),
            'top_services': popularity_order[:5],  # Top 5 más vendibles
            'market_year': '2024',
            'analysis_basis': 'Mercado Colombiano',
            'price_ranges': {
                'web_development': '$899 - $3,499',
                'hosting': '$6.99/mes - $299/año',
                'domains': '$19.99 - $99.99/año',
                'ssl': '$49.99 - $279.99/año',
                'email': '$7.99/mes - $259/año'
            }
        }
    }
    
    return render(request, 'servicios/home.html', context)

def servicio_detail(request, servicio_slug):
    '''Vista para mostrar lista de servicios vendibles de un servicio (Nivel 2)'''
    # Buscar el servicio usando el método estático get_by_slug
    try:
        servicio = Servicio.get_by_slug(servicio_slug)
        if not servicio:
            raise Http404("Servicio no encontrado")
    except Exception as e:
        # Si hay error, solo permitir compatibilidad con IDs antiguos temporalmente
        if servicio_slug.isdigit():
            servicio = get_object_or_404(Servicio, id=servicio_slug)
        else:
            raise Http404("Servicio no encontrado")
    
    # Obtener servicios comprables asociados y activos
    servicios_comprables = PurchasableService.objects.filter(
        home_service=servicio, 
        is_active=True
    ).order_by('-is_featured', 'name')
    
    # Obtener información de moneda del usuario
    user_country = get_user_country(request, request.user if request.user.is_authenticated else None)
    user_currency = get_currency_for_country(user_country)
    
    # Procesar servicios vendibles con información básica para la lista
    servicios_con_precios = []
    for servicio_comprable in servicios_comprables:
        try:
            # Obtener precios convertidos
            prices = get_service_prices_for_user(servicio_comprable, request, request.user if request.user.is_authenticated else None)
            
            # Obtener ciclos de facturación disponibles
            billing_cycles = []
            cycle_map = {
                'monthly': {'label': 'Mensual', 'price': servicio_comprable.price_monthly},
                'quarterly': {'label': 'Trimestral', 'price': servicio_comprable.price_quarterly},
                'semiannual': {'label': 'Semestral', 'price': servicio_comprable.price_semiannual},
                'annual': {'label': 'Anual', 'price': servicio_comprable.price_annual},
                'biennial': {'label': 'Bienal', 'price': servicio_comprable.price_biennial},
                'one_time': {'label': 'Pago Único', 'price': servicio_comprable.price_one_time},
            }
            
            for cycle, info in cycle_map.items():
                if info['price'] and info['price'] > 0:
                    cycle_data = {
                        'cycle': cycle,
                        'label': info['label'],
                        'price_original': info['price'],
                        'price_converted': prices.get(cycle, {}).get('amount', info['price']),
                        'price_formatted': prices.get(cycle, {}).get('formatted', f"${info['price']}"),
                        'currency': user_currency
                    }
                    billing_cycles.append(cycle_data)
            
            # Determinar precio "desde" (más bajo disponible)
            precio_desde = None
            if billing_cycles:
                precio_desde = min(billing_cycles, key=lambda x: x['price_converted'])
            
            servicios_con_precios.append({
                'servicio': servicio_comprable,
                'precio_desde': precio_desde,
                'billing_cycles': billing_cycles,
                'features_count': len(servicio_comprable.features) if servicio_comprable.features else 0,
                'is_featured': servicio_comprable.is_featured,
                'requires_domain': servicio_comprable.requires_domain,
                'setup_fee': servicio_comprable.setup_fee
            })
            
        except Exception as e:
            # Si hay error con un servicio, continuar con los demás
            print(f"Error procesando servicio {servicio_comprable.name}: {e}")
            continue
    
    # Estadísticas del servicio
    total_servicios = len(servicios_con_precios)
    servicios_destacados = len([s for s in servicios_con_precios if s['is_featured']])
    
    context = {
        'servicio': servicio,
        'servicios_con_precios': servicios_con_precios,
        'user_country': user_country,
        'user_currency': user_currency,
        'stats': {
            'total_servicios': total_servicios,
            'servicios_destacados': servicios_destacados,
            'moneda': user_currency
        },
        'page_title': f"{servicio.nombre} - Planes y Servicios",
        'meta_description': f"Descubre nuestros planes de {servicio.nombre.lower()}. Diferentes opciones para satisfacer tus necesidades."
    }
    
    return render(request, 'servicios/servicio_list.html', context)

def service_purchasable_detail(request, servicio_slug, service_slug):
    '''Vista para mostrar detalle completo de un servicio vendible específico (Nivel 3)'''
    # Buscar el servicio principal
    try:
        servicio = Servicio.get_by_slug(servicio_slug)
        if not servicio:
            raise Http404("Servicio no encontrado")
    except Exception as e:
        # Si hay error, solo permitir compatibilidad con IDs antiguos temporalmente
        if servicio_slug.isdigit():
            servicio = get_object_or_404(Servicio, id=servicio_slug)
        else:
            raise Http404("Servicio no encontrado")
    
    # Buscar el servicio vendible específico
    servicio_vendible = get_object_or_404(
        PurchasableService, 
        home_service=servicio, 
        slug=service_slug, 
        is_active=True
    )
    
    # Obtener información de moneda del usuario
    user_country = get_user_country(request, request.user if request.user.is_authenticated else None)
    user_currency = get_currency_for_country(user_country)
    
    # Procesar detalle completo del servicio vendible
    try:
        # Obtener precios convertidos
        prices = get_service_prices_for_user(servicio_vendible, request, request.user if request.user.is_authenticated else None)
        
        # Procesar características (features)
        features = servicio_vendible.features if servicio_vendible.features else []
        
        # Procesar especificaciones (specifications)
        specifications = servicio_vendible.specifications if servicio_vendible.specifications else {}
        
        # Obtener ciclos de facturación disponibles con precios
        billing_cycles = []
        cycle_map = {
            'monthly': {'label': 'Mensual', 'price': servicio_vendible.price_monthly},
            'quarterly': {'label': 'Trimestral', 'price': servicio_vendible.price_quarterly},
            'semiannual': {'label': 'Semestral', 'price': servicio_vendible.price_semiannual},
            'annual': {'label': 'Anual', 'price': servicio_vendible.price_annual},
            'biennial': {'label': 'Bienal', 'price': servicio_vendible.price_biennial},
            'one_time': {'label': 'Pago Único', 'price': servicio_vendible.price_one_time},
        }
        
        for cycle, info in cycle_map.items():
            if info['price'] and info['price'] > 0:
                cycle_data = {
                    'cycle': cycle,
                    'label': info['label'],
                    'price_original': info['price'],
                    'price_converted': prices.get(cycle, {}).get('amount', info['price']),
                    'price_formatted': prices.get(cycle, {}).get('formatted', f"${info['price']}"),
                    'currency': user_currency,
                    'savings': None  # Se puede calcular el ahorro comparado con mensual
                }
                billing_cycles.append(cycle_data)
        
        # Calcular ahorros comparado con precio mensual
        if len(billing_cycles) > 1:
            monthly_price = next((c for c in billing_cycles if c['cycle'] == 'monthly'), None)
            if monthly_price:
                monthly_equivalent = monthly_price['price_converted']
                for cycle in billing_cycles:
                    if cycle['cycle'] != 'monthly':
                        # Calcular precio mensual equivalente
                        multiplier = {'quarterly': 3, 'semiannual': 6, 'annual': 12, 'biennial': 24}.get(cycle['cycle'], 1)
                        if multiplier > 1:
                            monthly_equiv = cycle['price_converted'] / multiplier
                            savings_pct = ((monthly_equivalent - monthly_equiv) / monthly_equivalent) * 100
                            cycle['savings'] = max(0, round(savings_pct, 1))
        
        # Obtener servicios relacionados (otros servicios del mismo tipo)
        servicios_relacionados = PurchasableService.objects.filter(
            home_service=servicio,
            is_active=True
        ).exclude(id=servicio_vendible.id).order_by('-is_featured', 'name')[:3]
        
        # Procesar servicios relacionados con precios básicos
        relacionados_con_precios = []
        for relacionado in servicios_relacionados:
            try:
                precios_relacionado = get_service_prices_for_user(relacionado, request, request.user if request.user.is_authenticated else None)
                
                # Obtener precio "desde" más bajo
                precio_desde = None
                for cycle in ['monthly', 'quarterly', 'semiannual', 'annual', 'biennial', 'one_time']:
                    if hasattr(relacionado, f'price_{cycle}'):
                        price_attr = getattr(relacionado, f'price_{cycle}')
                        if price_attr and price_attr > 0:
                            precio_desde = {
                                'cycle': cycle,
                                'price_converted': precios_relacionado.get(cycle, {}).get('amount', price_attr),
                                'price_formatted': precios_relacionado.get(cycle, {}).get('formatted', f"${price_attr}"),
                                'currency': user_currency
                            }
                            break
                
                relacionados_con_precios.append({
                    'servicio': relacionado,
                    'precio_desde': precio_desde
                })
            except Exception as e:
                continue
        
        servicio_detallado = {
            'servicio': servicio_vendible,
            'features': features,
            'specifications': specifications,
            'billing_cycles': billing_cycles,
            'setup_fee': servicio_vendible.setup_fee,
            'requires_domain': servicio_vendible.requires_domain,
            'is_featured': servicio_vendible.is_featured,
            'prices': prices
        }
        
    except Exception as e:
        raise Http404("Error al procesar el servicio")
    
    context = {
        'servicio_principal': servicio,
        'servicio_detallado': servicio_detallado,
        'servicios_relacionados': relacionados_con_precios,
        'user_country': user_country,
        'user_currency': user_currency,
        'page_title': f"{servicio_vendible.name} - {servicio.nombre}",
        'meta_description': f"{servicio_vendible.short_description} - {servicio.nombre}. Consulta características, precios y planes disponibles."
    }
    
    return render(request, 'servicios/service_detail.html', context)



# ===============================
# VISTAS DEL CARRITO DE COMPRAS (MOVIDAS DESDE ACCOUNTS)
# ===============================

@require_http_methods(["POST"])
def add_to_cart(request):
    """Agregar servicio al carrito"""
    try:
        service_id = request.POST.get('service_id')
        billing_cycle = request.POST.get('billing_cycle')
        quantity = int(request.POST.get('quantity', 1))
        
        if not service_id:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'ID del servicio requerido'})
            else:
                messages.error(request, 'ID del servicio requerido')
                return redirect('servicios:home')
        
        # Obtener servicio
        try:
            service = PurchasableService.objects.get(id=service_id)
        except PurchasableService.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Servicio no encontrado'})
            else:
                messages.error(request, 'Servicio no encontrado')
                return redirect('servicios:home')
        
        # Si no se especifica billing_cycle, detectar automáticamente
        if not billing_cycle:
            # Obtener ciclos disponibles para este servicio
            available_cycles = service.get_available_billing_cycles()
            
            if available_cycles:
                # Usar el primer ciclo disponible (generalmente el más común)
                billing_cycle = available_cycles[0][0]
            else:
                # Fallback a monthly si no hay ciclos disponibles
                billing_cycle = 'monthly'
        
        # Validar billing_cycle
        valid_cycles = ['monthly', 'quarterly', 'semiannual', 'annual', 'biennial', 'one_time']
        if billing_cycle not in valid_cycles:
            billing_cycle = 'monthly'
        
        # Verificar que el servicio tenga precio para el ciclo seleccionado
        service_price = service.get_price(billing_cycle)
        if not service_price:
            # Si no hay precio para el ciclo seleccionado, buscar otro ciclo disponible
            available_cycles = service.get_available_billing_cycles()
            if available_cycles:
                billing_cycle = available_cycles[0][0]  # Usar el primer ciclo disponible
                service_price = service.get_price(billing_cycle)
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': 'Este servicio no tiene precios configurados'})
                else:
                    messages.error(request, 'Este servicio no tiene precios configurados')
                    return redirect('servicios:home')
        
        # Validar cantidad
        if quantity < 1 or quantity > 10:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Cantidad debe estar entre 1 y 10'})
            else:
                messages.error(request, 'Cantidad debe estar entre 1 y 10')
                return redirect('servicios:home')
        
        # Obtener o crear carrito
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            cart_id = request.session.get('cart_id')
            if cart_id:
                try:
                    cart = Cart.objects.get(id=cart_id, user__isnull=True)
                except Cart.DoesNotExist:
                    cart = None
            else:
                cart = None
            
            if not cart:
                cart = Cart.objects.create(user=None)
                request.session['cart_id'] = cart.id
        
        # Verificar si el servicio ya está en el carrito
        existing_item = cart.items.filter(service=service, billing_cycle=billing_cycle).first()
        
        if existing_item:
            # Actualizar cantidad
            new_quantity = existing_item.quantity + quantity
            if new_quantity > 10:
                new_quantity = 10
            existing_item.quantity = new_quantity
            existing_item.save()
            cart_item = existing_item
        else:
            # Crear nuevo item
            cart_item = CartItem.objects.create(
                cart=cart,
                service=service,
                billing_cycle=billing_cycle,
                quantity=quantity
            )
        
        # Si es AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{service.name} agregado al carrito',
                'cart_items_count': cart.get_items_count(),
                'cart_total': float(cart.get_total())
            })
        else:
            # Si no es AJAX, redirigir al carrito con mensaje
            messages.success(request, f'{service.name} agregado al carrito')
            return redirect('servicios:cart')
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error en add_to_cart: {str(e)}', exc_info=True)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor. Por favor, inténtalo de nuevo.'
            })
        else:
            messages.error(request, 'Error interno del servidor. Por favor, inténtalo de nuevo.')
            return redirect('servicios:home')

def cart_counter(request):
    """Endpoint para obtener contador del carrito (sin autenticación requerida)"""
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items_count = cart.get_items_count()
        except Cart.DoesNotExist:
            cart_items_count = 0
    else:
        # Para usuarios anónimos, obtener carrito de sesión
        cart_id = request.session.get('cart_id')
        cart_items_count = 0
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id, user__isnull=True)
                cart_items_count = cart.get_items_count()
            except Cart.DoesNotExist:
                pass
    
    return JsonResponse({
        'cart_items_count': cart_items_count,
        'cart_total': 0,  # Simplified for counter
        'items': []
    })

def cart_view(request):
    """Vista del carrito de compras, ahora pública y soporta usuarios anónimos"""
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
                # Limpiar ID de carrito inválido de la sesión
                request.session.pop('cart_id', None)
                cart = None
        
        if not cart:
            # Crear carrito vacío para usuarios anónimos en lugar de redirigir
            cart = Cart.objects.create(user=None)
            request.session['cart_id'] = cart.id
            request.session.modified = True
    
    cart_items = cart.items.all()
    
    # Obtener información de moneda del usuario
    if request.user.is_authenticated:
        user_country = get_user_country(request, request.user)
        user_currency = get_currency_for_country(user_country)
    else:
        user_country = get_user_country(request)
        user_currency = get_currency_for_country(user_country)
    
    # Procesar precios de items del carrito
    cart_items_with_prices = []
    cart_total_converted = 0
    
    for item in cart_items:
        # Obtener precios convertidos para el servicio
        service_prices = get_service_prices_for_user(item.service, request, request.user if request.user.is_authenticated else None)
        
        # Obtener precio unitario convertido
        unit_price_key = item.billing_cycle
        price_info = service_prices.get(unit_price_key)
        if isinstance(price_info, dict) and 'amount' in price_info:
            unit_price_converted = price_info['amount']
            unit_price_formatted = price_info.get('formatted', str(price_info['amount']))
        elif isinstance(price_info, (int, float)):
            unit_price_converted = price_info
            unit_price_formatted = format_price(unit_price_converted, user_currency)
        elif isinstance(price_info, str):
            try:
                unit_price_converted = float(price_info)
            except Exception:
                unit_price_converted = 0
            unit_price_formatted = format_price(unit_price_converted, user_currency)
        else:
            # Fallback al precio original si no hay conversión
            unit_price_original = item.get_unit_price()
            unit_price_converted = convert_price_to_currency(unit_price_original, user_currency)
            unit_price_formatted = format_price(unit_price_converted, user_currency)
        
        # Calcular total del item
        item_total_converted = unit_price_converted * item.quantity
        item_total_formatted = format_price(item_total_converted, user_currency)
        
        # Agregar precios convertidos al item
        item.unit_price_converted = unit_price_converted
        item.unit_price_formatted = unit_price_formatted
        item.total_converted = item_total_converted
        item.total_formatted = item_total_formatted
        item.user_currency = user_currency
        
        cart_items_with_prices.append(item)
        cart_total_converted += item_total_converted
    
    # Formatear total del carrito
    cart_total_formatted = format_price(cart_total_converted, user_currency)
    
    # Si es una solicitud AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'cart_items_count': cart.get_items_count(),
            'cart_total': float(cart_total_converted),
            'items': [
                {
                    'id': item.id,
                    'service_name': item.service.name,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price_converted),
                    'total_price': float(item.total_converted),
                    'billing_cycle': item.get_billing_cycle_display(),
                    'domain_name': item.domain_name or '',
                }
                for item in cart_items_with_prices
            ]
        })
    
    # Contexto para el template
    context = {
        'cart': cart,
        'cart_items': cart_items_with_prices,
        'cart_total': cart_total_converted,
        'cart_total_formatted': cart_total_formatted,
        'user_country': user_country,
        'user_currency': user_currency,
        'user': request.user,
    }
    
    return render(request, 'servicios/cart.html', context)

@require_http_methods(["POST"])
def update_cart_item(request):
    """Actualizar cantidad de un item en el carrito"""
    try:
        item_id = request.POST.get('item_id')
        quantity_str = request.POST.get('quantity')
        
        if not item_id or not quantity_str:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Datos requeridos faltantes'})
            else:
                messages.error(request, 'Datos requeridos faltantes')
                return redirect('servicios:cart')
        
        try:
            quantity = int(quantity_str)
            if quantity < 1 or quantity > 10:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': 'Cantidad debe estar entre 1 y 10'})
                else:
                    messages.error(request, 'Cantidad debe estar entre 1 y 10')
                    return redirect('servicios:cart')
        except ValueError:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Cantidad inválida'})
            else:
                messages.error(request, 'Cantidad inválida')
                return redirect('servicios:cart')
        
        # Obtener item del carrito
        try:
            cart_item = CartItem.objects.get(id=item_id)
            
            # Verificar que el usuario tenga acceso al carrito
            if request.user.is_authenticated:
                if cart_item.cart.user != request.user:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': 'No tienes permisos para modificar este carrito'})
                    else:
                        messages.error(request, 'No tienes permisos para modificar este carrito')
                        return redirect('servicios:cart')
            else:
                if cart_item.cart.user is not None:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': 'No tienes permisos para modificar este carrito'})
                    else:
                        messages.error(request, 'No tienes permisos para modificar este carrito')
                        return redirect('servicios:cart')
            
            # Actualizar cantidad
            cart_item.quantity = quantity
            cart_item.save()
            
            # Si es AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Cantidad actualizada',
                    'cart_items_count': cart_item.cart.get_items_count(),
                    'cart_total': float(cart_item.cart.get_total()),
                    'item_total': float(cart_item.get_total())
                })
            else:
                # Si no es AJAX, redirigir al carrito con mensaje
                messages.success(request, 'Cantidad actualizada')
                return redirect('servicios:cart')
            
        except CartItem.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Item no encontrado'})
            else:
                messages.error(request, 'Item no encontrado')
                return redirect('servicios:cart')
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error en update_cart_item: {str(e)}', exc_info=True)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor. Por favor, inténtalo de nuevo.'
            })
        else:
            messages.error(request, 'Error interno del servidor. Por favor, inténtalo de nuevo.')
            return redirect('servicios:cart')

@require_http_methods(["POST"])
def remove_from_cart(request):
    """Remover item del carrito"""
    try:
        item_id = request.POST.get('item_id')
        
        if not item_id:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'ID del item requerido'})
            else:
                messages.error(request, 'ID del item requerido')
                return redirect('servicios:cart')
        
        # Obtener item del carrito
        try:
            cart_item = CartItem.objects.get(id=item_id)
            
            # Verificar que el usuario tenga acceso al carrito
            if request.user.is_authenticated:
                if cart_item.cart.user != request.user:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': 'No tienes permisos para modificar este carrito'})
                    else:
                        messages.error(request, 'No tienes permisos para modificar este carrito')
                        return redirect('servicios:cart')
            else:
                if cart_item.cart.user is not None:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': 'No tienes permisos para modificar este carrito'})
                    else:
                        messages.error(request, 'No tienes permisos para modificar este carrito')
                        return redirect('servicios:cart')
            
            # Obtener información antes de eliminar
            cart = cart_item.cart
            cart_items_count = cart.get_items_count()
            
            # Eliminar item
            cart_item.delete()
            
            # Si es AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Item removido del carrito',
                    'cart_items_count': cart.get_items_count(),
                    'cart_total': float(cart.get_total())
                })
            else:
                # Si no es AJAX, redirigir al carrito con mensaje
                messages.success(request, 'Item removido del carrito')
                return redirect('servicios:cart')
            
        except CartItem.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Item no encontrado'})
            else:
                messages.error(request, 'Item no encontrado')
                return redirect('servicios:cart')
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error en remove_from_cart: {str(e)}', exc_info=True)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor. Por favor, inténtalo de nuevo.'
            })
        else:
            messages.error(request, 'Error interno del servidor. Por favor, inténtalo de nuevo.')
            return redirect('servicios:cart')

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
            return redirect('servicios:cart')  # Redirigir al carrito en lugar del catálogo
    
    cart_items = cart.items.all()
    if not cart_items:
        # En lugar de redirigir inmediatamente, mostrar un mensaje más amigable
        messages.warning(request, 'Tu carrito está vacío. Agrega algunos productos antes de proceder al checkout.')
        return redirect('servicios:cart')  # Redirigir al carrito en lugar del catálogo
    
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
        
        # Validar que el precio esté disponible y tenga la estructura correcta
        if unit_price_key in service_prices and isinstance(service_prices[unit_price_key], dict):
            price_data = service_prices[unit_price_key]
            if 'amount' in price_data and 'formatted' in price_data:
                unit_price_converted = price_data['amount']
                unit_price_formatted = price_data['formatted']
            else:
                # Si no tiene la estructura esperada, usar precio original
                unit_price_original = item.get_unit_price()
                unit_price_converted = convert_price_to_currency(unit_price_original, user_currency)
                unit_price_formatted = format_price(unit_price_converted, user_currency)
        else:
            # Si no está en service_prices o no es un diccionario, usar precio original
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
                    return redirect('servicios:cart')
    
    # Importar configuración de Wompi
    from accounts.models import WompiConfiguration
    from accounts.services import WompiService
    import logging
    logger = logging.getLogger(__name__)
    
    wompi_config = WompiConfiguration.objects.filter(is_active=True).first()
    
    # Obtener métodos de pago de Wompi (necesario para el contexto en caso de error)
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
    
    if request.method == 'POST':
        # Verificar términos y condiciones
        terms_accepted = request.POST.get('terms_accepted')
        if not terms_accepted:
            messages.error(request, 'Debes aceptar los términos y condiciones para continuar.')
            return render(request, 'servicios/checkout.html', {
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
            })
        
        payment_method = request.POST.get('payment_method', 'manual')
        try:
            from django.db import transaction
            with transaction.atomic():
                # Crear o registrar usuario si es anónimo
                user = request.user
                if not request.user.is_authenticated:
                    # Crear usuario con los datos del formulario
                    from accounts.models import User
                    from django.contrib.auth.hashers import make_password
                    import random
                    import string
                    
                    # Validar que el email no exista
                    email = request.POST.get('billing_email')
                    if User.objects.filter(email=email).exists():
                        messages.error(request, f'El correo electrónico {email} ya está registrado. Por favor, inicie sesión o use un correo diferente.')
                        return render(request, 'servicios/checkout.html', {
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
                        })
                    
                    # Validar que el teléfono no exista (si se proporciona)
                    phone = request.POST.get('phone', '').strip()
                    if phone and User.objects.filter(phone=phone).exists():
                        messages.error(request, f'El número de teléfono {phone} ya está registrado. Por favor, use un número diferente o inicie sesión.')
                        return render(request, 'servicios/checkout.html', {
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
                        })
                    
                    # Generar contraseña temporal
                    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
                    
                    # Crear usuario
                    user = User.objects.create(
                        username=email,
                        email=email,
                        first_name=request.POST.get('billing_name').split()[0] if request.POST.get('billing_name') else '',
                        last_name=' '.join(request.POST.get('billing_name').split()[1:]) if request.POST.get('billing_name') and len(request.POST.get('billing_name').split()) > 1 else '',
                        password=make_password(temp_password),
                        user_type='client',
                        address=request.POST.get('billing_address', ''),
                        phone=phone,
                        company=request.POST.get('company', '')
                    )
                    
                    # Registrar aceptación de términos
                    from accounts.models import TermsAcceptance
                    TermsAcceptance.objects.create(
                        user=user,
                        terms_version="1.0",
                        ip_address=request.META.get('REMOTE_ADDR', ''),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                    
                    # Hacer login automático
                    from django.contrib.auth import login
                    login(request, user)
                    
                    # Enviar email con credenciales (opcional)
                    # from django.core.mail import send_mail
                    # send_mail(
                    #     'Bienvenido a Megadominio.co',
                    #     f'Tu cuenta ha sido creada. Usuario: {user.email}, Contraseña: {temp_password}',
                    #     'noreply@megadominio.co',
                    #     [user.email],
                    #     fail_silently=True,
                    # )
                    
                    messages.success(request, f'Cuenta creada exitosamente. Usuario: {user.email}, Contraseña: {temp_password}')
                
                # Crear orden
                order = Order.objects.create(
                    user=user,
                    subtotal=cart_total_converted,
                    tax_amount=0,
                    total_amount=cart_total_converted,
                    billing_name=request.POST.get('billing_name', f"{user.first_name} {user.last_name}"),
                    billing_email=request.POST.get('billing_email', user.email),
                    billing_address=request.POST.get('billing_address', user.address or ''),
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
                            return redirect('servicios:order_confirmation', order_number=order.order_number)
                    except Exception as e:
                        logger.error(f"Error procesando pago con Wompi: {e}")
                        messages.error(request, f'Error procesando el pago: {str(e)}')
                        return render(request, 'servicios/checkout.html', {
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
                    messages.success(request, f'Orden #{order.order_number} creada exitosamente.')
                    return redirect('servicios:order_confirmation', order_number=order.order_number)
        except Exception as e:
            logger.error(f"Error en checkout: {e}")
            messages.error(request, f'Error procesando la orden: {str(e)}')
    
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
    
    return render(request, 'servicios/checkout.html', context)

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
    
    # Procesar items de la orden con precios convertidos
    order_items_with_prices = []
    order_total_converted = 0
    
    for item in order.items.all():
        # Obtener precios convertidos para el servicio
        service_prices = get_service_prices_for_user(item.service, request, request.user if request.user.is_authenticated else None)
        
        # Usar precio ya guardado en la orden
        item_total_converted = float(item.total_price)
        item_total_formatted = format_price(item_total_converted, user_currency)
        
        # Agregar información adicional al item
        item.total_converted = item_total_converted
        item.total_formatted = item_total_formatted
        item.user_currency = user_currency
        
        order_items_with_prices.append(item)
        order_total_converted += item_total_converted
    
    # Formatear total de la orden
    order_total_formatted = format_price(order_total_converted, user_currency)
    
    context = {
        'order': order,
        'order_items': order_items_with_prices,
        'order_total': order_total_converted,
        'order_total_formatted': order_total_formatted,
        'user_country': user_country,
        'user_currency': user_currency,
        'user': request.user,
    }
    
    return render(request, 'servicios/order_confirmation.html', context)

@require_http_methods(["POST"])
def validate_user_data(request):
    """Validación AJAX de email y teléfono"""
    from django.http import JsonResponse
    from accounts.models import User
    from django.urls import reverse
    
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    
    response_data = {
        'email_valid': True,
        'phone_valid': True,
        'email_message': '',
        'phone_message': '',
        'login_url': reverse('accounts:login')
    }
    
    # Validar email
    if email:
        if User.objects.filter(email=email).exists():
            response_data['email_valid'] = False
            response_data['email_message'] = f'El correo electrónico {email} ya está registrado. <a href="{reverse("accounts:login")}" class="text-warning">¿Ya tienes cuenta? Inicia sesión</a>'
    
    # Validar teléfono
    if phone:
        if User.objects.filter(phone=phone).exists():
            response_data['phone_valid'] = False
            response_data['phone_message'] = f'El número de teléfono {phone} ya está registrado. <a href="{reverse("accounts:login")}" class="text-warning">¿Ya tienes cuenta? Inicia sesión</a>'
    
    return JsonResponse(response_data)
