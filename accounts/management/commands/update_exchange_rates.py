from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import ExchangeRate
from decimal import Decimal
import requests
import logging
from datetime import datetime, time

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Actualiza las tasas de cambio desde APIs externas - MÁXIMO 1 VEZ POR DÍA'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar actualización aunque ya se haya ejecutado hoy',
        )
        parser.add_argument(
            '--source',
            type=str,
            default='exchangerate-api',
            help='Fuente de datos (exchangerate-api, fixer, etc.)',
        )
        parser.add_argument(
            '--preferred-hour',
            type=int,
            default=8,
            help='Hora preferida para actualización (0-23, default: 8)',
        )
    
    def handle(self, *args, **options):
        force_update = options['force']
        source = options['source']
        preferred_hour = options['preferred_hour']
        
        self.stdout.write(
            self.style.SUCCESS(f'=== ACTUALIZACIÓN DIARIA DE TASAS DE CAMBIO ===')
        )
        self.stdout.write(f'Fuente: {source}')
        self.stdout.write(f'Hora preferida: {preferred_hour}:00')
        self.stdout.write(f'Forzar actualización: {force_update}')
        
        # Verificar si ya se actualizó HOY (día calendario, no 24 horas)
        if not force_update:
            if self.already_updated_today():
                return
            
            # Verificar si es la hora adecuada (solo advertencia)
            current_hour = timezone.now().hour
            if abs(current_hour - preferred_hour) > 2:  # Tolerancia de 2 horas
                self.stdout.write(
                    self.style.WARNING(f'⏰ Hora actual: {current_hour}:00. Hora preferida: {preferred_hour}:00')
                )
                self.stdout.write(
                    self.style.WARNING(f'💡 Para mejor distribución de carga, considere ejecutar cerca de las {preferred_hour}:00')
                )
        
                 # Registrar intento de actualización
        self.stdout.write(f'🔄 Iniciando actualización... ({timezone.now().strftime("%Y-%m-%d %H:%M:%S")})')
        
        # Actualizar tasas según la fuente
        if source == 'exchangerate-api':
            success = self.update_from_exchangerate_api()
        elif source == 'fixer':
            success = self.update_from_fixer()
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Fuente no soportada: {source}')
            )
            return
        
        if success:
            self.stdout.write(
                self.style.SUCCESS('✅ Actualización completada exitosamente!')
            )
            self.stdout.write(
                self.style.SUCCESS(f'⏰ Próxima actualización: mañana después de las {preferred_hour}:00')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ La actualización falló')
            )
    
    def already_updated_today(self):
        """Verifica si ya se actualizó HOY (día calendario)"""
        try:
            latest_rate = ExchangeRate.objects.filter(
                from_currency='USD',
                to_currency='COP'
            ).latest('updated_at')
            
            # Verificar si fue actualizada hoy (día calendario)
            today = timezone.now().date()
            last_update_date = latest_rate.updated_at.date()
            
            if last_update_date == today:
                update_time = latest_rate.updated_at.strftime("%H:%M:%S")
                self.stdout.write(
                    self.style.WARNING(f'⏰ Ya se actualizó HOY a las {update_time}')
                )
                self.stdout.write(
                    self.style.WARNING(f'📊 Tasa actual: 1 USD = {latest_rate.rate} COP')
                )
                self.stdout.write(
                    self.style.WARNING(f'🛡️ Use --force para forzar actualización')
                )
                return True
            else:
                days_ago = (today - last_update_date).days
                self.stdout.write(
                    self.style.SUCCESS(f'📅 Última actualización: hace {days_ago} días')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Procediendo con actualización diaria...')
                )
                return False
                
        except ExchangeRate.DoesNotExist:
            self.stdout.write(
                self.style.WARNING('⚠️ No hay tasas existentes. Creando primera tasa...')
            )
            return False
    
    def update_from_exchangerate_api(self):
        """Actualiza tasas desde exchangerate-api.com"""
        try:
            self.stdout.write('🌐 Conectando con exchangerate-api.com...')
            
            response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=10)
            response.raise_for_status()
            
            data = response.json()
            rates = data.get('rates', {})
            
            self.stdout.write(f'📡 Respuesta recibida con {len(rates)} tasas de cambio')
            
            # Actualizar tasa USD -> COP
            if 'COP' in rates:
                cop_rate = Decimal(str(rates['COP']))
                exchange_rate, created = ExchangeRate.objects.update_or_create(
                    from_currency='USD',
                    to_currency='COP',
                    defaults={
                        'rate': cop_rate,
                        'source': 'exchangerate-api'
                    }
                )
                
                action = 'Creada' if created else 'Actualizada'
                self.stdout.write(
                    self.style.SUCCESS(f'💰 {action} tasa USD -> COP: {cop_rate}')
                )
                
                # Crear tasa inversa COP -> USD
                usd_rate = Decimal('1') / cop_rate
                exchange_rate_inv, created_inv = ExchangeRate.objects.update_or_create(
                    from_currency='COP',
                    to_currency='USD',
                    defaults={
                        'rate': usd_rate,
                        'source': 'exchangerate-api'
                    }
                )
                
                action_inv = 'Creada' if created_inv else 'Actualizada'
                self.stdout.write(
                    self.style.SUCCESS(f'💰 {action_inv} tasa COP -> USD: {usd_rate}')
                )
                
                # Registro exitoso
                logger.info(f'Tasas actualizadas exitosamente: USD/COP = {cop_rate}')
                return True
                
            else:
                self.stdout.write(
                    self.style.ERROR('❌ No se encontró la tasa COP en la respuesta')
                )
                logger.error('Tasa COP no encontrada en respuesta de API')
                return False
                
        except requests.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error de conectividad: {e}')
            )
            logger.error(f'Error al obtener tasas de cambio: {e}')
            return False
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error inesperado: {e}')
            )
            logger.error(f'Error inesperado al actualizar tasas: {e}')
            return False
    
    def update_from_fixer(self):
        """Actualiza tasas desde fixer.io (requiere API key)"""
        # Implementar si se necesita en el futuro
        self.stdout.write(
            self.style.WARNING('⚠️ Fuente fixer.io no implementada aún')
        )
        return False 