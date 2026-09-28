"""
restaurantes/views.py

Vistas de la aplicación "restaurantes". Todos los datos se obtienen
desde la base de datos mediante Django ORM.
"""
from django.http import Http404
from django.shortcuts import render

from .models import Restaurante, TipoCocina


def listado_restaurantes(request):
    """
    Lista los restaurantes almacenados en la base de datos, con filtro
    opcional por tipo de cocina (?tipo=) y búsqueda por nombre (?q=).
    """
    restaurantes = Restaurante.objects.select_related('tipo_cocina').all()

    tipo_filtro = request.GET.get('tipo', 'todos')
    busqueda = request.GET.get('q', '')

    if tipo_filtro != 'todos':
        restaurantes = restaurantes.filter(tipo_cocina__nombre=tipo_filtro)

    if busqueda:
        restaurantes = restaurantes.filter(nombre__icontains=busqueda)

    contexto = {
        'titulo_pagina': 'Guía de Restaurantes',
        'restaurantes': restaurantes,
        'tipos': TipoCocina.objects.all(),
        'tipo_actual': tipo_filtro,
        'busqueda': busqueda,
        'total_restaurantes': Restaurante.objects.count(),
    }
    return render(request, 'restaurantes/listado.html', contexto)


def detalle_restaurante(request, slug):
    """Muestra el detalle de un restaurante, buscado por su slug."""
    restaurante = Restaurante.objects.select_related('tipo_cocina').filter(
        slug=slug
    ).first()

    if restaurante is None:
        raise Http404('El restaurante solicitado no existe.')

    contexto = {
        'titulo_pagina': restaurante.nombre,
        'restaurante': restaurante,
    }
    return render(request, 'restaurantes/detalle.html', contexto)
