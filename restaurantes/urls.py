"""
restaurantes/urls.py

Archivo de rutas PROPIO de la aplicación 'restaurantes'.
"""
from django.urls import path
from . import views

app_name = 'restaurantes'

urlpatterns = [
    path('', views.listado_restaurantes, name='listado'),
    path('<slug:slug>/', views.detalle_restaurante, name='detalle'),
]
