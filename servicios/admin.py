from django.contrib import admin
from .models import Servicio

# Registro básico para el admin de Django (opcional)
# Se recomienda usar el panel personalizado en /panel/servicios/
admin.site.register(Servicio)
