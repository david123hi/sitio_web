"""
cursos/urls.py

Archivo de rutas PROPIO de la aplicación 'cursos'.
"""
from django.urls import path
from . import views
from .mantenedores import cursos as mant_cursos

app_name = 'cursos'

urlpatterns = [
    *mant_cursos.urls('gestion/'),
    path('', views.listado_cursos, name='listado'),
    path('<int:curso_id>/', views.detalle_curso, name='detalle'),
]
