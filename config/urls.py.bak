"""
config/urls.py

Archivo de rutas PRINCIPAL del proyecto.
Actúa como punto de entrada y delega (mediante include()) las rutas
de cada aplicación a su propio archivo urls.py.

Evaluación N°3: se elimina la ruta /admin/. Toda la administración del
sistema se hace desde las interfaces propias (Django Templates).
Si en algún momento se necesitara Django Admin solo para soporte técnico,
basta con volver a agregar:  path('admin/', admin.site.urls)
"""

from django.urls import path, include

urlpatterns = [
    # Autenticación, dashboards y gestión de usuarios
    path('cuentas/', include('cuentas.urls')),

    # Cada app tiene su propio urls.py. Aquí solo se "conectan".
    # La app "blog" se monta en la raíz del sitio (incluye la página de inicio).
    path('', include('blog.urls')),
    path('destinos/', include('destinos.urls')),
    path('cursos/', include('cursos.urls')),
    path('restaurantes/', include('restaurantes.urls')),
    path('viajes/', include('travelers.urls')),
    path('travel_advisories/', include('travel_advisories.urls')),
]
