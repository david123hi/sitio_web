from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import ViajeForm
from .models import Viaje
from .models import Participacion
from .models import Viajero

@login_required
def lista_viajes(request):
    q = request.GET.get('q', '').strip()
    viajes = Viaje.objects.select_related('destino')
    if q:
        viajes = viajes.filter(
            Q(actividad__icontains=q)
            | Q(destino__nombre__icontains=q)
            | Q(destino__pais__icontains=q)
        )
    contexto = {
        'viajes': viajes,
        'q': q
    }
    return render(request, 'travelers_Main.html', contexto)


@login_required
def crear_viaje(request):
    form = ViajeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        viaje = form.save()
        messages.success(request, f'Viaje "{viaje.actividad}" creado correctamente.')
        return redirect('travelers:lista_viajes')
    return render(request, 'travelers_Form.html', {'form': form, 'titulo': 'Agregar viaje'})


@login_required
def editar_viaje(request, viaje_id):
    viaje = get_object_or_404(Viaje, id=viaje_id)
    form = ViajeForm(request.POST or None, instance=viaje)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Viaje "{viaje.actividad}" modificado correctamente.')
        return redirect('travelers:lista_viajes')
    return render(request, 'travelers_Form.html', {'form': form, 'titulo': 'Modificar viaje'})


@login_required
def eliminar_viaje(request, viaje_id):
    """Pide confirmación (GET) y elimina solo por POST."""
    viaje = get_object_or_404(Viaje, id=viaje_id)
    if request.method == 'POST':
        nombre = viaje.actividad
        viaje.delete()
        messages.success(request, f'Viaje "{nombre}" eliminado correctamente.')
        return redirect('travelers:lista_viajes')
    contexto = {
        'viaje': viaje,
        'participantes': viaje.participaciones.count(),
    }
    return render(request, 'travelers_ConfirmDelete.html', contexto)

@login_required
def detalle_viaje(request, viaje_id):
    viaje = Viaje.objects.get(id=viaje_id)
    participaciones = Participacion.objects.filter(viaje=viaje).select_related('viajero')
    contexto = {
        'viaje': viaje,
        'participaciones': participaciones
    }
    return render(request, 'travelers_Details.html', contexto)
@login_required
def detalle_viajeros(request):
    viajeros = Viajero.objects.all()
    contexto = {
        'viajeros': viajeros
    }
    return render(request, 'travelers_Manage.html', contexto)
