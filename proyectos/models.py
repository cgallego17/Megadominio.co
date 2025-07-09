from django.db import models

# Create your models here.

class Proyecto(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='proyectos/')
    tecnologias = models.CharField(max_length=200, help_text='Tecnologías separadas por coma')
    enlace = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nombre
