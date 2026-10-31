from django.urls import path
from . import views

app_name = 'travel_advisories'

urlpatterns = [
    path('', views.lista_alerta, name='lista_alerta')
    path('new/', views.crear_alerta, name='crear_alerta')
     path('<int:alerta_id>/editar/', views.editar_alerta, name='editar_alerta'),
        path('<int:alerta_id>/eliminar/', views.eliminar_alerta, name='eliminar_alerta'),

]