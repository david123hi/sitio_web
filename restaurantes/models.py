"""
restaurantes/models.py

Módulo "Guía de Restaurantes": restaurantes recomendados agrupados
por tipo de cocina.

Relación: 1 TipoCocina -> N Restaurantes (ForeignKey).
"""
from django.db import models

from .choices import RANGOS_PRECIO


class TipoCocina(models.Model):
    """Tipo de cocina de un restaurante (Chilena, Italiana, etc.)."""
    nombre = models.CharField(max_length=60, unique=True)

    class Meta:
        verbose_name = "Tipo de cocina"
        verbose_name_plural = "Tipos de cocina"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Restaurante(models.Model):
    """Restaurante recomendado en la guía."""
    slug = models.SlugField(max_length=150, unique=True)
    nombre = models.CharField(max_length=150)
    tipo_cocina = models.ForeignKey(
        TipoCocina, on_delete=models.PROTECT, related_name='restaurantes'
    )
    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    rango_precio = models.CharField(max_length=3, choices=RANGOS_PRECIO, default='$$')
    # Calificación de 0.0 a 9.9 (se usa una escala de 1.0 a 5.0)
    calificacion = models.DecimalField(max_digits=2, decimal_places=1)
    descripcion = models.TextField()
    # Ruta relativa dentro de /static/, ej: 'restaurantes/img/sabores.svg'
    imagen = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Restaurante"
        verbose_name_plural = "Restaurantes"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def estrellas(self):
        """Representa la calificación como estrellas (redondeada)."""
        return '★' * int(round(self.calificacion))
