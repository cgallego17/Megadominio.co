from django.shortcuts import render
from .models import Proyecto

# Create your views here.

def proyectos_list(request):
    proyectos = Proyecto.objects.all()
    return render(request, 'proyectos/proyectos_list.html', {'proyectos': proyectos})
