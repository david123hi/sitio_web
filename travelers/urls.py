from django.urls import path
from . import views

app_name = 'travelers'

urlpatterns = [
    path('', views.lista_viajes, name='lista_viajes'),
    path('<int:viaje_id>/', views.detalle_viaje, name='detalle_viaje'),
    path('viajeros/', views.detalle_viajeros, name='detalle_viajeros'),
]