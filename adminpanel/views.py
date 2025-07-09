from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from servicios.models import Servicio
from proyectos.models import Proyecto
from .models import EstadisticaDiaria, ContactoFormulario, Visita, PaginaVisitada, Cliente, Venta, DetalleVenta
import json
import requests
from datetime import date, timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from accounts.models import TwoFactorCode, User, PurchasableService, Order, ClientService
from django.core.paginator import Paginator
from django.db.models import Sum

# Create your views here.

# Función eliminada - usando verify_recaptcha_v3 en su lugar

def verify_recaptcha_v3(token):
    """
    Función para verificar reCAPTCHA v3 con Google
    """
    if not token:
        print("[DEBUG] reCAPTCHA: Token vacío")
        return False
    
    secret = settings.RECAPTCHA_PRIVATE_KEY
    data = {
        'secret': secret,
        'response': token
    }
    
    try:
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()
        
        if result.get('success', False):
            score = result.get('score', 0)
            print(f'[DEBUG] reCAPTCHA: OK (score: {score})')
            # Usar score desde settings
            min_score = getattr(settings, 'RECAPTCHA_REQUIRED_SCORE', 0.5)
            return score >= min_score
        else:
            print(f"[DEBUG] reCAPTCHA: FAIL - {result.get('error-codes', [])}")
            return False
    except Exception as e:
        print(f"[DEBUG] reCAPTCHA: ERROR - {e}")
        return False

