from django.contrib import admin
from .models import Area, Curso


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'area', 'instructor', 'nivel', 'duracion_horas', 'precio_clp')
    list_filter = ('area', 'nivel')
    search_fields = ('titulo', 'instructor', 'descripcion')
    autocomplete_fields = ('area',)
    list_select_related = ('area',)
