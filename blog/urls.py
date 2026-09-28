"""
blog/urls.py

Archivo de rutas PROPIO de la aplicación 'blog'.
Cada app define sus propias rutas y luego el urls.py principal
del proyecto las incluye con include().
"""

from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('articulos/', views.lista_articulos, name='lista_articulos'),
    path('articulos/<int:articulo_id>/', views.detalle_articulo, name='detalle_articulo'),
]
