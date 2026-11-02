"""
cuentas/crud.py

Fábrica de mantenedores (CRUD) reutilizable. A partir de un modelo y su
formulario genera las 4 vistas (listar/buscar, crear, modificar, eliminar)
protegidas por LOGIN y PERMISOS de Django, más sus rutas. Así todas las
apps comparten el mismo comportamiento y las mismas plantillas
(templates/crud/*.html), sin usar Django Admin.

Uso (en <app>/urls.py):
    from .mantenedores import articulos
    urlpatterns += articulos.urls('gestion/articulos/')
"""
from types import SimpleNamespace

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import router
from django.db.models import ProtectedError, Q
from django.db.models.deletion import Collector
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.text import slugify
from django.views.generic import CreateView, DeleteView, ListView, UpdateView


def slug_unico(modelo, texto, pk=None):
    """Genera un slug único para el modelo a partir de un texto."""
    base = slugify(texto) or 'item'
    candidato, n = base, 1
    while modelo.objects.filter(slug=candidato).exclude(pk=pk).exists():
        n += 1
        candidato = f'{base}-{n}'
    return candidato


class SlugAutomaticoMixin:
    """Para ModelForms de modelos con `slug`: lo genera desde `nombre` si está vacío."""

    def save(self, commit=True):
        objeto = super().save(commit=False)
        if not objeto.slug:
            objeto.slug = slug_unico(type(objeto), objeto.nombre, objeto.pk)
        if commit:
            objeto.save()
        return objeto


def _resolver(objeto, ruta):
    """Obtiene un valor siguiendo una ruta con puntos (p. ej. 'categoria.nombre')."""
    valor = objeto
    for parte in ruta.split('.'):
        valor = getattr(valor, parte, None)
        if valor is None:
            return None
        if callable(valor):
            valor = valor()
    return valor


def _dependientes(objeto):
    """Cuenta los registros que se borrarían en cascada; indica si hay protegidos."""
    recolector = Collector(using=router.db_for_write(type(objeto)))
    try:
        recolector.collect([objeto])
    except ProtectedError:
        return {}, True
    cuentas = {
        modelo._meta.verbose_name_plural: len(instancias)
        for modelo, instancias in recolector.data.items()
        if modelo is not type(objeto) and instancias
    }
    # Los modelos "hoja" se borran por la vía rápida (fast_deletes): también se cuentan.
    for consulta in recolector.fast_deletes:
        modelo_hoja = getattr(consulta, 'model', None)
        if modelo_hoja is None:
            continue
        total = consulta.count()
        if total:
            nombre = modelo_hoja._meta.verbose_name_plural
            cuentas[nombre] = cuentas.get(nombre, 0) + total
    return cuentas, False


def mantenedor(modelo, formulario, columnas, busqueda, singular, plural, por_pagina=10):
    """
    modelo     : clase del modelo
    formulario : ModelForm usado para crear y modificar
    columnas   : lista de (encabezado, 'atributo.o.ruta') mostradas en el listado
    busqueda   : campos (icontains) sobre los que busca el parámetro ?q=
    """
    app = modelo._meta.app_label
    nombre = modelo._meta.model_name

    def perm(accion):
        return f'{app}.{accion}_{nombre}'

    def url(accion, *args):
        return reverse(f'{app}:{nombre}_{accion}', args=args)

    class Lista(PermissionRequiredMixin, ListView):
        model = modelo
        permission_required = perm('view')
        template_name = 'crud/lista.html'
        paginate_by = por_pagina

        def get_queryset(self):
            qs = super().get_queryset()
            q = self.request.GET.get('q', '').strip()
            if q and busqueda:
                condicion = Q()
                for campo in busqueda:
                    condicion |= Q(**{f'{campo}__icontains': q})
                qs = qs.filter(condicion)
            return qs

        def get_context_data(self, **kwargs):
            ctx = super().get_context_data(**kwargs)
            user = self.request.user
            ctx.update({
                'titulo': plural,
                'singular': singular,
                'encabezados': [c[0] for c in columnas],
                'filas': [{
                    'celdas': [_resolver(o, c[1]) for c in columnas],
                    'url_editar': url('editar', o.pk),
                    'url_eliminar': url('eliminar', o.pk),
                } for o in ctx['object_list']],
                'total_columnas': len(columnas) + 1,
                'q': self.request.GET.get('q', '').strip(),
                'url_lista': url('lista'),
                'url_crear': url('crear'),
                'puede_crear': user.has_perm(perm('add')),
                'puede_editar': user.has_perm(perm('change')),
                'puede_eliminar': user.has_perm(perm('delete')),
            })
            return ctx

    class Crear(PermissionRequiredMixin, CreateView):
        model = modelo
        form_class = formulario
        permission_required = perm('add')
        template_name = 'crud/form.html'

        def get_success_url(self):
            return url('lista')

        def form_valid(self, form):
            respuesta = super().form_valid(form)
            messages.success(self.request, f'{singular.capitalize()} "{self.object}" creado correctamente.')
            return respuesta

        def get_context_data(self, **kwargs):
            ctx = super().get_context_data(**kwargs)
            ctx.update({'titulo': f'Agregar {singular}', 'url_cancelar': url('lista')})
            return ctx

    class Actualizar(PermissionRequiredMixin, UpdateView):
        model = modelo
        form_class = formulario
        permission_required = perm('change')
        template_name = 'crud/form.html'

        def get_success_url(self):
            return url('lista')

        def form_valid(self, form):
            respuesta = super().form_valid(form)
            messages.success(self.request, f'{singular.capitalize()} "{self.object}" modificado correctamente.')
            return respuesta

        def get_context_data(self, **kwargs):
            ctx = super().get_context_data(**kwargs)
            ctx.update({'titulo': f'Modificar {singular}', 'url_cancelar': url('lista')})
            return ctx

    class Eliminar(PermissionRequiredMixin, DeleteView):
        model = modelo
        permission_required = perm('delete')
        template_name = 'crud/confirmar_eliminar.html'

        def get_context_data(self, **kwargs):
            ctx = super().get_context_data(**kwargs)
            dependientes, protegido = _dependientes(self.object)
            ctx.update({
                'titulo': f'Eliminar {singular}',
                'singular': singular,
                'url_cancelar': url('lista'),
                'dependientes': dependientes,
                'protegido': protegido,
            })
            return ctx

        def form_valid(self, form):
            etiqueta = str(self.object)
            try:
                self.object.delete()
            except ProtectedError:
                messages.error(self.request, f'No se puede eliminar "{etiqueta}": tiene registros asociados.')
            else:
                messages.success(self.request, f'{singular.capitalize()} "{etiqueta}" eliminado correctamente.')
            return redirect(url('lista'))

    def urls(prefijo):
        return [
            path(prefijo, Lista.as_view(), name=f'{nombre}_lista'),
            path(f'{prefijo}nuevo/', Crear.as_view(), name=f'{nombre}_crear'),
            path(f'{prefijo}<int:pk>/editar/', Actualizar.as_view(), name=f'{nombre}_editar'),
            path(f'{prefijo}<int:pk>/eliminar/', Eliminar.as_view(), name=f'{nombre}_eliminar'),
        ]

    return SimpleNamespace(urls=urls, url=url)
