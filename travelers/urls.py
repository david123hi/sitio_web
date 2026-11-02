from django.urls import path
from . import views
from .mantenedores import viajeros as mant_viajeros

app_name = 'travelers'

urlpatterns = [
    path('', views.lista_viajes, name='lista_viajes'),
    path('nuevo/', views.crear_viaje, name='crear_viaje'),
    path('programar/', views.programar_viaje, name='programar_viaje'),
    path('<int:viaje_id>/', views.detalle_viaje, name='detalle_viaje'),
    path('<int:viaje_id>/editar/', views.editar_viaje, name='editar_viaje'),
    path('<int:viaje_id>/eliminar/', views.eliminar_viaje, name='eliminar_viaje'),

    # Participaciones (transacción de inscripción)
    path('<int:viaje_id>/participantes/nuevo/', views.agregar_participacion, name='agregar_participacion'),
    path('participantes/<int:pk>/editar/', views.editar_participacion, name='editar_participacion'),
    path('participantes/<int:pk>/eliminar/', views.eliminar_participacion, name='eliminar_participacion'),

    # Mantenedor de viajeros: viajero_lista / viajero_crear / viajero_editar / viajero_eliminar
    *mant_viajeros.urls('viajeros/'),
]