@login_required
def admin_dashboard(request):
    """Vista principal del dashboard administrativo"""
    # Verificar que el usuario sea administrador
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder al panel administrativo.')
        return redirect('accounts:client_dashboard')
    
    # Estadísticas generales
    total_users = User.objects.filter(user_type='client').count()
    total_orders = Order.objects.count()
    total_services = ClientService.objects.count()
    total_home_services = Servicio.objects.count()
    total_purchasable_services = PurchasableService.objects.count()
    
    # Servicios vendibles activos y destacados
    servicios_vendibles_activos = PurchasableService.objects.filter(is_active=True).count()
    servicios_vendibles_destacados = PurchasableService.objects.filter(is_featured=True, is_active=True).select_related('home_service')[:5]
    
    # Órdenes recientes
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    
    # Servicios por vencer
    thirty_days_from_now = timezone.now().date() + timedelta(days=30)
    expiring_services = ClientService.objects.filter(
        expiry_date__lte=thirty_days_from_now,
        status='active'
    ).select_related('client').order_by('expiry_date')[:5]
    
    # Ingresos del mes actual
    current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = Order.objects.filter(
        created_at__gte=current_month_start,
        status='completed'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Estadísticas simuladas para el dashboard (puedes reemplazar con datos reales)
    visitas_hoy = 45
    visitantes_unicos_hoy = 32
    total_contactos = total_users
    contactos_nuevos = User.objects.filter(
        user_type='client',
        created_at__gte=timezone.now().date()
    ).count()
    
    # Servicios populares simulados
    servicios_populares = Servicio.objects.all()[:5]
    for servicio in servicios_populares:
        servicio.consultas = 25  # Simulado
    
    # Stats geográficos simulados
    stats_geo = {
        'total_paises': 12,
    }
    
    context = {
        'total_users': total_users,
        'total_orders': total_orders,
        'total_services': total_services,
        'total_home_services': total_home_services,
        'total_purchasable_services': total_purchasable_services,
        'total_servicios': total_home_services,  # Para compatibilidad con template
        'servicios_vendibles_activos': servicios_vendibles_activos,
        'total_servicios_vendibles': total_purchasable_services,
        'servicios_vendibles_destacados': servicios_vendibles_destacados,
        'recent_orders': recent_orders,
        'expiring_services': expiring_services,
        'monthly_revenue': monthly_revenue,
        'visitas_hoy': visitas_hoy,
        'visitantes_unicos_hoy': visitantes_unicos_hoy,
        'total_contactos': total_contactos,
        'contactos_nuevos': contactos_nuevos,
        'servicios_populares': servicios_populares,
        'stats_geo': stats_geo,
    }
    
    return render(request, 'adminpanel/dashboard.html', context)

@login_required
def servicios_home_list(request):
    """Vista para listar servicios del home"""
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder al panel administrativo.')
        return redirect('accounts:client_dashboard')
    
    # Filtros
    search = request.GET.get('search', '')
    has_image = request.GET.get('has_image', '')
    has_price = request.GET.get('has_price', '')
    has_vendibles = request.GET.get('has_vendibles', '')
    
    # Query base
    servicios = Servicio.objects.annotate(
        total_purchasable=Count('purchasable_services')
    )
    
    # Aplicar filtros
    if search:
        servicios = servicios.filter(
            Q(nombre__icontains=search) | 
            Q(descripcion__icontains=search)
        )
    
    if has_image:
        if has_image == 'true':
            servicios = servicios.filter(imagen__isnull=False).exclude(imagen='')
        elif has_image == 'false':
            servicios = servicios.filter(Q(imagen__isnull=True) | Q(imagen=''))
    
    if has_price:
        if has_price == 'true':
            servicios = servicios.filter(precio__isnull=False).exclude(precio='')
        elif has_price == 'false':
            servicios = servicios.filter(Q(precio__isnull=True) | Q(precio=''))
    
    if has_vendibles:
        if has_vendibles == 'true':
            servicios = servicios.filter(total_purchasable__gt=0)
        elif has_vendibles == 'false':
            servicios = servicios.filter(total_purchasable=0)
    
    # Ordenar
    servicios = servicios.order_by('nombre')
    
    # Estadísticas adicionales
    servicios_con_imagen = servicios.filter(imagen__isnull=False).exclude(imagen='')
    servicios_con_precio = servicios.filter(precio__isnull=False).exclude(precio='')
    total_servicios_vendibles = PurchasableService.objects.count()
    
    context = {
        'servicios': servicios,
        'servicios_con_imagen': servicios_con_imagen,
        'servicios_con_precio': servicios_con_precio,
        'total_servicios_vendibles': total_servicios_vendibles,
        'current_search': search,
        'current_has_image': has_image,
        'current_has_price': has_price,
        'current_has_vendibles': has_vendibles,
    }
    
    return render(request, 'adminpanel/servicios_home_list.html', context)

@login_required
def servicios_vendibles_list(request):
    """Vista para listar servicios vendibles"""
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder al panel administrativo.')
        return redirect('accounts:client_dashboard')
    
    # Filtros
    search = request.GET.get('search', '')
    home_service_id = request.GET.get('home_service', '')
    is_active = request.GET.get('is_active', '')
    
    # Query base
    servicios = PurchasableService.objects.select_related('home_service')
    
    # Aplicar filtros
    if search:
        servicios = servicios.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search) |
            Q(home_service__nombre__icontains=search)
        )
    
    if home_service_id:
        servicios = servicios.filter(home_service_id=home_service_id)
    
    if is_active:
        servicios = servicios.filter(is_active=is_active == 'true')
    
    # Ordenar
    servicios = servicios.order_by('-is_featured', 'home_service__nombre', 'name')
    
    # Paginación
    paginator = Paginator(servicios, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Servicios del home para el filtro
    home_services = Servicio.objects.all().order_by('nombre')
    
    # Estadísticas
    stats = {
        'total': PurchasableService.objects.count(),
        'active': PurchasableService.objects.filter(is_active=True).count(),
        'featured': PurchasableService.objects.filter(is_featured=True).count(),
        'categories': Servicio.objects.count(),
    }
    
    context = {
        'page_obj': page_obj,
        'servicios': page_obj,  # Para compatibilidad con el template
        'home_services': home_services,
        'categories': home_services,  # Para compatibilidad con el template
        'search': search,
        'current_search': search,
        'home_service_id': home_service_id,
        'current_category': home_service_id,
        'is_active': is_active,
        'current_active': is_active,
        'stats': stats,
    }
    
    return render(request, 'adminpanel/servicios_vendibles_list.html', context)

@login_required
def servicio_vendible_create(request):
    """Vista para crear un nuevo servicio vendible"""
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder al panel administrativo.')
        return redirect('accounts:client_dashboard')
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            home_service_id = request.POST.get('home_service')
            name = request.POST.get('name')
            slug = request.POST.get('slug')
            short_description = request.POST.get('short_description')
            description = request.POST.get('description')
            
            # Precios
            price_monthly = request.POST.get('price_monthly') or None
            price_quarterly = request.POST.get('price_quarterly') or None
            price_semiannual = request.POST.get('price_semiannual') or None
            price_annual = request.POST.get('price_annual') or None
            price_biennial = request.POST.get('price_biennial') or None
            price_one_time = request.POST.get('price_one_time') or None
            setup_fee = request.POST.get('setup_fee') or 0
            
            # Características
            features_text = request.POST.get('features', '')
            features = [f.strip() for f in features_text.split('\n') if f.strip()]
            
            # Configuración
            is_active = request.POST.get('is_active') == 'on'
            is_featured = request.POST.get('is_featured') == 'on'
            requires_domain = request.POST.get('requires_domain') == 'on'
            
            # Crear el servicio
            servicio = PurchasableService.objects.create(
                home_service_id=home_service_id,
                name=name,
                slug=slug,
                short_description=short_description,
                description=description,
                price_monthly=price_monthly,
                price_quarterly=price_quarterly,
                price_semiannual=price_semiannual,
                price_annual=price_annual,
                price_biennial=price_biennial,
                price_one_time=price_one_time,
                setup_fee=setup_fee,
                features=features,
                is_active=is_active,
                is_featured=is_featured,
                requires_domain=requires_domain,
            )
            
            messages.success(request, f'Servicio "{servicio.name}" creado exitosamente.')
            return redirect('adminpanel:servicios_vendibles_list')
            
        except Exception as e:
            messages.error(request, f'Error al crear el servicio: {str(e)}')
    
    # Obtener servicios del home para el formulario
    home_services = Servicio.objects.all().order_by('nombre')
    
    context = {
        'home_services': home_services,
        'categories': home_services,  # Para compatibilidad con el template
    }
    
    return render(request, 'adminpanel/servicio_vendible_create.html', context)

@login_required
def servicio_vendible_edit(request, servicio_id):
    """Vista para editar un servicio vendible"""
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder al panel administrativo.')
        return redirect('accounts:client_dashboard')
    
    servicio = get_object_or_404(PurchasableService, id=servicio_id)
    
    if request.method == 'POST':
        try:
            # Actualizar datos del formulario
            servicio.home_service_id = request.POST.get('home_service')
            servicio.name = request.POST.get('name')
            servicio.slug = request.POST.get('slug')
            servicio.short_description = request.POST.get('short_description')
            servicio.description = request.POST.get('description')
            
            # Precios
            servicio.price_monthly = request.POST.get('price_monthly') or None
            servicio.price_quarterly = request.POST.get('price_quarterly') or None
            servicio.price_semiannual = request.POST.get('price_semiannual') or None
            servicio.price_annual = request.POST.get('price_annual') or None
            servicio.price_biennial = request.POST.get('price_biennial') or None
            servicio.price_one_time = request.POST.get('price_one_time') or None
            servicio.setup_fee = request.POST.get('setup_fee') or 0
            
            # Características
            features_text = request.POST.get('features', '')
            servicio.features = [f.strip() for f in features_text.split('\n') if f.strip()]
            
            # Configuración
            servicio.is_active = request.POST.get('is_active') == 'on'
            servicio.is_featured = request.POST.get('is_featured') == 'on'
            servicio.requires_domain = request.POST.get('requires_domain') == 'on'
            
            servicio.save()
            
            messages.success(request, f'Servicio "{servicio.name}" actualizado exitosamente.')
            return redirect('adminpanel:servicios_vendibles_list')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar el servicio: {str(e)}')
    
    # Obtener servicios del home para el formulario
    home_services = Servicio.objects.all().order_by('nombre')
    
    # Convertir features a texto
    features_text = '\n'.join(servicio.features) if servicio.features else ''
    
    context = {
        'service': servicio,
        'home_services': home_services,
        'categories': home_services,  # Para compatibilidad con el template
        'features_text': features_text,
    }
    
    return render(request, 'adminpanel/servicio_vendible_edit.html', context)

@login_required
def servicio_vendible_delete(request, servicio_id):
    """Vista para eliminar un servicio vendible"""
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder al panel administrativo.')
        return redirect('accounts:client_dashboard')
    
    servicio = get_object_or_404(PurchasableService, id=servicio_id)
    
    if request.method == 'POST':
        servicio_name = servicio.name
        servicio.delete()
        messages.success(request, f'Servicio "{servicio_name}" eliminado exitosamente.')
        return redirect('adminpanel:servicios_vendibles_list')
    
    context = {
        'service': servicio,
    }
    
    return render(request, 'adminpanel/servicio_vendible_delete.html', context)

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente')
    return redirect('/accounts/login/')

def servicios_list(request):
    if not request.user.is_authenticated or not request.user.is_admin():
        return redirect('/accounts/login/')
    
    servicios = Servicio.objects.all()
    servicios_con_imagen = servicios.filter(imagen__isnull=False)
    servicios_con_precio = servicios.exclude(precio__isnull=True).exclude(precio__exact='')
    
    context = {
        'servicios': servicios,
        'servicios_con_imagen': servicios_con_imagen,
        'servicios_con_precio': servicios_con_precio,
    }
    return render(request, 'adminpanel/servicios_list.html', context)

def servicio_edit(request, servicio_id):
    if not request.user.is_authenticated or not request.user.is_admin():
        return redirect('/accounts/login/')
    
    servicio = get_object_or_404(Servicio, id=servicio_id)
    
    if request.method == 'POST':
        servicio.nombre = request.POST.get('nombre')
        servicio.descripcion = request.POST.get('descripcion')
        servicio.descripcion_corta = request.POST.get('descripcion_corta', '')
        servicio.precio = request.POST.get('precio', '')
        
        # Solo actualizar icono si se envía uno nuevo
        if request.POST.get('icono'):
            servicio.icono = request.POST.get('icono')
        
        # Manejar imagen si se sube
        if 'imagen' in request.FILES:
            servicio.imagen = request.FILES['imagen']
        
        servicio.save()
        messages.success(request, f'Servicio "{servicio.nombre}" actualizado exitosamente')
        return redirect('adminpanel:servicios_home_list')
    
    return render(request, 'adminpanel/servicio_edit.html', {'servicio': servicio})

def servicio_create(request):
    if not request.user.is_authenticated or not request.user.is_admin():
        return redirect('/accounts/login/')
    
    if request.method == 'POST':
        servicio = Servicio()
        servicio.nombre = request.POST.get('nombre')
        servicio.descripcion = request.POST.get('descripcion')
        servicio.descripcion_corta = request.POST.get('descripcion_corta', '')
        servicio.precio = request.POST.get('precio', '')
        servicio.icono = request.POST.get('icono', 'fas fa-cogs')
        
        # Manejar imagen si se sube
        if 'imagen' in request.FILES:
            servicio.imagen = request.FILES['imagen']
        
        servicio.save()
        messages.success(request, f'Servicio "{servicio.nombre}" creado exitosamente')
        return redirect('adminpanel:servicios_home_list')
    
    return render(request, 'adminpanel/servicio_create.html')

def servicio_delete(request, servicio_id):
    if not request.user.is_authenticated or not request.user.is_admin():
        return redirect('/accounts/login/')
    
    servicio = get_object_or_404(Servicio, id=servicio_id)
    
    if request.method == 'POST':
        nombre = servicio.nombre
        servicio.delete()
        messages.success(request, f'Servicio "{nombre}" eliminado exitosamente')
        return redirect('adminpanel:servicios_home_list')
    
    return render(request, 'adminpanel/servicio_delete.html', {'servicio': servicio})

# API para datos de gráficos en tiempo real
def api_chart_data(request):
    if not request.session.get('admin_logged'):
        return JsonResponse({'error': 'No autorizado'}, status=401)
    
    period = request.GET.get('period', '7d')
    
    if period == '7d':
        days = 7
    elif period == '30d':
        days = 30
    elif period == '90d':
        days = 90
    else:
        days = 7
    
    fechas, visitas, visitas_unicas = EstadisticaDiaria.obtener_datos_grafico(days)
    
    return JsonResponse({
        'fechas': fechas,
        'visitas': visitas,
        'visitas_unicas': visitas_unicas
    })

def contactos_list(request):
    if not request.user.is_authenticated or not request.user.is_admin():
        return redirect('/accounts/login/')
    
    contactos = ContactoFormulario.objects.all().order_by('-fecha_contacto')
    
    context = {
        'contactos': contactos,
    }
    return render(request, 'adminpanel/contactos_list.html', context)

def analytics_view(request):
    """Vista de analytics detallados"""
    if not request.user.is_authenticated or not request.user.is_admin():
        return redirect('/accounts/login/')
    
    # Obtener datos para gráficos
    fechas_30, visitas_30, visitas_unicas_30 = EstadisticaDiaria.obtener_datos_grafico(30)
    
    # Estadísticas geográficas
    stats_geo = EstadisticaDiaria.obtener_estadisticas_geograficas(30)
    paises_visitantes = EstadisticaDiaria.obtener_paises_visitantes(30)
    
    # Páginas más visitadas
    paginas_populares = PaginaVisitada.objects.all()[:10]
    
    context = {
        'chart_data_30': {
            'fechas': json.dumps(fechas_30),
            'visitas': json.dumps(visitas_30),
            'visitas_unicas': json.dumps(visitas_unicas_30),
        },
        'stats_geo': stats_geo,
        'paises_visitantes': paises_visitantes,
        'paginas_populares': paginas_populares,
    }
    return render(request, 'adminpanel/analytics.html', context)

def categorias_list(request):
    """Lista de categorías de servicios"""
    if not request.user.is_authenticated or not request.user.is_admin():
        return redirect('/accounts/login/')
    
    from accounts.models import ServiceCategory
    
    categorias = ServiceCategory.objects.all().order_by('order')
    
    context = {
        'categorias': categorias,
    }
    return render(request, 'adminpanel/categorias_list.html', context)

@login_required
def clientes_list(request):
    """Vista para listar clientes"""
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder al panel administrativo.')
        return redirect('accounts:client_dashboard')
    
    # Filtros
    search = request.GET.get('search', '')
    estado = request.GET.get('estado', '')
    
    # Query base
    clientes = Cliente.objects.all()
    
    # Aplicar filtros
    if search:
        clientes = clientes.filter(
            Q(nombre__icontains=search) | 
            Q(email__icontains=search) | 
            Q(empresa__icontains=search)
        )
    
    if estado:
        clientes = clientes.filter(estado=estado)
    
    # Ordenar
    clientes = clientes.order_by('-fecha_registro')
    
    # Estadísticas
    total_clientes = clientes.count()
    clientes_activos = clientes.filter(estado='activo').count()
    clientes_vip = clientes.filter(estado='vip').count()
    clientes_prospectos = clientes.filter(estado='prospecto').count()
    
    # Paginación
    paginator = Paginator(clientes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'clientes': page_obj,
        'total_clientes': total_clientes,
        'clientes_activos': clientes_activos,
        'clientes_vip': clientes_vip,
        'clientes_prospectos': clientes_prospectos,
        'current_search': search,
        'current_estado': estado,
    }
    
    return render(request, 'adminpanel/clientes_list.html', context)

@login_required
def cliente_create(request):
    """Vista para crear un nuevo cliente"""
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder al panel administrativo.')
        return redirect('accounts:client_dashboard')
    
    if request.method == 'POST':
        try:
            cliente = Cliente.objects.create(
                nombre=request.POST['nombre'],
                email=request.POST['email'],
                telefono=request.POST.get('telefono', ''),
                empresa=request.POST.get('empresa', ''),
                direccion=request.POST.get('direccion', ''),
                estado=request.POST.get('estado', 'prospecto'),
                notas=request.POST.get('notas', '')
            )
            messages.success(request, f'Cliente "{cliente.nombre}" creado exitosamente.')
            return redirect('adminpanel:clientes_list')
        except Exception as e:
            messages.error(request, f'Error al crear el cliente: {str(e)}')
    
    context = {
        'estados': Cliente.ESTADO_CHOICES,
    }
    
    return render(request, 'adminpanel/cliente_create.html', context)

@login_required
def cliente_edit(request, cliente_id):
    """Vista para editar un cliente"""
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder al panel administrativo.')
        return redirect('accounts:client_dashboard')
    
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    if request.method == 'POST':
        try:
            cliente.nombre = request.POST['nombre']
            cliente.email = request.POST['email']
            cliente.telefono = request.POST.get('telefono', '')
            cliente.empresa = request.POST.get('empresa', '')
            cliente.direccion = request.POST.get('direccion', '')
            cliente.estado = request.POST.get('estado', 'prospecto')
            cliente.notas = request.POST.get('notas', '')
            cliente.save()
            
            messages.success(request, f'Cliente "{cliente.nombre}" actualizado exitosamente.')
            return redirect('adminpanel:clientes_list')
        except Exception as e:
            messages.error(request, f'Error al actualizar el cliente: {str(e)}')
    
    context = {
        'cliente': cliente,
        'estados': Cliente.ESTADO_CHOICES,
    }
    
    return render(request, 'adminpanel/cliente_edit.html', context)

@login_required
def cliente_delete(request, cliente_id):
    """Vista para eliminar un cliente"""
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder al panel administrativo.')
        return redirect('accounts:client_dashboard')
    
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    if request.method == 'POST':
        try:
            nombre = cliente.nombre
            cliente.delete()
            messages.success(request, f'Cliente "{nombre}" eliminado exitosamente.')
            return redirect('adminpanel:clientes_list')
        except Exception as e:
            messages.error(request, f'Error al eliminar el cliente: {str(e)}')
    
    context = {
        'cliente': cliente,
    }
    
    return render(request, 'adminpanel/cliente_delete.html', context)

@login_required
def ventas_list(request):
    """Vista para listar ventas"""
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder al panel administrativo.')
        return redirect('accounts:client_dashboard')
    
    # Filtros
    search = request.GET.get('search', '')
    estado = request.GET.get('estado', '')
    cliente_id = request.GET.get('cliente', '')
    
    # Query base
    ventas = Venta.objects.select_related('cliente').all()
    
    # Aplicar filtros
    if search:
        ventas = ventas.filter(
            Q(numero_factura__icontains=search) | 
            Q(cliente__nombre__icontains=search) | 
            Q(cliente__email__icontains=search)
        )
    
    if estado:
        ventas = ventas.filter(estado=estado)
    
    if cliente_id:
        ventas = ventas.filter(cliente_id=cliente_id)
    
    # Ordenar
    ventas = ventas.order_by('-fecha_venta')
    
    # Estadísticas
    total_ventas = ventas.count()
    ventas_completadas = ventas.filter(estado='completada').count()
    ventas_pendientes = ventas.filter(estado='pendiente').count()
    total_ingresos = ventas.filter(estado='completada').aggregate(total=Sum('valor_total'))['total'] or 0
    
    # Clientes para filtro
    clientes = Cliente.objects.all().order_by('nombre')
    
    # Paginación
    paginator = Paginator(ventas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'ventas': page_obj,
        'total_ventas': total_ventas,
        'ventas_completadas': ventas_completadas,
        'ventas_pendientes': ventas_pendientes,
        'total_ingresos': total_ingresos,
        'clientes': clientes,
        'current_search': search,
        'current_estado': estado,
        'current_cliente': cliente_id,
    }
    
    return render(request, 'adminpanel/ventas_list.html', context)

@login_required
def venta_create(request):
    """Vista para crear una nueva venta"""
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder al panel administrativo.')
        return redirect('accounts:client_dashboard')
    
    if request.method == 'POST':
        try:
            # Generar número de factura único
            import uuid
            numero_factura = f"FAC-{uuid.uuid4().hex[:8].upper()}"
            
            venta = Venta.objects.create(
                cliente_id=request.POST['cliente'],
                numero_factura=numero_factura,
                estado=request.POST.get('estado', 'pendiente'),
                metodo_pago=request.POST['metodo_pago'],
                subtotal=request.POST.get('subtotal', 0),
                impuestos=request.POST.get('impuestos', 0),
                descuento=request.POST.get('descuento', 0),
                valor_total=request.POST.get('valor_total', 0),
                descripcion=request.POST.get('descripcion', ''),
                notas=request.POST.get('notas', '')
            )
            
            # Crear detalles de venta si se proporcionan
            servicios = request.POST.getlist('servicio[]')
            descripciones = request.POST.getlist('descripcion_servicio[]')
            cantidades = request.POST.getlist('cantidad[]')
            precios = request.POST.getlist('precio[]')
            
            for i in range(len(servicios)):
                if servicios[i] and descripciones[i]:
                    DetalleVenta.objects.create(
                        venta=venta,
                        servicio=servicios[i],
                        descripcion=descripciones[i],
                        cantidad=int(cantidades[i]) if cantidades[i] else 1,
                        precio_unitario=float(precios[i]) if precios[i] else 0
                    )
            
            messages.success(request, f'Venta "{venta.numero_factura}" creada exitosamente.')
            return redirect('adminpanel:ventas_list')
        except Exception as e:
            messages.error(request, f'Error al crear la venta: {str(e)}')
    
    context = {
        'clientes': Cliente.objects.all().order_by('nombre'),
        'estados': Venta.ESTADO_CHOICES,
        'metodos_pago': Venta.METODO_PAGO_CHOICES,
    }
    
    return render(request, 'adminpanel/venta_create.html', context)

@login_required
def venta_edit(request, venta_id):
    """Vista para editar una venta"""
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder al panel administrativo.')
        return redirect('accounts:client_dashboard')
    
    venta = get_object_or_404(Venta, id=venta_id)
    
    if request.method == 'POST':
        try:
            venta.cliente_id = request.POST['cliente']
            venta.estado = request.POST.get('estado', 'pendiente')
            venta.metodo_pago = request.POST['metodo_pago']
            venta.subtotal = request.POST.get('subtotal', 0)
            venta.impuestos = request.POST.get('impuestos', 0)
            venta.descuento = request.POST.get('descuento', 0)
            venta.valor_total = request.POST.get('valor_total', 0)
            venta.descripcion = request.POST.get('descripcion', '')
            venta.notas = request.POST.get('notas', '')
            venta.save()
            
            messages.success(request, f'Venta "{venta.numero_factura}" actualizada exitosamente.')
            return redirect('adminpanel:ventas_list')
        except Exception as e:
            messages.error(request, f'Error al actualizar la venta: {str(e)}')
    
    context = {
        'venta': venta,
        'clientes': Cliente.objects.all().order_by('nombre'),
        'estados': Venta.ESTADO_CHOICES,
        'metodos_pago': Venta.METODO_PAGO_CHOICES,
    }
    
    return render(request, 'adminpanel/venta_edit.html', context)

@login_required
def venta_delete(request, venta_id):
    """Vista para eliminar una venta"""
    if not request.user.is_admin():
        messages.error(request, 'No tienes permisos para acceder al panel administrativo.')
        return redirect('accounts:client_dashboard')
    
    venta = get_object_or_404(Venta, id=venta_id)
    
    if request.method == 'POST':
        try:
            numero_factura = venta.numero_factura
            venta.delete()
            messages.success(request, f'Venta "{numero_factura}" eliminada exitosamente.')
            return redirect('adminpanel:ventas_list')
        except Exception as e:
            messages.error(request, f'Error al eliminar la venta: {str(e)}')
    
    context = {
        'venta': venta,
    }
    
    return render(request, 'adminpanel/venta_delete.html', context)


