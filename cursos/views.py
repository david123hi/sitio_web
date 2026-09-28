"""
cursos/views.py

Vistas de la aplicación "cursos". Todos los datos se obtienen desde la
base de datos mediante Django ORM.
"""
from django.http import Http404
from django.shortcuts import render

from .models import Area, Curso


def listado_cursos(request):
    """
    Lista los cursos almacenados en la base de datos, con filtro
    opcional por área (?area=) y búsqueda por título (?q=).
    """
    cursos = Curso.objects.select_related('area').all()

    area_filtro = request.GET.get('area', 'todas')
    busqueda = request.GET.get('q', '')

    if area_filtro != 'todas':
        cursos = cursos.filter(area__nombre=area_filtro)

    if busqueda:
        cursos = cursos.filter(titulo__icontains=busqueda)

    contexto = {
        'titulo_pagina': 'Cursos Online',
        'cursos': cursos,
        'areas': Area.objects.all(),
        'area_actual': area_filtro,
        'busqueda': busqueda,
        'total_cursos': Curso.objects.count(),
    }
    return render(request, 'cursos/listado.html', contexto)


def detalle_curso(request, curso_id):
    """Muestra el detalle de un curso, buscado por su id en la base de datos."""
    curso = Curso.objects.select_related('area').filter(id=curso_id).first()

    if curso is None:
        raise Http404('El curso solicitado no existe.')

    contexto = {
        'titulo_pagina': curso.titulo,
        'curso': curso,
    }
    return render(request, 'cursos/detalle.html', contexto)
