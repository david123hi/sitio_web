from django.urls import path
from . import views
from .mantenedores import vacunas as mant_vacunas

app_name = 'travel_advisories'

urlpatterns = [
    path('', views.lista_alerta, name='lista_alerta'),
    path('nueva/', views.crear_alerta, name='crear_alerta'),
    path('<int:alerta_id>/', views.detalle_alerta, name='detalle_alerta'),
    path('<int:alerta_id>/editar/', views.editar_alerta, name='editar_alerta'),
    path('<int:alerta_id>/eliminar/', views.eliminar_alerta, name='eliminar_alerta'),

    # Requisitos de vacunación (transacción)
    path('<int:alerta_id>/requisitos/nuevo/', views.agregar_requisito, name='agregar_requisito'),
    path('requisitos/<int:pk>/editar/', views.editar_requisito, name='editar_requisito'),
    path('requisitos/<int:pk>/eliminar/', views.eliminar_requisito, name='eliminar_requisito'),

    # Mantenedor de vacunas: vacuna_lista / vacuna_crear / vacuna_editar / vacuna_eliminar
    *mant_vacunas.urls('vacunas/'),
]
