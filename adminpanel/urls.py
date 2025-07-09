from django.urls import path
from django.shortcuts import redirect
from . import views

def redirect_to_accounts_login(request):
    """Redirigir a /accounts/login/ para unificar login"""
    return redirect('/accounts/login/')

app_name = 'adminpanel'

urlpatterns = [
    path('login/', redirect_to_accounts_login, name='admin_login'),
    path('logout/', views.logout_view, name='admin_logout'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Servicios del Home
    path('servicios-home/', views.servicios_home_list, name='servicios_home_list'),
    
    # Servicios Vendibles
    path('servicios-vendibles/', views.servicios_vendibles_list, name='servicios_vendibles_list'),
    path('servicios-vendibles/crear/', views.servicio_vendible_create, name='servicio_vendible_create'),
    path('servicios-vendibles/<int:servicio_id>/editar/', views.servicio_vendible_edit, name='servicio_vendible_edit'),
    path('servicios-vendibles/<int:servicio_id>/eliminar/', views.servicio_vendible_delete, name='servicio_vendible_delete'),
    
    # Servicios (legacy - mantener para compatibilidad)
    path('servicios/', views.servicios_list, name='servicios_list'),
    path('servicios/crear/', views.servicio_create, name='servicio_create'),
    path('servicios/<int:servicio_id>/editar/', views.servicio_edit, name='servicio_edit'),
    path('servicios/<int:servicio_id>/eliminar/', views.servicio_delete, name='servicio_delete'),
    
    # Gestión de categorías
    path('categorias/', views.categorias_list, name='categorias_list'),
    
    # Analytics
    path('analytics/', views.analytics_view, name='analytics'),
    
    # API para gráficos
    path('api/chart-data/', views.api_chart_data, name='api_chart_data'),
    
    # Gestión de contactos
    path('contactos/', views.contactos_list, name='contactos_list'),
    
    # Gestión de clientes
    path('clientes/', views.clientes_list, name='clientes_list'),
    path('clientes/crear/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:cliente_id>/editar/', views.cliente_edit, name='cliente_edit'),
    path('clientes/<int:cliente_id>/eliminar/', views.cliente_delete, name='cliente_delete'),
    
    # Gestión de ventas
    path('ventas/', views.ventas_list, name='ventas_list'),
    path('ventas/crear/', views.venta_create, name='venta_create'),
    path('ventas/<int:venta_id>/editar/', views.venta_edit, name='venta_edit'),
    path('ventas/<int:venta_id>/eliminar/', views.venta_delete, name='venta_delete'),
] 