from django.contrib import admin
from .models import Categoria, Articulo


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'categoria', 'autor', 'fecha')
    list_filter = ('categoria', 'autor')
    search_fields = ('titulo', 'resumen', 'contenido', 'autor')
    autocomplete_fields = ('categoria',)
    list_select_related = ('categoria',)
    date_hierarchy = 'fecha'
