from django.urls import path
from . import views

app_name = 'travel_advisories'

urlpatterns = [
    path('', views.lista_alerta, name='lista_alerta')
]