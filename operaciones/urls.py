from django.urls import path

from . import views

app_name = 'operaciones'

urlpatterns = [
    path('reservas-destino/', views.ListaReservasDestinoView.as_view(), name='destino_lista'),
    path('reservas-destino/nueva/', views.CrearReservaDestinoView.as_view(), name='destino_nueva'),
    path('reservas-mesa/', views.ListaReservasMesaView.as_view(), name='mesa_lista'),
    path('reservas-mesa/nueva/', views.CrearReservaMesaView.as_view(), name='mesa_nueva'),
    path('inscripciones-curso/', views.ListaInscripcionesCursoView.as_view(), name='curso_lista'),
    path('inscripciones-curso/nueva/', views.CrearInscripcionCursoView.as_view(), name='curso_nueva'),
    path('suscripciones-blog/', views.ListaSuscripcionesBlogView.as_view(), name='blog_lista'),
    path('suscripciones-blog/nueva/', views.CrearSuscripcionBlogView.as_view(), name='blog_nueva'),
]
