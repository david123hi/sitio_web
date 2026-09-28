"""
destinos/views.py

Vistas de la aplicación "destinos" (destinos de viaje).

A partir de la Evaluación Sumativa N°2, los datos ya NO se leen desde
destinos.json: se obtienen desde la base de datos relacional mediante
Django ORM.
"""
from django.http import Http404
from django.shortcuts import render
from .models import Continente, Destino


def listado_destinos(request):
    """
    Vista 1 de la app 'destinos': lista todos los destinos almacenados
    en la base de datos, con filtro opcional por continente
    (?continente=) y búsqueda simple por nombre (?q=).
    """
    destinos = Destino.objects.select_related('continente').all()

    continente_filtro = request.GET.get('continente', 'todos')
    busqueda = request.GET.get('q', '')

    if continente_filtro != 'todos':
        destinos = destinos.filter(continente__nombre=continente_filtro)

    if busqueda:
        destinos = destinos.filter(nombre__icontains=busqueda)

    continentes_disponibles = Continente.objects.all()

    contexto = {
        'titulo_pagina': 'Destinos de Viaje',
        'destinos': destinos,
        'continentes': continentes_disponibles,
        'continente_actual': continente_filtro,
        'busqueda': busqueda,
        'total_destinos': Destino.objects.count(),
    }
    return render(request, 'destinos/listado.html', contexto)


def detalle_destino(request, slug):
    """
    Vista 2 de la app 'destinos': muestra el detalle de un destino
    específico, buscado por su 'slug' directamente en la base de datos.
    """
    destino = Destino.objects.select_related('continente').filter(
        slug=slug
    ).first()

    if destino is None:
        raise Http404('El destino solicitado no existe.')

    contexto = {
        'titulo_pagina': destino.nombre,
        'destino': destino,
    }
    return render(request, 'destinos/detalle.html', contexto)
