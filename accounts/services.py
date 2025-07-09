import requests
import hashlib
import hmac
import json
import logging
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from django.urls import reverse
from .models import WompiConfiguration, WompiTransaction, WompiWebhookEvent, Order

logger = logging.getLogger(__name__)

class WompiService:
    """Servicio para manejar la API de Wompi"""
    
    def __init__(self, config=None):
        """
        Inicializa el servicio con una configuración específica
        Si no se proporciona, usa la configuración activa por defecto
        """
        if config is None:
            try:
                self.config = WompiConfiguration.objects.filter(is_active=True).first()
                if not self.config:
                    raise ValueError("No hay configuración de Wompi activa")
            except WompiConfiguration.DoesNotExist:
                raise ValueError("No se encontró configuración de Wompi")
        else:
            self.config = config
        
        self.base_url = self.config.get_base_url()
        self.headers = {
            'Authorization': f'Bearer {self.config.private_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def create_acceptance_token(self):
        """Crea un token de aceptación para términos y condiciones"""
        try:
            url = f"{self.base_url}/merchants/{self.config.public_key}"
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            return data.get('data', {}).get('presigned_acceptance', {})
            
        except requests.RequestException as e:
            logger.error(f"Error creando token de aceptación: {e}")
            raise
    
    def create_payment_source_card(self, email, card_token, acceptance_token):
        """Crea una fuente de pago con tarjeta"""
        try:
            url = f"{self.base_url}/payment_sources"
            
            payload = {
                "type": "CARD",
                "token": card_token,
                "customer_email": email,
                "acceptance_token": acceptance_token
            }
            
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error creando fuente de pago: {e}")
            raise
    
    def create_transaction(self, order, payment_method='CARD', **kwargs):
        """
        Crea una transacción en Wompi
        
        Args:
            order: Instancia del modelo Order
            payment_method: Método de pago (CARD, NEQUI, PSE, etc.)
            **kwargs: Parámetros adicionales específicos del método de pago
        """
        try:
            # Crear token de aceptación
            acceptance_data = self.create_acceptance_token()
            acceptance_token = acceptance_data.get('acceptance_token')
            
            if not acceptance_token:
                raise ValueError("No se pudo obtener el token de aceptación")
            
            # Preparar datos base de la transacción
            amount_in_cents = int(order.total_amount * 100)  # Convertir a centavos
            reference = f"ORDER-{order.order_number}"
            
            # URLs de redirección
            base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
            redirect_url = f"{base_url}{reverse('accounts:wompi_return')}"
            
            payload = {
                "amount_in_cents": amount_in_cents,
                "currency": "COP",
                "customer_email": order.billing_email,
                "reference": reference,
                "redirect_url": redirect_url,
                "acceptance_token": acceptance_token,
                "customer_data": {
                    "full_name": order.billing_name,
                    "phone_number": getattr(order.user, 'phone', ''),
                }
            }
            
            # Agregar parámetros específicos del método de pago
            if payment_method == 'CARD':
                # Para tarjetas, se necesita el token de la tarjeta
                card_token = kwargs.get('card_token')
                if not card_token:
                    raise ValueError("Token de tarjeta requerido para pagos con tarjeta")
                payload["payment_source_id"] = card_token
                
            elif payment_method == 'NEQUI':
                # Para Nequi, se necesita el número de teléfono
                phone_number = kwargs.get('phone_number')
                if not phone_number:
                    raise ValueError("Número de teléfono requerido para pagos con Nequi")
                payload["payment_method"] = {
                    "type": "NEQUI",
                    "phone_number": phone_number
                }
                
            elif payment_method == 'PSE':
                # Para PSE, se necesitan datos bancarios
                bank_code = kwargs.get('bank_code')
                user_type = kwargs.get('user_type', '0')  # 0: Persona natural, 1: Persona jurídica
                user_legal_id_type = kwargs.get('user_legal_id_type', 'CC')
                user_legal_id = kwargs.get('user_legal_id')
                
                if not all([bank_code, user_legal_id]):
                    raise ValueError("Datos bancarios requeridos para pagos PSE")
                
                payload["payment_method"] = {
                    "type": "PSE",
                    "user_type": user_type,
                    "user_legal_id_type": user_legal_id_type,
                    "user_legal_id": user_legal_id,
                    "financial_institution_code": bank_code
                }
            
            # Realizar la petición a Wompi
            url = f"{self.base_url}/transactions"
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            transaction_data = response.json()
            wompi_data = transaction_data.get('data', {})
            
            # Crear registro de transacción en la base de datos
            wompi_transaction = WompiTransaction.objects.create(
                order=order,
                wompi_id=wompi_data.get('id'),
                reference=reference,
                amount_in_cents=amount_in_cents,
                currency='COP',
                payment_method=payment_method,
                customer_email=order.billing_email,
                customer_phone=getattr(order.user, 'phone', ''),
                redirect_url=redirect_url,
                wompi_response=transaction_data,
                status='PENDING'
            )
            
            return wompi_transaction
            
        except requests.RequestException as e:
            logger.error(f"Error creando transacción en Wompi: {e}")
            raise
        except Exception as e:
            logger.error(f"Error general creando transacción: {e}")
            raise
    
    def get_transaction(self, transaction_id):
        """Obtiene el estado de una transacción desde Wompi"""
        try:
            url = f"{self.base_url}/transactions/{transaction_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error obteniendo transacción {transaction_id}: {e}")
            raise
    
    def update_transaction_status(self, wompi_transaction_id, webhook_data=None):
        """
        Actualiza el estado de una transacción basado en datos de webhook o consulta directa
        """
        try:
            # Buscar la transacción en la base de datos
            transaction = WompiTransaction.objects.get(wompi_id=wompi_transaction_id)
            
            # Si no se proporcionan datos de webhook, consultar a Wompi
            if webhook_data is None:
                webhook_data = self.get_transaction(wompi_transaction_id)
            
            transaction_data = webhook_data.get('data', {})
            status = transaction_data.get('status', 'PENDING')
            
            # Mapear estados de Wompi a nuestros estados
            status_mapping = {
                'APPROVED': 'APPROVED',
                'DECLINED': 'DECLINED',
                'PENDING': 'PENDING',
                'VOIDED': 'VOIDED',
                'ERROR': 'ERROR'
            }
            
            new_status = status_mapping.get(status, 'ERROR')
            
            # Actualizar transacción
            transaction.status = new_status
            transaction.wompi_response = webhook_data
            
            if new_status == 'APPROVED':
                transaction.paid_at = datetime.now()
                # Actualizar estado de la orden
                transaction.order.status = 'completed'
                transaction.order.save()
                
                # Crear cliente automáticamente cuando se complete la transacción
                try:
                    from .views import create_or_update_client_from_order
                    create_or_update_client_from_order(transaction.order)
                except Exception as e:
                    logger.error(f"Error creando cliente desde transacción aprobada: {e}")
                    
            elif new_status in ['DECLINED', 'ERROR']:
                transaction.order.status = 'failed'
                transaction.order.save()
            
            transaction.save()
            
            return transaction
            
        except WompiTransaction.DoesNotExist:
            logger.error(f"Transacción Wompi {wompi_transaction_id} no encontrada")
            raise
        except Exception as e:
            logger.error(f"Error actualizando estado de transacción: {e}")
            raise
    
    def verify_webhook_signature(self, payload, signature, timestamp):
        """
        Verifica la firma de un webhook de Wompi
        """
        try:
            if not self.config.events_secret:
                logger.warning("No hay secret de eventos configurado")
                return True  # En desarrollo, permitir sin verificación
            
            # Crear la cadena a firmar
            string_to_sign = f"{payload}{timestamp}{self.config.events_secret}"
            
            # Calcular la firma esperada
            expected_signature = hashlib.sha256(string_to_sign.encode()).hexdigest()
            
            # Comparar firmas
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error verificando firma de webhook: {e}")
            return False
    
    def process_webhook_event(self, event_data, signature, timestamp):
        """
        Procesa un evento de webhook de Wompi
        """
        try:
            # Verificar firma si está configurada
            payload_str = json.dumps(event_data, separators=(',', ':'))
            if not self.verify_webhook_signature(payload_str, signature, timestamp):
                raise ValueError("Firma de webhook inválida")
            
            event_type = event_data.get('event')
            data = event_data.get('data', {})
            
            # Crear registro del evento
            event_record = WompiWebhookEvent.objects.create(
                event_id=event_data.get('sent_at', str(datetime.now())),
                event_type=event_type,
                data=event_data,
                signature=signature
            )
            
            # Procesar según el tipo de evento
            if event_type == 'transaction.updated':
                transaction_data = data.get('transaction', {})
                wompi_id = transaction_data.get('id')
                
                if wompi_id:
                    updated_transaction = self.update_transaction_status(wompi_id, {'data': transaction_data})
                    event_record.transaction = updated_transaction
                    event_record.processed = True
                    event_record.processed_at = datetime.now()
                    event_record.save()
                    
                    return updated_transaction
            
            # Marcar como procesado aunque no se haya hecho nada específico
            event_record.processed = True
            event_record.processed_at = datetime.now()
            event_record.save()
            
            return event_record
            
        except Exception as e:
            logger.error(f"Error procesando webhook: {e}")
            if 'event_record' in locals():
                event_record.error_message = str(e)
                event_record.save()
            raise
    
    def get_payment_methods(self):
        """Obtiene los métodos de pago disponibles"""
        try:
            url = f"{self.base_url}/payment_methods"
            response = requests.get(url)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error obteniendo métodos de pago: {e}")
            raise
    
    def get_pse_banks(self):
        """Obtiene la lista de bancos disponibles para PSE"""
        try:
            url = f"{self.base_url}/pse/financial_institutions"
            response = requests.get(url)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error obteniendo bancos PSE: {e}")
            raise 