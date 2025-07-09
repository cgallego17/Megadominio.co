import requests
import json
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import ExchangeRate
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """
    Obtiene la dirección IP del cliente desde la request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def verify_recaptcha_v3(token, min_score=0.5):
    """
    Verifica un token de reCAPTCHA v3
    """
    if not token:
        return False
    
    # Verificar si reCAPTCHA está habilitado
    if not getattr(settings, 'RECAPTCHA_ENABLED', True):
        return True
    
    secret_key = getattr(settings, 'RECAPTCHA_SECRET_KEY', None)
    if not secret_key:
        return False
    
    try:
        data = {
            'secret': secret_key,
            'response': token
        }
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=data,
            timeout=10
        )
        result = response.json()
        
        if result.get('success') and result.get('score', 0) >= min_score:
            return True
        
        return False
    except Exception:
        return False


def get_user_country(request, user=None):
    """
    Obtiene el país del usuario basado en diferentes fuentes
    """
    # 1. Si el usuario está autenticado y tiene país en su perfil
    if user and hasattr(user, 'country') and user.country:
        return user.country
    
    # 2. Si hay un usuario en la request y tiene país
    if hasattr(request, 'user') and request.user.is_authenticated:
        if hasattr(request.user, 'country') and request.user.country:
            return request.user.country
    
    # 3. Intentar obtener desde la IP usando un servicio de geolocalización
    try:
        client_ip = get_client_ip(request)
        
        # Usar ipapi.co para obtener la ubicación
        response = requests.get(
            f'https://ipapi.co/{client_ip}/json/',
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            country_code = data.get('country_code')
            if country_code:
                return country_code
    except Exception:
        pass
    
    # 4. Fallback: usar Colombia como país por defecto
    return 'CO'


def get_currency_for_country(country_code):
    """
    Obtiene la moneda correspondiente a un país
    Versión mejorada con más países soportados
    """
    # Mapeo de países a monedas (manteniendo solo las que soportamos)
    currency_map = {
        'CO': 'COP',  # Colombia
        'US': 'USD',  # Estados Unidos
        'CA': 'USD',  # Canadá (aproximar a USD)
        'MX': 'USD',  # México (aproximar a USD)
        'AR': 'USD',  # Argentina (aproximar a USD)
        'CL': 'USD',  # Chile (aproximar a USD)
        'PE': 'USD',  # Perú (aproximar a USD)
        'EC': 'USD',  # Ecuador (usa USD)
        'VE': 'USD',  # Venezuela (aproximar a USD)
        'BR': 'USD',  # Brasil (aproximar a USD)
        'UY': 'USD',  # Uruguay (aproximar a USD)
        'PY': 'USD',  # Paraguay (aproximar a USD)
        'BO': 'USD',  # Bolivia (aproximar a USD)
        'CR': 'USD',  # Costa Rica (aproximar a USD)
        'PA': 'USD',  # Panamá (aproximar a USD)
        'GT': 'USD',  # Guatemala (aproximar a USD)
        'HN': 'USD',  # Honduras (aproximar a USD)
        'SV': 'USD',  # El Salvador (usa USD)
        'NI': 'USD',  # Nicaragua (aproximar a USD)
        'DO': 'USD',  # República Dominicana (aproximar a USD)
        'CU': 'USD',  # Cuba (aproximar a USD)
        'ES': 'USD',  # España (aproximar a USD)
        'FR': 'USD',  # Francia (aproximar a USD)
        'DE': 'USD',  # Alemania (aproximar a USD)
        'IT': 'USD',  # Italia (aproximar a USD)
        'PT': 'USD',  # Portugal (aproximar a USD)
        'GB': 'USD',  # Reino Unido (aproximar a USD)
        'IE': 'USD',  # Irlanda (aproximar a USD)
        'NL': 'USD',  # Países Bajos (aproximar a USD)
        'BE': 'USD',  # Bélgica (aproximar a USD)
        'CH': 'USD',  # Suiza (aproximar a USD)
        'AT': 'USD',  # Austria (aproximar a USD)
        'SE': 'USD',  # Suecia (aproximar a USD)
        'NO': 'USD',  # Noruega (aproximar a USD)
        'DK': 'USD',  # Dinamarca (aproximar a USD)
        'FI': 'USD',  # Finlandia (aproximar a USD)
        'IS': 'USD',  # Islandia (aproximar a USD)
        'AU': 'USD',  # Australia (aproximar a USD)
        'NZ': 'USD',  # Nueva Zelanda (aproximar a USD)
        'JP': 'USD',  # Japón (aproximar a USD)
        'KR': 'USD',  # Corea del Sur (aproximar a USD)
        'CN': 'USD',  # China (aproximar a USD)
        'IN': 'USD',  # India (aproximar a USD)
        'SG': 'USD',  # Singapur (aproximar a USD)
        'MY': 'USD',  # Malasia (aproximar a USD)
        'TH': 'USD',  # Tailandia (aproximar a USD)
        'PH': 'USD',  # Filipinas (aproximar a USD)
        'ID': 'USD',  # Indonesia (aproximar a USD)
        'VN': 'USD',  # Vietnam (aproximar a USD)
        'ZA': 'USD',  # Sudáfrica (aproximar a USD)
        'EG': 'USD',  # Egipto (aproximar a USD)
        'MA': 'USD',  # Marruecos (aproximar a USD)
        'NG': 'USD',  # Nigeria (aproximar a USD)
        'KE': 'USD',  # Kenia (aproximar a USD)
        'GH': 'USD',  # Ghana (aproximar a USD)
        'IL': 'USD',  # Israel (aproximar a USD)
        'AE': 'USD',  # Emiratos Árabes Unidos (aproximar a USD)
        'SA': 'USD',  # Arabia Saudita (aproximar a USD)
        'TR': 'USD',  # Turquía (aproximar a USD)
        'RU': 'USD',  # Rusia (aproximar a USD)
        'UA': 'USD',  # Ucrania (aproximar a USD)
        'PL': 'USD',  # Polonia (aproximar a USD)
        'CZ': 'USD',  # República Checa (aproximar a USD)
        'SK': 'USD',  # Eslovaquia (aproximar a USD)
        'HU': 'USD',  # Hungría (aproximar a USD)
        'RO': 'USD',  # Rumania (aproximar a USD)
        'BG': 'USD',  # Bulgaria (aproximar a USD)
        'HR': 'USD',  # Croacia (aproximar a USD)
        'SI': 'USD',  # Eslovenia (aproximar a USD)
        'LT': 'USD',  # Lituania (aproximar a USD)
        'LV': 'USD',  # Letonia (aproximar a USD)
        'EE': 'USD',  # Estonia (aproximar a USD)
    }
    
    # Obtener moneda del mapeo
    currency = currency_map.get(country_code, 'USD')
    
    # Log para debugging
    logger.debug(f"País detectado: {country_code} -> Moneda: {currency}")
    
    return currency


def convert_price_to_currency(price, target_currency, from_currency='USD'):
    """
    Convierte un precio de una moneda a otra usando tasas de cambio
    Versión mejorada con mejor manejo de errores
    """
    if not price:
        return 0
    
    try:
        # Convertir a Decimal para mayor precisión
        price = Decimal(str(price))
        
        # Si la moneda origen y destino son iguales, no convertir
        if from_currency == target_currency:
            return price
        
        # Obtener tasa de cambio
        rate = ExchangeRate.get_rate(from_currency, target_currency)
        
        # Convertir precio
        converted_price = price * Decimal(str(rate))
        
        logger.debug(f"Conversión: {price} {from_currency} -> {converted_price} {target_currency} (tasa: {rate})")
        
        return converted_price
        
    except Exception as e:
        logger.error(f"Error en conversión de precio: {e}")
        logger.error(f"Precio: {price}, From: {from_currency}, To: {target_currency}")
        return price  # Retornar precio original si hay error


def format_price(price, currency='USD'):
    """
    Formatea un precio según la moneda especificada
    """
    if not price:
        return "Gratis"
    
    try:
        # Convertir a número si es string
        if isinstance(price, str):
            price = float(price.replace(',', '').replace('$', ''))
        
        price = float(price)
        
        if currency == 'COP':
            # Para pesos colombianos, sin decimales
            return f"${price:,.0f} COP"
        else:
            # Para USD y otras monedas, con decimales
            return f"${price:,.2f} {currency}"
    except (ValueError, TypeError):
        return str(price)


def get_service_prices_for_user(service, request, user=None):
    """
    Obtiene los precios de un servicio convertidos a la moneda del usuario
    Versión mejorada que maneja tanto servicios del home como servicios comprables
    """
    # Obtener información del usuario
    user_country = get_user_country(request, user)
    user_currency = get_currency_for_country(user_country)
    
    # Obtener precios del servicio
    prices = {}
    
    # Verificar si es un servicio del home (Servicio) o un servicio comprable (PurchasableService)
    if hasattr(service, 'purchasable_services'):
        # Es un servicio del home, obtener precios de sus servicios comprables
        logger.debug(f"Obteniendo precios para servicio del home: {service.nombre}")
        
        # Obtener el servicio comprable más representativo (el primero activo)
        purchasable_service = service.purchasable_services.filter(is_active=True).first()
        
        if purchasable_service:
            # Obtener precios del servicio comprable
            prices = get_purchasable_service_prices(purchasable_service, user_currency)
            logger.debug(f"Precios obtenidos de servicio comprable: {purchasable_service.name}")
        else:
            # Si no hay servicios comprables, usar precio estático si existe
            if hasattr(service, 'precio') and service.precio:
                prices = get_static_price_info(service.precio, user_currency)
                logger.debug(f"Usando precio estático: {service.precio}")
            else:
                logger.warning(f"Servicio {service.nombre} no tiene servicios comprables ni precio estático")
    else:
        # Es un servicio comprable, usar función original
        logger.debug(f"Obteniendo precios para servicio comprable: {service.name}")
        prices = get_purchasable_service_prices(service, user_currency)
    
    return prices


def get_purchasable_service_prices(service, user_currency):
    """
    Obtiene los precios de un servicio comprable específico
    """
    prices = {}
    
    # Ciclos de facturación disponibles
    billing_cycles = ['monthly', 'quarterly', 'semiannual', 'annual', 'biennial', 'one_time']
    
    for cycle in billing_cycles:
        price_field = f'price_{cycle}'
        if hasattr(service, price_field):
            original_price = getattr(service, price_field)
            
            if original_price and original_price > 0:
                try:
                    # Convertir precio a la moneda del usuario
                    converted_price = convert_price_to_currency(
                        original_price, 
                        user_currency, 
                        'USD'  # Asumimos que los precios base están en USD
                    )
                    
                    # Formatear precio
                    formatted_price = format_price(converted_price, user_currency)
                    
                    prices[cycle] = {
                        'original': original_price,
                        'converted': float(converted_price),
                        'formatted': formatted_price,
                        'currency': user_currency
                    }
                    
                    logger.debug(f"Precio {cycle}: {original_price} USD -> {formatted_price}")
                    
                except Exception as e:
                    logger.error(f"Error al convertir precio {cycle}: {e}")
                    continue
    
    return prices


def get_static_price_info(precio_texto, user_currency):
    """
    Convierte un precio estático de texto a formato estructurado
    """
    prices = {}
    
    try:
        # Extraer número del texto (ej: "Desde $999" -> 999)
        import re
        numeros = re.findall(r'\d+[.,]?\d*', precio_texto)
        
        if numeros:
            precio_base = float(numeros[0].replace(',', ''))
            
            # Detectar si el precio está en COP o USD
            if 'cop' in precio_texto.lower() or precio_base > 10000:
                from_currency = 'COP'
            else:
                from_currency = 'USD'
            
            # Convertir a moneda del usuario
            converted_price = convert_price_to_currency(precio_base, user_currency, from_currency)
            formatted_price = format_price(converted_price, user_currency)
            
            # Crear entrada para "desde" (se puede usar como one_time)
            prices['one_time'] = {
                'original': precio_base,
                'converted': float(converted_price),
                'formatted': formatted_price,
                'currency': user_currency,
                'is_static': True
            }
            
            logger.debug(f"Precio estático: {precio_texto} -> {formatted_price}")
            
    except Exception as e:
        logger.error(f"Error al procesar precio estático '{precio_texto}': {e}")
    
    return prices


def get_service_best_price(service, user_currency):
    """
    Obtiene el mejor precio (más barato) de un servicio para mostrar en listados
    """
    prices = {}
    
    # Si es servicio del home, obtener del servicio comprable más barato
    if hasattr(service, 'purchasable_services'):
        purchasable_services = service.purchasable_services.filter(is_active=True)
        
        if purchasable_services.exists():
            best_price = None
            best_formatted = None
            best_period = None
            
            for purchasable in purchasable_services:
                service_prices = get_purchasable_service_prices(purchasable, user_currency)
                
                for cycle, price_info in service_prices.items():
                    if best_price is None or price_info['converted'] < best_price:
                        best_price = price_info['converted']
                        best_formatted = price_info['formatted']
                        best_period = cycle
            
            if best_price:
                prices['best_price'] = {
                    'converted': best_price,
                    'formatted': best_formatted,
                    'period': best_period,
                    'currency': user_currency
                }
    
    return prices


def detect_price_currency(price, user_currency='USD'):
    """
    Detecta si un precio está en COP o USD basado en su magnitud
    y la moneda esperada del usuario
    """
    if not price:
        return 'USD'
    
    price = float(price)
    
    # Rangos típicos para detectar moneda
    # USD: $5 - $5,000 (servicios web típicos)
    # COP: $20,000 - $20,000,000 (equivalente en pesos)
    
    if price >= 10000:  # Probablemente COP
        return 'COP'
    elif price <= 5000:  # Probablemente USD
        return 'USD'
    else:
        # Rango ambiguo, usar la moneda del usuario
        return user_currency


def ensure_price_in_currency(price, target_currency, assumed_currency=None):
    """
    Asegura que un precio esté en la moneda correcta
    Si no está seguro, convierte desde la moneda asumida
    """
    if not price:
        return 0
    
    # Detectar moneda actual del precio si no se especifica
    if assumed_currency is None:
        assumed_currency = detect_price_currency(price, target_currency)
    
    # Si ya está en la moneda correcta, retornar tal como está
    if assumed_currency == target_currency:
        return price
    
    # Convertir a la moneda objetivo
    return convert_price_to_currency(price, target_currency, assumed_currency)


def format_order_prices(order, user_currency):
    """
    Formatea los precios de una orden según la moneda del usuario
    Simplifica la lógica compleja que había en las vistas
    """
    try:
        # Detectar y convertir precios
        total_in_currency = ensure_price_in_currency(order.total_amount, user_currency)
        subtotal_in_currency = ensure_price_in_currency(order.subtotal, user_currency)
        tax_in_currency = ensure_price_in_currency(order.tax_amount, user_currency)
        
        # Formatear precios
        order.total_formatted = format_price(total_in_currency, user_currency)
        order.subtotal_formatted = format_price(subtotal_in_currency, user_currency)
        order.tax_formatted = format_price(tax_in_currency, user_currency)
        order.currency = user_currency
        
        logger.debug(f"Orden {order.order_number} formateada en {user_currency}")
        
        return order
        
    except Exception as e:
        logger.error(f"Error al formatear precios de orden {order.order_number}: {e}")
        # Fallback a formato USD
        order.total_formatted = format_price(order.total_amount, 'USD')
        order.subtotal_formatted = format_price(order.subtotal, 'USD')
        order.tax_formatted = format_price(order.tax_amount, 'USD')
        order.currency = 'USD'
        return order 