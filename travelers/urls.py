from django.urls import path
from . import views

app_name = 'travelers'

urlpatterns = [
    path('', views.lista_viajes, name='lista_viajes'),
    path('nuevo/', views.crear_viaje, name='crear_viaje'),
    path('<int:viaje_id>/', views.detalle_viaje, name='detalle_viaje'),
    path('<int:viaje_id>/editar/', views.editar_viaje, name='editar_viaje'),
    path('<int:viaje_id>/eliminar/', views.eliminar_viaje, name='eliminar_viaje'),
    path('viajeros/', views.detalle_viajeros, name='detalle_viajeros'),
]
