from django.contrib import admin
from .models import Continente, Destino


@admin.register(Continente)
class ContinenteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(Destino)
class DestinoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'pais', 'continente', 'precio_clp', 'duracion_dias')
    list_filter = ('continente',)
    search_fields = ('nombre', 'pais', 'slug')
    autocomplete_fields = ('continente',)
    list_select_related = ('continente',)
    prepopulated_fields = {'slug': ('nombre',)}
