from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from cuentas.decorators import requiere_permiso
from .forms import AlertaForm, RequisitoVacunaForm
from .models import Alerta, RequisitoVacuna


# ------------------------------------------------------------------
# Mantenedor de Alertas (el de Vacunas está en mantenedores.py)
# ------------------------------------------------------------------
@requiere_permiso('travel_advisories.view_alerta')
def lista_alerta(request):
    """Listar y buscar alertas (por título, descripción, destino o país)."""
    q = request.GET.get('q', '').strip()
    alertas = Alerta.objects.select_related('pais').prefetch_related('requisitos_vacunas__vacuna')
    if q:
        alertas = alertas.filter(
            Q(titulo__icontains=q)
            | Q(descripcion__icontains=q)
            | Q(pais__nombre__icontains=q)
            | Q(pais__pais__icontains=q)
        )
    return render(request, 'advisories_Main.html', {'alertas': alertas, 'q': q})


@requiere_permiso('travel_advisories.add_alerta')
def crear_alerta(request):
    form = AlertaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        alerta = form.save()
        messages.success(request, f'Alerta "{alerta.titulo}" creada correctamente.')
        return redirect('travel_advisories:lista_alerta')
    return render(request, 'advisories_Form.html', {'form': form, 'titulo': 'Agregar alerta de viaje'})


@requiere_permiso('travel_advisories.change_alerta')
def editar_alerta(request, alerta_id):
    alerta = get_object_or_404(Alerta, id=alerta_id)
    form = AlertaForm(request.POST or None, instance=alerta)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Alerta "{alerta.titulo}" modificada correctamente.')
        return redirect('travel_advisories:lista_alerta')
    return render(request, 'advisories_Form.html', {'form': form, 'titulo': 'Modificar alerta de viaje'})


@requiere_permiso('travel_advisories.delete_alerta')
def eliminar_alerta(request, alerta_id):
    """Pide confirmación (GET) y elimina solo por POST."""
    alerta = get_object_or_404(Alerta, id=alerta_id)
    if request.method == 'POST':
        titulo = alerta.titulo
        alerta.delete()
        messages.success(request, f'Alerta "{titulo}" eliminada correctamente.')
        return redirect('travel_advisories:lista_alerta')
    contexto = {'alerta': alerta, 'requisitos': alerta.requisitos_vacunas.count()}
    return render(request, 'advisories_ConfirmDelete.html', contexto)


@requiere_permiso('travel_advisories.view_alerta', 'travel_advisories.view_requisitovacuna')
def detalle_alerta(request, alerta_id):
    alerta = get_object_or_404(Alerta.objects.select_related('pais'), id=alerta_id)
    requisitos = alerta.requisitos_vacunas.select_related('vacuna')
    return render(request, 'advisories_Details.html', {'alerta': alerta, 'requisitos': requisitos})


# ------------------------------------------------------------------
# TRANSACCIÓN 3: requisitos de vacunación (Alerta + Vacuna + RequisitoVacuna)
# ------------------------------------------------------------------
@requiere_permiso('travel_advisories.add_requisitovacuna')
def agregar_requisito(request, alerta_id):
    alerta = get_object_or_404(Alerta, id=alerta_id)
    form = RequisitoVacunaForm(request.POST or None, alerta=alerta)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            requisito = form.save(commit=False)
            requisito.pais = alerta
            requisito.save()
        messages.success(request, f'Vacuna "{requisito.vacuna}" asociada a la alerta.')
        return redirect('travel_advisories:detalle_alerta', alerta_id=alerta.pk)
    return render(request, 'advisories_Requisito_Form.html', {
        'form': form, 'alerta': alerta, 'titulo': f'Agregar requisito a "{alerta.titulo}"'})


@requiere_permiso('travel_advisories.change_requisitovacuna')
def editar_requisito(request, pk):
    requisito = get_object_or_404(RequisitoVacuna.objects.select_related('pais', 'vacuna'), pk=pk)
    alerta = requisito.pais
    form = RequisitoVacunaForm(request.POST or None, instance=requisito, alerta=alerta)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Requisito modificado correctamente.')
        return redirect('travel_advisories:detalle_alerta', alerta_id=alerta.pk)
    return render(request, 'advisories_Requisito_Form.html', {
        'form': form, 'alerta': alerta, 'titulo': f'Modificar requisito de "{alerta.titulo}"'})


@requiere_permiso('travel_advisories.delete_requisitovacuna')
def eliminar_requisito(request, pk):
    requisito = get_object_or_404(RequisitoVacuna.objects.select_related('pais', 'vacuna'), pk=pk)
    alerta = requisito.pais
    if request.method == 'POST':
        requisito.delete()
        messages.success(request, 'Requisito eliminado correctamente.')
        return redirect('travel_advisories:detalle_alerta', alerta_id=alerta.pk)
    return render(request, 'advisories_Requisito_ConfirmDelete.html', {
        'requisito': requisito, 'alerta': alerta})
