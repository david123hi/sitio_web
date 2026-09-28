from django.contrib import admin
from .models import Alerta, Vacuna, RequisitoVacuna

@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'pais', 'emision', 'expiracion')
    list_filter = ('pais', 'emision', 'expiracion')
    search_fields = ('titulo', 'descripcion')

@admin.register(Vacuna)
class VacunaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre', 'descripcion')

@admin.register(RequisitoVacuna)
class RequisitoVacunaAdmin(admin.ModelAdmin):
    list_display = ('vacuna', 'tipo')
    list_filter = ('tipo', 'vacuna')
