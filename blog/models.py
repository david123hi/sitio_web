"""
blog/models.py

Modelos de la aplicación 'blog'. Reemplazan la fuente de datos en
data/articulos.json (Evaluación Sumativa N°1) por persistencia real
en base de datos relacional mediante Django ORM (Evaluación N°2).
"""
from django.db import models


class Categoria(models.Model):
    """Categoría de un artículo (Backend, Frontend, IA, etc.)."""
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Articulo(models.Model):
    """Artículo publicado en el blog de tecnología."""
    titulo = models.CharField(max_length=200)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name='articulos'
    )
    autor = models.CharField(max_length=100)
    fecha = models.DateField()
    resumen = models.CharField(max_length=300)
    contenido = models.TextField()
    # Ruta relativa dentro de /static/, ej: 'blog/img/django.svg'
    imagen = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Artículo"
        verbose_name_plural = "Artículos"
        ordering = ['-fecha']

    def __str__(self):
        return self.titulo

    @property
    def tiempo_lectura(self):
        """Estima minutos de lectura a partir del contenido (mínimo 1)."""
        palabras_por_minuto = 200
        cantidad_palabras = len(self.contenido.split())
        tiempo = cantidad_palabras / palabras_por_minuto
        return 1 if tiempo < 1 else round(tiempo)
