"""
restaurantes/urls.py

Archivo de rutas PROPIO de la aplicación 'restaurantes'.
"""
from django.urls import path
from . import views
from .mantenedores import restaurantes as mant_restaurantes

app_name = 'restaurantes'

urlpatterns = [
    *mant_restaurantes.urls('gestion/'),
    path('', views.listado_restaurantes, name='listado'),
    path('<slug:slug>/', views.detalle_restaurante, name='detalle'),
]
