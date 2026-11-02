from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from cuentas.decorators import requiere_permiso
from .forms import ParticipacionForm, ViajeConOrganizadorForm, ViajeForm
from .models import Participacion, Viaje


# ------------------------------------------------------------------
# Mantenedor de Viajes (el de Viajeros está en mantenedores.py)
# ------------------------------------------------------------------
@requiere_permiso('travelers.view_viaje')
def lista_viajes(request):
    q = request.GET.get('q', '').strip()
    viajes = Viaje.objects.select_related('destino')
    if q:
        viajes = viajes.filter(
            Q(actividad__icontains=q)
            | Q(destino__nombre__icontains=q)
            | Q(destino__pais__icontains=q)
        )
    return render(request, 'travelers_Main.html', {'viajes': viajes, 'q': q})


@requiere_permiso('travelers.add_viaje')
def crear_viaje(request):
    form = ViajeForm(request.POST or None, initial={'estado': 'A'})
    if request.method == 'POST' and form.is_valid():
        viaje = form.save()
        messages.success(request, f'Viaje "{viaje.actividad}" creado correctamente.')
        return redirect('travelers:lista_viajes')
    return render(request, 'travelers_Form.html', {'form': form, 'titulo': 'Agregar viaje'})


@requiere_permiso('travelers.change_viaje')
def editar_viaje(request, viaje_id):
    viaje = get_object_or_404(Viaje, id=viaje_id)
    form = ViajeForm(request.POST or None, instance=viaje)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Viaje "{viaje.actividad}" modificado correctamente.')
        return redirect('travelers:lista_viajes')
    return render(request, 'travelers_Form.html', {'form': form, 'titulo': 'Modificar viaje'})


@requiere_permiso('travelers.delete_viaje')
def eliminar_viaje(request, viaje_id):
    """Pide confirmación (GET) y elimina solo por POST."""
    viaje = get_object_or_404(Viaje, id=viaje_id)
    if request.method == 'POST':
        nombre = viaje.actividad
        viaje.delete()
        messages.success(request, f'Viaje "{nombre}" eliminado correctamente.')
        return redirect('travelers:lista_viajes')
    contexto = {'viaje': viaje, 'participantes': viaje.participaciones.count()}
    return render(request, 'travelers_ConfirmDelete.html', contexto)


@requiere_permiso('travelers.view_viaje', 'travelers.view_participacion')
def detalle_viaje(request, viaje_id):
    viaje = get_object_or_404(Viaje, id=viaje_id)
    q = request.GET.get('q', '').strip()
    participaciones = Participacion.objects.filter(viaje=viaje).select_related('viajero')
    if q:
        participaciones = participaciones.filter(
            Q(viajero__nombre__icontains=q) | Q(viajero__correo__icontains=q))
    contexto = {'viaje': viaje, 'participaciones': participaciones, 'q': q}
    return render(request, 'travelers_Details.html', contexto)


# ------------------------------------------------------------------
# TRANSACCIÓN 1: programar un viaje con su organizador (2 entidades, 1 paso)
# ------------------------------------------------------------------
@requiere_permiso('travelers.add_viaje', 'travelers.add_participacion')
def programar_viaje(request):
    form = ViajeConOrganizadorForm(request.POST or None, initial={'estado': 'A'})
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            viaje = form.save()
            Participacion.objects.create(
                viaje=viaje, viajero=form.cleaned_data['organizador'], rol='O', estado='C')
            viaje.sincronizar_estado()
        messages.success(request, f'Viaje "{viaje.actividad}" programado con su organizador.')
        return redirect('travelers:detalle_viaje', viaje_id=viaje.pk)
    return render(request, 'travelers_Form.html', {
        'form': form, 'titulo': 'Programar viaje con organizador'})


# ------------------------------------------------------------------
# TRANSACCIÓN 2: inscripción de viajeros en un viaje (Viaje + Viajero + Participacion)
# Valida duplicados, organizador único y cupos; actualiza el estado del viaje.
# ------------------------------------------------------------------
def _guardar_participacion(form, viaje_id):
    """Guarda la participación y sincroniza el viaje en una sola transacción atómica."""
    with transaction.atomic():
        viaje = Viaje.objects.select_for_update().get(pk=viaje_id)
        participacion = form.save(commit=False)
        if participacion.estado == 'C':
            confirmados = viaje.participaciones.filter(estado='C').exclude(pk=participacion.pk).count()
            if confirmados >= viaje.cupos:  # revalida con el viaje bloqueado
                raise ValidationError('No quedan cupos disponibles para confirmar esta participación.')
        participacion.viaje = viaje
        participacion.save()
        viaje.sincronizar_estado()
    return participacion


@requiere_permiso('travelers.add_participacion')
def agregar_participacion(request, viaje_id):
    viaje = get_object_or_404(Viaje, id=viaje_id)
    form = ParticipacionForm(request.POST or None, viaje=viaje)
    if request.method == 'POST' and form.is_valid():
        try:
            participacion = _guardar_participacion(form, viaje.pk)
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, f'{participacion.viajero} fue inscrito en "{viaje.actividad}".')
            return redirect('travelers:detalle_viaje', viaje_id=viaje.pk)
    return render(request, 'travelers_Participacion_Form.html', {
        'form': form, 'viaje': viaje, 'titulo': f'Inscribir participante en "{viaje.actividad}"'})


@requiere_permiso('travelers.change_participacion')
def editar_participacion(request, pk):
    participacion = get_object_or_404(Participacion.objects.select_related('viaje', 'viajero'), pk=pk)
    viaje = participacion.viaje
    form = ParticipacionForm(request.POST or None, instance=participacion, viaje=viaje)
    if request.method == 'POST' and form.is_valid():
        try:
            _guardar_participacion(form, viaje.pk)
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, 'Participación modificada correctamente.')
            return redirect('travelers:detalle_viaje', viaje_id=viaje.pk)
    return render(request, 'travelers_Participacion_Form.html', {
        'form': form, 'viaje': viaje, 'titulo': f'Modificar participación de {participacion.viajero}'})


@requiere_permiso('travelers.delete_participacion')
def eliminar_participacion(request, pk):
    participacion = get_object_or_404(Participacion.objects.select_related('viaje', 'viajero'), pk=pk)
    viaje = participacion.viaje
    if request.method == 'POST':
        with transaction.atomic():
            viaje_bloqueado = Viaje.objects.select_for_update().get(pk=viaje.pk)
            participacion.delete()
            viaje_bloqueado.sincronizar_estado()
        messages.success(request, 'Participación eliminada correctamente.')
        return redirect('travelers:detalle_viaje', viaje_id=viaje.pk)
    return render(request, 'travelers_Participacion_ConfirmDelete.html', {
        'participacion': participacion, 'viaje': viaje})
