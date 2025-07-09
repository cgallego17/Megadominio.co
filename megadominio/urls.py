"""
URL configuration for megadominio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin de Django (solo para desarrollo)
    path('servicios/cart/', RedirectView.as_view(url='/cart/', permanent=True)),
    path('servicios/checkout/', RedirectView.as_view(url='/checkout/', permanent=True)),
    path('servicios/order-confirmation/<str:order_number>/', RedirectView.as_view(pattern_name='services:order_confirmation', permanent=True)),
    path('', include(('servicios.urls', 'servicios'), namespace='services')),  # Home y servicios
    path('proyectos/', include('proyectos.urls')),  # Proyectos realizados
    path('panel/', include('adminpanel.urls')),  # Panel de administración propio
    path('accounts/', include('accounts.urls')),  # Nuevo sistema de autenticación
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
