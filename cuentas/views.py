"""Vistas de la app cuentas: dashboards por perfil y gestión de usuarios."""
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from blog.models import Articulo
from cursos.models import Curso
from destinos.models import Destino
from restaurantes.models import Restaurante
from travel_advisories.models import Alerta, Vacuna
from travelers.models import Participacion, Viaje, Viajero

from .decorators import requiere_permiso
from .forms import UsuarioCrearForm, UsuarioEditarForm
from .roles import ADMINISTRADOR, ADMINISTRATIVO, SUPERVISOR, rol_de


@login_required
def dashboard(request):
    """Muestra el panel que corresponde al perfil del usuario autenticado."""
    rol = rol_de(request.user)
    hoy = date.today()

    if rol == ADMINISTRADOR:
        contexto = {
            'totales': [
                ('Usuarios', User.objects.count()),
                ('Artículos', Articulo.objects.count()),
                ('Destinos', Destino.objects.count()),
                ('Cursos', Curso.objects.count()),
                ('Restaurantes', Restaurante.objects.count()),
                ('Viajes', Viaje.objects.count()),
                ('Viajeros', Viajero.objects.count()),
                ('Participaciones', Participacion.objects.count()),
                ('Alertas', Alerta.objects.count()),
                ('Vacunas', Vacuna.objects.count()),
            ],
            'usuarios_recientes': User.objects.order_by('-date_joined')[:5],
        }
        plantilla = 'cuentas/dashboard_administrador.html'
    elif rol == SUPERVISOR:
        contexto = {
            'viajes_abiertos': Viaje.objects.filter(estado='A').count(),
            'viajes_completos': Viaje.objects.filter(estado='C').count(),
            'pendientes': Participacion.objects.filter(estado='P').count(),
            'alertas_graves': Alerta.objects.filter(
                activo=True, expiracion__gte=hoy, nivel__in=['A', 'E']).count(),
            'proximos_viajes': Viaje.objects.select_related('destino').filter(
                inicio__gte=hoy).exclude(estado='F')[:5],
            'alertas_activas': Alerta.objects.select_related('pais').filter(
                activo=True, expiracion__gte=hoy).order_by('-nivel')[:5],
        }
        plantilla = 'cuentas/dashboard_supervisor.html'
    else:
        contexto = {
            'sin_perfil': rol != ADMINISTRATIVO,
            'viajes_abiertos': Viaje.objects.filter(estado='A').count(),
            'viajeros': Viajero.objects.count(),
        }
        plantilla = 'cuentas/dashboard_administrativo.html'

    contexto['rol'] = rol
    return render(request, plantilla, contexto)


@requiere_permiso('auth.view_user')
def usuarios_lista(request):
    q = request.GET.get('q', '').strip()
    usuarios = User.objects.prefetch_related('groups').order_by('username')
    if q:
        usuarios = usuarios.filter(
            Q(username__icontains=q) | Q(email__icontains=q)
            | Q(first_name__icontains=q) | Q(last_name__icontains=q)
        )
    return render(request, 'cuentas/usuarios_lista.html', {'usuarios': usuarios, 'q': q})


@requiere_permiso('auth.add_user')
def usuario_crear(request):
    form = UsuarioCrearForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        usuario = form.save()
        messages.success(request, f'Usuario "{usuario.username}" creado y asignado al perfil '
                                  f'{form.cleaned_data["grupo"].name}.')
        return redirect('cuentas:usuarios')
    return render(request, 'cuentas/usuario_form.html', {'form': form, 'titulo': 'Crear usuario'})


@requiere_permiso('auth.change_user')
def usuario_editar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    form = UsuarioEditarForm(request.POST or None, instance=usuario)
    if request.method == 'POST' and form.is_valid():
        if usuario == request.user and not form.cleaned_data['is_active']:
            form.add_error('is_active', 'No puedes desactivar tu propio usuario.')
        else:
            form.save()
            messages.success(request, f'Usuario "{usuario.username}" modificado correctamente.')
            return redirect('cuentas:usuarios')
    return render(request, 'cuentas/usuario_form.html', {
        'form': form, 'titulo': f'Modificar usuario: {usuario.username}'})


@requiere_permiso('auth.delete_user')
def usuario_eliminar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if usuario == request.user or usuario.is_superuser:
        messages.error(request, 'No puedes eliminar tu propio usuario ni un superusuario.')
        return redirect('cuentas:usuarios')
    if request.method == 'POST':
        nombre = usuario.username
        usuario.delete()
        messages.success(request, f'Usuario "{nombre}" eliminado correctamente.')
        return redirect('cuentas:usuarios')
    return render(request, 'cuentas/usuario_confirm_delete.html', {'usuario_obj': usuario})
