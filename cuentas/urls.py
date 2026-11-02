from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import LoginForm, NuevaClaveForm, RecuperarForm

app_name = 'cuentas'

urlpatterns = [
    # --- Inicio y cierre de sesión ---
    path('login/', auth_views.LoginView.as_view(
        template_name='cuentas/login.html', authentication_form=LoginForm,
        redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # solo POST (Django 5)

    # --- Dashboard por perfil ---
    path('dashboard/', views.dashboard, name='dashboard'),

    # --- Gestión de usuarios (solo Administrador) ---
    path('usuarios/', views.usuarios_lista, name='usuarios'),
    path('usuarios/nuevo/', views.usuario_crear, name='usuario_crear'),
    path('usuarios/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('usuarios/<int:pk>/eliminar/', views.usuario_eliminar, name='usuario_eliminar'),

    # --- Recuperación de contraseña por correo (token firmado de Django) ---
    path('recuperar/', auth_views.PasswordResetView.as_view(
        template_name='cuentas/recuperar_form.html',
        form_class=RecuperarForm,
        email_template_name='cuentas/recuperar_correo.txt',
        subject_template_name='cuentas/recuperar_asunto.txt',
        success_url=reverse_lazy('cuentas:recuperar_enviado')), name='recuperar'),
    path('recuperar/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='cuentas/recuperar_enviado.html'), name='recuperar_enviado'),
    path('recuperar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='cuentas/recuperar_confirmar.html',
        form_class=NuevaClaveForm,
        success_url=reverse_lazy('cuentas:recuperar_completo')), name='recuperar_confirmar'),
    path('recuperar/completo/', auth_views.PasswordResetCompleteView.as_view(
        template_name='cuentas/recuperar_completo.html'), name='recuperar_completo'),
]
