"""
cursos/models.py

Módulo "Cursos Online": catálogo de cursos de tecnología agrupados
por área de conocimiento.

Relación: 1 Area -> N Cursos (ForeignKey).
"""
from django.db import models

from .choices import NIVELES


class Area(models.Model):
    """Área de conocimiento a la que pertenece un curso."""
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Área"
        verbose_name_plural = "Áreas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Curso(models.Model):
    """Curso online ofrecido en el catálogo."""
    titulo = models.CharField(max_length=200)
    area = models.ForeignKey(
        Area, on_delete=models.PROTECT, related_name='cursos'
    )
    instructor = models.CharField(max_length=100)
    nivel = models.CharField(max_length=15, choices=NIVELES, default='basico')
    duracion_horas = models.PositiveIntegerField()
    # Precio en pesos chilenos. 0 significa curso gratuito.
    precio_clp = models.PositiveIntegerField(default=0)
    descripcion = models.TextField()
    # Ruta relativa dentro de /static/, ej: 'cursos/img/python.svg'
    imagen = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ['titulo']

    def __str__(self):
        return self.titulo

    @property
    def es_gratuito(self):
        """Indica si el curso no tiene costo."""
        return self.precio_clp == 0
