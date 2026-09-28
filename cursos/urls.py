"""
cursos/urls.py

Archivo de rutas PROPIO de la aplicación 'cursos'.
"""
from django.urls import path
from . import views

app_name = 'cursos'

urlpatterns = [
    path('', views.listado_cursos, name='listado'),
    path('<int:curso_id>/', views.detalle_curso, name='detalle'),
]
