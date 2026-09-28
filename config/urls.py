"""
config/urls.py

Archivo de rutas PRINCIPAL del proyecto.
Actúa como punto de entrada y delega (mediante include()) las rutas
de cada aplicación a su propio archivo urls.py, tal como pide el
requerimiento de arquitectura N°3 y N°4 de la pauta.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Cada app tiene su propio urls.py. Aquí solo se "conectan".
    # La app "blog" se monta en la raíz del sitio (incluye la página de inicio).
    path('', include('blog.urls')),
    path('destinos/', include('destinos.urls')),
    path('cursos/', include('cursos.urls')),
    path('restaurantes/', include('restaurantes.urls')),

]
