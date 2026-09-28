"""
blog/views.py

Vistas de la aplicación "blog" (artículos de tecnología).

A partir de la Evaluación Sumativa N°2, los datos ya NO se leen desde
articulos.json: se obtienen desde la base de datos relacional mediante
Django ORM. La lógica de negocio (tiempo de lectura, filtro por
categoría) se mantiene igual que en la Evaluación N°1.
"""
from django.shortcuts import render
from .models import Articulo, Categoria


def inicio(request):
    """
    Vista 1 de la app 'blog': página de inicio / presentación.
    Muestra un resumen general y los 3 artículos más recientes.
    """
    articulos = Articulo.objects.select_related('categoria').all()

    total_articulos = articulos.count()
    categorias = Categoria.objects.all()
    ultimos_articulos = articulos.order_by('-fecha')[:3]

    contexto = {
        'titulo_pagina': 'Inicio - Blog de Tecnología',
        'total_articulos': total_articulos,
        'categorias': categorias,
        'ultimos_articulos': ultimos_articulos,
    }
    return render(request, 'blog/inicio.html', contexto)


def lista_articulos(request):
    """
    Vista 2 de la app 'blog': lista TODOS los artículos almacenados en
    la base de datos y permite filtrar por categoría usando un
    parámetro ?categoria= en la URL, además de una búsqueda simple
    por título mediante ?q=.
    """
    articulos = Articulo.objects.select_related('categoria').all()
    categoria_seleccionada = request.GET.get('categoria', 'todas')
    busqueda = request.GET.get('q', '')

    if categoria_seleccionada != 'todas':
        articulos = articulos.filter(categoria__nombre=categoria_seleccionada)

    if busqueda:
        articulos = articulos.filter(titulo__icontains=busqueda)

    categorias_disponibles = Categoria.objects.all()

    contexto = {
        'titulo_pagina': 'Artículos - Blog de Tecnología',
        'articulos': articulos,
        'categorias': categorias_disponibles,
        'categoria_actual': categoria_seleccionada,
        'busqueda': busqueda,
    }
    return render(request, 'blog/lista_articulos.html', contexto)


def detalle_articulo(request, articulo_id):
    """
    Vista de detalle de un artículo específico, buscado por su id
    (llave primaria) directamente en la base de datos.
    """
    articulo = Articulo.objects.select_related('categoria').filter(
        id=articulo_id
    ).first()

    contexto = {
        'titulo_pagina': 'Detalle del artículo',
        'articulo': articulo,
    }
    return render(request, 'blog/detalle_articulo.html', contexto)
