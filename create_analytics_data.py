#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta, date
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'megadominio.settings')
django.setup()

from adminpanel.models import Visita, EstadisticaDiaria, ContactoFormulario, PaginaVisitada
from django.utils import timezone

def create_sample_analytics_data():
    """Crear datos de prueba para el sistema de analytics"""
    
    print("🚀 Creando datos de prueba para Analytics...")
    
    # Limpiar datos existentes
    Visita.objects.all().delete()
    EstadisticaDiaria.objects.all().delete()
    
    # Crear visitas de los últimos 30 días
    sources = [
        'directo', 'busqueda_google', 'busqueda_bing', 'social_facebook', 
        'social_instagram', 'social_twitter', 'social_linkedin', 'social_youtube',
        'social_whatsapp', 'email', 'referral'
    ]
    
    pages = [
        '/', '/servicios/', '/proyectos/', '/contacto/', 
        '/sobre-nosotros/', '/blog/', '/hosting/', '/desarrollo/',
        '/dominios/', '/ssl/', '/ecommerce/', '/wordpress/'
    ]
    
    # IPs de prueba
    sample_ips = [
        '192.168.1.1', '10.0.0.1', '172.16.0.1', '203.0.113.1',
        '198.51.100.1', '192.0.2.1', '127.0.0.1', '185.199.108.1',
        '8.8.8.8', '1.1.1.1', '208.67.222.222', '9.9.9.9'
    ]
    
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
    ]
    
    referrers = [
        '',  # Directo
        'https://google.com/search?q=hosting',
        'https://google.com/search?q=desarrollo+web',
        'https://www.facebook.com/',
        'https://instagram.com/',
        'https://twitter.com/',
        'https://linkedin.com/',
        'https://youtube.com/',
        'https://wa.me/',
        'https://otrodominio.com/',
        'https://ejemplo.com/'
    ]
    
    # Crear visitas para los últimos 30 días
    for i in range(30):
        fecha = timezone.now().date() - timedelta(days=i)
        
        # Número de visitas para el día (más en días recientes)
        base_visits = 20 + random.randint(0, 30)
        if i < 7:  # Últimos 7 días más visitas
            base_visits += random.randint(20, 50)
        
        daily_visits = 0
        unique_visitors = set()
        
        # Crear visitas para el día
        for j in range(base_visits):
            # Hora aleatoria del día
            hour = random.randint(8, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            timestamp = datetime.combine(fecha, datetime.min.time()) + timedelta(
                hours=hour, minutes=minute, seconds=second
            )
            timestamp = timezone.make_aware(timestamp)
            
            # Seleccionar datos aleatorios
            ip = random.choice(sample_ips)
            user_agent = random.choice(user_agents)
            page = random.choice(pages)
            referrer = random.choice(referrers)
            source = random.choice(sources)
            
            # Crear visita
            Visita.objects.create(
                ip_address=ip,
                user_agent=user_agent,
                referrer=referrer,
                referrer_source=source,
                page_visited=page,
                timestamp=timestamp
            )
            
            daily_visits += 1
            unique_visitors.add(ip)
        
        # Crear estadística diaria
        EstadisticaDiaria.objects.create(
            fecha=fecha,
            visitas_totales=daily_visits,
            visitas_unicas=len(unique_visitors),
            paginas_vistas=daily_visits + random.randint(0, 10)  # Algunas páginas adicionales
        )
        
        print(f"✅ Día {fecha}: {daily_visits} visitas, {len(unique_visitors)} únicos")
    
    # Crear algunos contactos adicionales
    ContactoFormulario.objects.create(
        nombre="Carlos Mendoza",
        email="carlos@empresa.com",
        telefono="555-0123",
        servicio_interes="Hosting Premium",
        mensaje="Necesito hosting para mi empresa, ¿qué opciones tienen?",
        atendido=False
    )
    
    ContactoFormulario.objects.create(
        nombre="Ana López",
        email="ana.lopez@startup.com",
        telefono="555-0456",
        servicio_interes="Desarrollo Web",
        mensaje="Quiero desarrollar una plataforma e-commerce moderna",
        atendido=True
    )
    
    ContactoFormulario.objects.create(
        nombre="Roberto Silva",
        email="roberto@negocio.com",
        telefono="555-0789",
        servicio_interes="SSL y Seguridad",
        mensaje="Mi sitio necesita certificado SSL urgente",
        atendido=False
    )
    
    # Crear páginas visitadas
    paginas_populares = [
        ("/", "Inicio", "Página principal del sitio"),
        ("/servicios/", "Servicios", "Catálogo de servicios"),
        ("/hosting/", "Hosting", "Servicios de hosting"),
        ("/desarrollo/", "Desarrollo Web", "Desarrollo de sitios web"),
        ("/contacto/", "Contacto", "Formulario de contacto"),
        ("/dominios/", "Dominios", "Registro de dominios"),
        ("/ssl/", "SSL", "Certificados SSL"),
        ("/ecommerce/", "E-commerce", "Tiendas online"),
    ]
    
    for path, nombre, descripcion in paginas_populares:
        visitas_count = Visita.objects.filter(page_visited=path).count()
        PaginaVisitada.objects.update_or_create(
            path=path,
            defaults={
                'nombre_amigable': nombre,
                'descripcion': descripcion,
                'visitas_totales': visitas_count,
                'activo': True
            }
        )
    
    print("\n🎉 Datos de Analytics creados exitosamente!")
    print(f"📊 Total de visitas: {Visita.objects.count()}")
    print(f"📈 Días con estadísticas: {EstadisticaDiaria.objects.count()}")
    print(f"✉️ Contactos creados: {ContactoFormulario.objects.count()}")
    print(f"📄 Páginas rastreadas: {PaginaVisitada.objects.count()}")
    
    # Mostrar estadísticas de hoy
    today = date.today()
    try:
        stats_today = EstadisticaDiaria.objects.get(fecha=today)
        print(f"\n📅 Estadísticas de hoy ({today}):")
        print(f"   - Visitas totales: {stats_today.visitas_totales}")
        print(f"   - Visitantes únicos: {stats_today.visitas_unicas}")
        print(f"   - Páginas vistas: {stats_today.paginas_vistas}")
    except EstadisticaDiaria.DoesNotExist:
        print(f"\n📅 No hay estadísticas para hoy ({today})")
    
    # Mostrar fuentes de tráfico
    print("\n🌐 Fuentes de tráfico (últimos 30 días):")
    from django.db.models import Count
    fuentes = Visita.objects.values('referrer_source').annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    for fuente in fuentes:
        source_name = fuente['referrer_source']
        nombres_fuentes = {
            'directo': 'Directo',
            'busqueda_google': 'Google',
            'busqueda_bing': 'Bing',
            'social_facebook': 'Facebook',
            'social_instagram': 'Instagram',
            'social_twitter': 'Twitter',
            'social_linkedin': 'LinkedIn',
            'social_youtube': 'YouTube',
            'social_whatsapp': 'WhatsApp',
            'email': 'Email',
            'referral': 'Otros sitios'
        }
        nombre_amigable = nombres_fuentes.get(source_name, source_name.title())
        print(f"   - {nombre_amigable}: {fuente['total']} visitas")
    
    print("\n🔄 El middleware está configurado para trackear nuevas visitas automáticamente")
    print("🚀 ¡Listo para usar el panel de analytics!")

if __name__ == "__main__":
    create_sample_analytics_data() 