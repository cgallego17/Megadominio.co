import json
from django.utils import timezone
from django.urls import resolve
from django.http import HttpResponse
from .models import Visita, EstadisticaDiaria
from datetime import date
from django.db import transaction

class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Procesar la request antes de la vista
        self.process_request(request)
        
        response = self.get_response(request)
        
        # Procesar después de la vista si es exitosa
        if isinstance(response, HttpResponse) and 200 <= response.status_code < 300:
            self.process_response(request, response)
        
        return response

    def process_request(self, request):
        # Obtener información del visitante
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referrer = request.META.get('HTTP_REFERER', '')
        path = request.path
        
        # No trackear visitas del panel admin ni archivos estáticos
        if path.startswith('/panel/') or path.startswith('/static/') or path.startswith('/admin/'):
            return
        
        # No trackear bots comunes
        if self.is_bot(user_agent):
            return
        
        # Clasificar referrer
        referrer_source = self.classify_referrer(referrer)
        
        # Obtener información geográfica
        geo_info = Visita.get_geo_info(ip_address)
        
        # Crear registro de visita
        try:
            with transaction.atomic():
                visita_data = {
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'referrer': referrer,
                    'referrer_source': referrer_source,
                    'page_visited': path,
                    'timestamp': timezone.now()
                }
                
                # Agregar información geográfica si está disponible
                if geo_info:
                    visita_data.update({
                        'country': geo_info.get('country', ''),
                        'country_code': geo_info.get('country_code', ''),
                        'city': geo_info.get('city', ''),
                        'region': geo_info.get('region', '')
                    })
                
                visita = Visita.objects.create(**visita_data)
                
                # Actualizar estadísticas diarias
                self.update_daily_stats(ip_address, path)
                
        except Exception as e:
            # No fallar si hay error en analytics
            pass

    def process_response(self, request, response):
        return response

    def get_client_ip(self, request):
        """Obtener IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def is_bot(self, user_agent):
        """Detectar bots comunes"""
        bot_keywords = [
            'bot', 'crawler', 'spider', 'scraper', 'facebook', 'twitter',
            'google', 'bing', 'yahoo', 'duckduckgo', 'slurp', 'linkedinbot'
        ]
        user_agent_lower = user_agent.lower()
        return any(keyword in user_agent_lower for keyword in bot_keywords)

    def classify_referrer(self, referrer):
        """Clasificar la fuente del tráfico"""
        if not referrer:
            return 'directo'
        
        referrer_lower = referrer.lower()
        
        # Motores de búsqueda
        search_engines = {
            'google.com': 'google',
            'bing.com': 'bing',
            'yahoo.com': 'yahoo',
            'duckduckgo.com': 'duckduckgo',
            'search.yahoo.com': 'yahoo',
            'yandex.com': 'yandex'
        }
        
        for domain, source in search_engines.items():
            if domain in referrer_lower:
                return f'busqueda_{source}'
        
        # Redes sociales
        social_networks = {
            'facebook.com': 'facebook',
            'instagram.com': 'instagram', 
            'twitter.com': 'twitter',
            'linkedin.com': 'linkedin',
            'tiktok.com': 'tiktok',
            'youtube.com': 'youtube',
            'whatsapp.com': 'whatsapp',
            't.me': 'telegram'
        }
        
        for domain, source in social_networks.items():
            if domain in referrer_lower:
                return f'social_{source}'
        
        # Email marketing
        email_providers = ['gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com']
        for provider in email_providers:
            if provider in referrer_lower:
                return 'email'
        
        # Otros sitios web
        return 'referral'

    def update_daily_stats(self, ip_address, path):
        """Actualizar estadísticas diarias"""
        today = date.today()
        
        # Obtener o crear estadística del día
        stats, created = EstadisticaDiaria.objects.get_or_create(
            fecha=today,
            defaults={
                'visitas_totales': 0,
                'visitas_unicas': 0,
                'paginas_vistas': 0
            }
        )
        
        # Incrementar contadores
        stats.visitas_totales += 1
        stats.paginas_vistas += 1
        
        # Verificar si es visitante único del día
        today_visits = Visita.objects.filter(
            ip_address=ip_address,
            timestamp__date=today
        ).count()
        
        if today_visits == 1:  # Primera visita del día
            stats.visitas_unicas += 1
        
        stats.save() 