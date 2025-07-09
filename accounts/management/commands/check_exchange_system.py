from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import ExchangeRate, PurchasableService
from accounts.utils import (
    get_currency_for_country, 
    convert_price_to_currency, 
    get_service_prices_for_user,
    detect_price_currency,
    format_price
)
from decimal import Decimal
import requests

class Command(BaseCommand):
    help = 'Verifica el estado del sistema de exchange rates y monedas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar información detallada',
        )
        parser.add_argument(
            '--test-api',
            action='store_true',
            help='Probar conectividad con API de exchange rates',
        )
    
    def handle(self, *args, **options):
        verbose = options['verbose']
        test_api = options['test_api']
        
        self.stdout.write(
            self.style.SUCCESS('=== DIAGNÓSTICO DEL SISTEMA DE EXCHANGE RATES ===')
        )
        
        # 1. Verificar tasas de cambio existentes
        self.check_exchange_rates(verbose)
        
        # 2. Verificar detección de países
        self.check_country_detection(verbose)
        
        # 3. Verificar conversión de precios
        self.check_price_conversion(verbose)
        
        # 4. Verificar servicios con precios
        self.check_service_prices(verbose)
        
        # 5. Probar API si se solicita
        if test_api:
            self.test_api_connectivity()
        
        self.stdout.write(
            self.style.SUCCESS('\n=== DIAGNÓSTICO COMPLETADO ===')
        )
    
    def check_exchange_rates(self, verbose):
        """Verifica el estado de las tasas de cambio"""
        self.stdout.write('\n📊 VERIFICANDO TASAS DE CAMBIO...')
        
        try:
            # Verificar tasa USD -> COP
            usd_cop_rate = ExchangeRate.objects.filter(
                from_currency='USD', 
                to_currency='COP'
            ).first()
            
            if usd_cop_rate:
                hours_ago = (timezone.now() - usd_cop_rate.updated_at).total_seconds() / 3600
                self.stdout.write(
                    self.style.SUCCESS(f'✅ USD -> COP: {usd_cop_rate.rate} (actualizada hace {hours_ago:.1f}h)')
                )
                
                if hours_ago > 24:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Tasa antigua (>24h). Ejecutar: python manage.py update_exchange_rates')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ No hay tasa USD -> COP. Ejecutar: python manage.py update_exchange_rates')
                )
            
            # Verificar tasa COP -> USD
            cop_usd_rate = ExchangeRate.objects.filter(
                from_currency='COP', 
                to_currency='USD'
            ).first()
            
            if cop_usd_rate:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ COP -> USD: {cop_usd_rate.rate}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ No hay tasa COP -> USD')
                )
            
            # Estadísticas generales
            total_rates = ExchangeRate.objects.count()
            self.stdout.write(f'📈 Total de tasas en BD: {total_rates}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al verificar tasas: {e}')
            )
    
    def check_country_detection(self, verbose):
        """Verifica la detección de países"""
        self.stdout.write('\n🌍 VERIFICANDO DETECCIÓN DE PAÍSES...')
        
        test_countries = ['CO', 'US', 'MX', 'AR', 'ES', 'XX']
        
        for country in test_countries:
            currency = get_currency_for_country(country)
            if country == 'CO':
                expected = 'COP'
            elif country == 'XX':
                expected = 'USD'  # Fallback
            else:
                expected = 'USD'
            
            if currency == expected:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {country} -> {currency}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ {country} -> {currency} (esperado: {expected})')
                )
    
    def check_price_conversion(self, verbose):
        """Verifica la conversión de precios"""
        self.stdout.write('\n💱 VERIFICANDO CONVERSIÓN DE PRECIOS...')
        
        test_prices = [
            (100, 'USD', 'COP'),
            (400000, 'COP', 'USD'),
            (50, 'USD', 'USD'),  # Sin conversión
        ]
        
        for price, from_curr, to_curr in test_prices:
            try:
                converted = convert_price_to_currency(price, to_curr, from_curr)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {price} {from_curr} -> {converted} {to_curr}')
                )
                
                # Verificar detección automática
                detected_curr = detect_price_currency(price)
                if verbose:
                    self.stdout.write(f'   💡 Moneda detectada: {detected_curr}')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error convirtiendo {price} {from_curr} -> {to_curr}: {e}')
                )
    
    def check_service_prices(self, verbose):
        """Verifica servicios con precios"""
        self.stdout.write('\n🛍️ VERIFICANDO SERVICIOS CON PRECIOS...')
        
        services = PurchasableService.objects.filter(is_active=True)[:3]
        
        for service in services:
            try:
                # Simular request para usuario colombiano
                class MockRequest:
                    def __init__(self):
                        self.META = {'REMOTE_ADDR': '190.1.1.1'}  # IP colombiana
                
                mock_request = MockRequest()
                
                # Obtener precios
                prices = get_service_prices_for_user(service, mock_request, None)
                
                if prices:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ {service.name}: {len(prices)} precios disponibles')
                    )
                    
                    if verbose:
                        for cycle, price_info in prices.items():
                            self.stdout.write(f'   - {cycle}: {price_info.get("formatted", "N/A")}')
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  {service.name}: Sin precios')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error con servicio {service.name}: {e}')
                )
    
    def test_api_connectivity(self):
        """Prueba la conectividad con la API"""
        self.stdout.write('\n🌐 PROBANDO CONECTIVIDAD CON API...')
        
        try:
            response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=10)
            response.raise_for_status()
            
            data = response.json()
            cop_rate = data.get('rates', {}).get('COP')
            
            if cop_rate:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ API conectada. Tasa actual: 1 USD = {cop_rate} COP')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ API conectada pero sin tasa COP')
                )
                
        except requests.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error de conectividad: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error inesperado: {e}')
            ) 