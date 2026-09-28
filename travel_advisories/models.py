from django.db import models
from destinos.models import Destino

class Alerta (models.Model):
    titulo = models.CharField(max_length=100)
    pais = models.ForeignKey(Destino, on_delete=models.CASCADE, related_name='alertas')
    nivel = models.CharField(max_length=1, choices=[('B', 'Bajo'), ('M', 'Medio'), ('A', 'Alto'), ('E', 'Extremo')], default='B', verbose_name='Nivel de alerta')
    emision = models.DateField()
    descripcion = models.CharField(max_length=100, default="Sin descripción")
    expiracion = models.DateField()
    activo = models.BooleanField(default=True, verbose_name='Activo')

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Alerta"
        verbose_name_plural = "Alertas"
        ordering = ['emision']
        

class Vacuna (models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Vacuna"
        verbose_name_plural = "Vacunas"
        ordering = ['nombre']

class RequisitoVacuna (models.Model):
    pais = models.ForeignKey(Alerta, on_delete=models.CASCADE, related_name='requisitos_vacunas')
    vacuna = models.ForeignKey(Vacuna, on_delete=models.CASCADE, related_name='requisitos_vacunas')
    tipo = models.CharField(max_length=1, choices=[('O', 'Obligatoria'), ('R', 'Recomendada')], default='R', verbose_name='Tipo de requisito')
    notas = models.TextField(blank=True, null=True, verbose_name='Notas adicionales')

    def __str__(self):
        return f"{self.pais} - {self.vacuna}"

    class Meta:
        verbose_name = "Requisito de Vacuna"
        verbose_name_plural = "Requisitos de Vacunas"
        ordering = ['pais', 'tipo']