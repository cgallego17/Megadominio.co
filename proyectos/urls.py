from django.urls import path
from . import views

urlpatterns = [
    path('', views.proyectos_list, name='proyectos_list'),
] 