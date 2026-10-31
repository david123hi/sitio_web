from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import AlertaForm
from .models import Alerta
# Create your views here.


@login_required
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
    contexto = {
        'alertas': alertas,
        'q': q
    }
    return render(request, 'advisories_Main.html', contexto)


@login_required
def crear_alerta(request):
    form = AlertaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        alerta = form.save()
        messages.success(request, f'Alerta "{alerta.titulo}" creada correctamente.')
        return redirect('travel_advisories:lista_alerta')
    return render(request, 'advisories_Form.html', {'form': form, 'titulo': 'Agregar alerta de viaje'})


@login_required
def editar_alerta(request, alerta_id):
    alerta = get_object_or_404(Alerta, id=alerta_id)
    form = AlertaForm(request.POST or None, instance=alerta)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Alerta "{alerta.titulo}" modificada correctamente.')
        return redirect('travel_advisories:lista_alerta')
    return render(request, 'advisories_Form.html', {'form': form, 'titulo': 'Modificar alerta de viaje'})


@login_required
def eliminar_alerta(request, alerta_id):
    """Pide confirmación (GET) y elimina solo por POST."""
    alerta = get_object_or_404(Alerta, id=alerta_id)
    if request.method == 'POST':
        titulo = alerta.titulo
        alerta.delete()
        messages.success(request, f'Alerta "{titulo}" eliminada correctamente.')
        return redirect('travel_advisories:lista_alerta')
    contexto = {
        'alerta': alerta,
        'requisitos': alerta.requisitos_vacunas.count(),
    }
    return render(request, 'advisories_ConfirmDelete.html', contexto)
