from django.contrib import admin
from .models import Viaje, Viajero, Participacion

@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    list_display = ('id', 'actividad', 'destino', 'inicio', 'fin', 'cupos', 'estado')
    list_filter = ('destino', 'estado')
    search_fields = ('actividad',)
    ordering = ('inicio',)
    autocomplete_fields = ('destino',)

@admin.register(Participacion)
class ParticipacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'viaje', 'viajero', 'rol', 'estado')
    list_filter = ('rol', 'estado')
    search_fields = ('viaje__actividad', 'viajero__nombre')
    ordering = ('viaje',)
    autocomplete_fields = ('viaje', 'viajero')

@admin.register(Viajero)
class ViajeroAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'correo')
    search_fields = ('nombre', 'correo')
    ordering = ('nombre',)

