from django.db import models
from django.core.validators import URLValidator

class CompañiaPlataforma(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
class Plataforma(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_salida = models.DateField(verbose_name='Fecha de salida', null=True)
    total_videojuegos = models.PositiveIntegerField(null=True)
    compañia_plataforma = models.ForeignKey(CompañiaPlataforma, on_delete=models.CASCADE)
    precio_original = models.FloatField(null=True)
    picture_url = models.URLField(validators=[URLValidator()])


    def _str__(self):
        return self.nombre

class Genero(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Desarrolladores(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre  

class VideoJuego(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_lanzamiento = models.DateField(verbose_name='Fecha de Lanzamiento', null=True)
    descripcion = models.TextField(null=True)
    plataformas = models.ManyToManyField(Plataforma)
    genero = models.ManyToManyField(Genero)
    temas = models.CharField(max_length=100)
    desarrolladores = models.ManyToManyField(Desarrolladores)
    picture_url = models.URLField(validators=[URLValidator()])

    def __str__(self):
        return self.nombre

