"""
destinos/urls.py

Archivo de rutas PROPIO de la aplicación 'destinos'.
"""

from django.urls import path
from . import views
from .mantenedores import destinos as mant_destinos

app_name = 'destinos'

urlpatterns = [
    *mant_destinos.urls('gestion/'),
    path('', views.listado_destinos, name='listado'),
    path('<slug:slug>/', views.detalle_destino, name='detalle'),
]
