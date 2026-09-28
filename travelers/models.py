from django.db import models
from destinos.models import Destino
from .status import status
from .tr_roles import roles
from .tr_status import trStatus

# Create your models here.

# Modelo del viaje
class Viaje (models.Model):
    actividad = models.CharField(max_length=100)
    destino = models.ForeignKey(Destino, on_delete=models.CASCADE, related_name='viajes')
    inicio = models.DateField()
    fin = models.DateField()
    cupos = models.PositiveIntegerField(max_length=10)
    estado = models.CharField(max_length=1, choices=status, default='0', verbose_name='Estado')

    @property
    def cupos_disponibles(self):
        inscritos = self.participaciones.filter(estado='C').count()
        return self.cupos - inscritos
    def __str__(self):
        return self.actividad
    class Meta:
        verbose_name = "Viaje"
        verbose_name_plural = "Viajes"
        ordering = ['inicio', 'fin']


#Modelo del viajero
class Viajero (models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Viajero"
        verbose_name_plural = "Viajeros"
        ordering = ['nombre']


#Modelo de la participacion del viajero en un viaje
class Participacion (models.Model):
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE, related_name='participaciones')
    viajero = models.ForeignKey(Viajero, on_delete=models.CASCADE, related_name='participaciones')
    rol = models.CharField(max_length=1, choices=roles, default='V', verbose_name='Rol')
    estado = models.CharField(max_length=1, choices=trStatus, default='P', verbose_name='Estado')

    def __str__(self):
        return f"{self.viajero.nombre} - {self.viaje.actividad}"

    class Meta:
        verbose_name = "Participacion"
        verbose_name_plural = "Participaciones"
        ordering = ['viaje', 'viajero']


