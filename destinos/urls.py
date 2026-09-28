"""
destinos/urls.py

Archivo de rutas PROPIO de la aplicación 'destinos'.
"""

from django.urls import path
from . import views

app_name = 'destinos'

urlpatterns = [
    path('', views.listado_destinos, name='listado'),
    path('<slug:slug>/', views.detalle_destino, name='detalle'),
]
