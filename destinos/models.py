"""
destinos/models.py

Modelos de la aplicación 'destinos'. Reemplazan la fuente de datos en
data/destinos.json (Evaluación Sumativa N°1) por persistencia real
en base de datos relacional mediante Django ORM (Evaluación N°2).
"""
from django.db import models


class Continente(models.Model):
    """Continente al que pertenece un destino de viaje."""
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Continente"
        verbose_name_plural = "Continentes"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Destino(models.Model):
    """Destino de viaje recomendado."""
    slug = models.SlugField(max_length=150, unique=True)
    nombre = models.CharField(max_length=150)
    pais = models.CharField(max_length=100)
    continente = models.ForeignKey(
        Continente, on_delete=models.PROTECT, related_name='destinos'
    )
    precio_clp = models.PositiveIntegerField()
    duracion_dias = models.PositiveIntegerField()
    descripcion = models.TextField()
    # Ruta relativa dentro de /static/, ej: 'destinos/img/kioto.svg'
    imagen = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Destino"
        verbose_name_plural = "Destinos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def categoria_precio(self):
        """Clasifica el destino según su precio de referencia."""
        if self.precio_clp < 500000:
            return 'Económico'
        elif self.precio_clp < 1200000:
            return 'Moderado'
        return 'Premium'
