from django.contrib import admin
from .models import TipoCocina, Restaurante


@admin.register(TipoCocina)
class TipoCocinaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'tipo_cocina', 'ciudad', 'rango_precio', 'calificacion')
    list_filter = ('tipo_cocina', 'rango_precio', 'ciudad')
    search_fields = ('nombre', 'ciudad', 'direccion', 'slug')
    autocomplete_fields = ('tipo_cocina',)
    list_select_related = ('tipo_cocina',)
    prepopulated_fields = {'slug': ('nombre',)}
