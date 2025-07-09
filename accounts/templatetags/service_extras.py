from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def format_price(price, currency='USD'):
    """Formatea un precio según la moneda"""
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
            return f"${price:,.2f} USD"
    except (ValueError, TypeError):
        return str(price)

@register.filter
def get_price(service, billing_cycle):
    """Obtiene el precio de un servicio para un ciclo de facturación específico"""
    try:
        if hasattr(service, 'get_price'):
            return service.get_price(billing_cycle) or 0
        else:
            # Fallback manual
            price_field = f'price_{billing_cycle}'
            return getattr(service, price_field, 0) or 0
    except:
        return 0

@register.filter
def get_price_for_cycle(service, cycle):
    """Obtiene el precio de un servicio para un ciclo específico"""
    if hasattr(service, 'user_prices') and service.user_prices:
        price_info = service.user_prices.get(cycle)
        if price_info:
            return price_info.get('formatted', 'N/A')
    
    # Fallback a precios originales
    price_field = f'price_{cycle}'
    price = getattr(service, price_field, None)
    if price:
        return f"${price:,.2f}"
    return None

@register.filter
def get_currency_symbol(currency):
    """Obtiene el símbolo de la moneda"""
    symbols = {
        'USD': '$',
        'COP': '$',
        'EUR': '€',
        'GBP': '£',
    }
    return symbols.get(currency, '$')

@register.filter
def get_country_name(country_code):
    """Obtiene el nombre del país basado en el código"""
    countries = {
        'CO': 'Colombia',
        'US': 'Estados Unidos',
        'CA': 'Canadá',
        'MX': 'México',
        'AR': 'Argentina',
        'CL': 'Chile',
        'PE': 'Perú',
        'EC': 'Ecuador',
        'VE': 'Venezuela',
        'BR': 'Brasil',
        'UY': 'Uruguay',
        'PY': 'Paraguay',
        'BO': 'Bolivia',
        'CR': 'Costa Rica',
        'PA': 'Panamá',
        'GT': 'Guatemala',
        'HN': 'Honduras',
        'SV': 'El Salvador',
        'NI': 'Nicaragua',
        'DO': 'República Dominicana',
        'CU': 'Cuba',
        'PR': 'Puerto Rico',
        'ES': 'España',
        'FR': 'Francia',
        'DE': 'Alemania',
        'IT': 'Italia',
        'PT': 'Portugal',
        'GB': 'Reino Unido',
        'IE': 'Irlanda',
        'NL': 'Países Bajos',
        'BE': 'Bélgica',
        'CH': 'Suiza',
        'AT': 'Austria',
        'SE': 'Suecia',
        'NO': 'Noruega',
        'DK': 'Dinamarca',
        'FI': 'Finlandia',
        'IS': 'Islandia',
        'AU': 'Australia',
        'NZ': 'Nueva Zelanda',
        'JP': 'Japón',
        'KR': 'Corea del Sur',
        'CN': 'China',
        'IN': 'India',
        'SG': 'Singapur',
        'MY': 'Malasia',
        'TH': 'Tailandia',
        'PH': 'Filipinas',
        'ID': 'Indonesia',
        'VN': 'Vietnam',
        'ZA': 'Sudáfrica',
        'EG': 'Egipto',
        'MA': 'Marruecos',
        'NG': 'Nigeria',
        'KE': 'Kenia',
        'GH': 'Ghana',
        'IL': 'Israel',
        'AE': 'Emiratos Árabes Unidos',
        'SA': 'Arabia Saudita',
        'TR': 'Turquía',
        'RU': 'Rusia',
        'UA': 'Ucrania',
        'PL': 'Polonia',
        'CZ': 'República Checa',
        'SK': 'Eslovaquia',
        'HU': 'Hungría',
        'RO': 'Rumania',
        'BG': 'Bulgaria',
        'HR': 'Croacia',
        'SI': 'Eslovenia',
        'LT': 'Lituania',
        'LV': 'Letonia',
        'EE': 'Estonia',
    }
    return countries.get(country_code, country_code)

@register.simple_tag
def currency_info(currency, country_code=None):
    """Genera información sobre la moneda detectada"""
    currency_names = {
        'USD': 'Dólar Estadounidense',
        'COP': 'Peso Colombiano',
        'EUR': 'Euro',
        'GBP': 'Libra Esterlina',
    }
    
    currency_name = currency_names.get(currency, currency)
    country_name = get_country_name(country_code) if country_code else ''
    
    if country_code == 'CO':
        return f"Precios mostrados en {currency_name} para Colombia"
    else:
        return f"Precios mostrados en {currency_name}"

@register.inclusion_tag('accounts/currency_indicator.html')
def show_currency_indicator(currency, country_code=None):
    """Muestra un indicador de moneda"""
    return {
        'currency': currency,
        'country_code': country_code,
        'country_name': get_country_name(country_code) if country_code else '',
        'currency_symbol': get_currency_symbol(currency),
    } 