"""
operaciones/views.py

Vistas de las transacciones. Todas exigen sesion iniciada y el permiso
correspondiente del sistema de Django (403 si el perfil no lo tiene).
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView

from .forms import (
    InscripcionCursoForm, ReservaDestinoForm, ReservaMesaForm, SuscripcionBlogForm,
)
from .models import InscripcionCurso, ReservaDestino, ReservaMesa, SuscripcionBlog


def clp(valor):
    """Formatea pesos chilenos: 1250000 -> $1.250.000"""
    return '$' + f'{valor:,}'.replace(',', '.')


# --------------------------------------------------------------------------
# Crear (transaccion)
# --------------------------------------------------------------------------
class CrearOperacionView(LoginRequiredMixin, PermissionRequiredMixin, View):
    form_class = None
    titulo = ''
    descripcion = ''
    mensaje_exito = ''
    url_lista = ''
    template_name = 'operaciones/formulario.html'

    def _mostrar(self, request, form):
        return render(request, self.template_name, {
            'form': form,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'url_lista': self.url_lista,
        })

    def get(self, request):
        return self._mostrar(request, self.form_class())

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            try:
                form.guardar()
            except ValidationError as error:
                form.add_error(None, error)
            else:
                messages.success(request, self.mensaje_exito)
                return redirect(self.url_lista)
        return self._mostrar(request, form)


class CrearReservaDestinoView(CrearOperacionView):
    permission_required = 'operaciones.add_reservadestino'
    form_class = ReservaDestinoForm
    titulo = 'Reservar destino'
    descripcion = 'Registra la reserva de un viaje. El total se calcula con el precio del destino.'
    mensaje_exito = 'Reserva de destino registrada correctamente.'
    url_lista = 'operaciones:destino_lista'


class CrearReservaMesaView(CrearOperacionView):
    permission_required = 'operaciones.add_reservamesa'
    form_class = ReservaMesaForm
    titulo = 'Reservar mesa'
    descripcion = 'Registra una reserva de mesa. Se valida el cupo disponible del horario.'
    mensaje_exito = 'Reserva de mesa registrada correctamente.'
    url_lista = 'operaciones:mesa_lista'


class CrearInscripcionCursoView(CrearOperacionView):
    permission_required = 'operaciones.add_inscripcioncurso'
    form_class = InscripcionCursoForm
    titulo = 'Inscribir en un curso'
    descripcion = 'Inscribe a un viajero en un curso. No se permite inscribirlo dos veces.'
    mensaje_exito = 'Inscripción registrada correctamente.'
    url_lista = 'operaciones:curso_lista'


class CrearSuscripcionBlogView(CrearOperacionView):
    permission_required = 'operaciones.add_suscripcionblog'
    form_class = SuscripcionBlogForm
    titulo = 'Suscribir a una categoría del blog'
    descripcion = 'Suscribe a un viajero a una categoría. Máximo 5 categorías por viajero.'
    mensaje_exito = 'Suscripción registrada correctamente.'
    url_lista = 'operaciones:blog_lista'


# --------------------------------------------------------------------------
# Listar y buscar
# --------------------------------------------------------------------------
class ListaOperacionView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    template_name = 'operaciones/lista.html'
    paginate_by = 10
    titulo = ''
    columnas = []
    relaciones = []
    campos_busqueda = []
    url_nueva = ''
    permiso_crear = ''

    def get_queryset(self):
        consulta = super().get_queryset().select_related(*self.relaciones)
        q = self.request.GET.get('q', '').strip()
        if q:
            condicion = Q()
            for campo in self.campos_busqueda:
                condicion |= Q(**{f'{campo}__icontains': q})
            consulta = consulta.filter(condicion)
        return consulta

    def fila(self, obj):
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'titulo': self.titulo,
            'columnas': self.columnas,
            'filas': [self.fila(obj) for obj in ctx['object_list']],
            'q': self.request.GET.get('q', '').strip(),
            'url_nueva': self.url_nueva,
            'puede_crear': self.request.user.has_perm(self.permiso_crear),
        })
        return ctx


class ListaReservasDestinoView(ListaOperacionView):
    permission_required = 'operaciones.view_reservadestino'
    permiso_crear = 'operaciones.add_reservadestino'
    model = ReservaDestino
    titulo = 'Reservas de destinos'
    columnas = ['Registrada', 'Viajero', 'Destino', 'Fecha del viaje', 'Personas', 'Total', 'Estado']
    relaciones = ['viajero', 'destino']
    campos_busqueda = ['viajero__nombre', 'viajero__correo', 'destino__nombre', 'destino__pais']
    url_nueva = 'operaciones:destino_nueva'

    def fila(self, o):
        return [
            o.creada.strftime('%d-%m-%Y'), str(o.viajero), str(o.destino),
            o.fecha_viaje.strftime('%d-%m-%Y'), o.cantidad_personas,
            clp(o.total_clp), o.get_estado_display(),
        ]


class ListaReservasMesaView(ListaOperacionView):
    permission_required = 'operaciones.view_reservamesa'
    permiso_crear = 'operaciones.add_reservamesa'
    model = ReservaMesa
    titulo = 'Reservas de mesa'
    columnas = ['Registrada', 'Viajero', 'Restaurante', 'Fecha', 'Hora', 'Personas', 'Estado']
    relaciones = ['viajero', 'restaurante']
    campos_busqueda = ['viajero__nombre', 'viajero__correo', 'restaurante__nombre', 'restaurante__ciudad']
    url_nueva = 'operaciones:mesa_nueva'

    def fila(self, o):
        return [
            o.creada.strftime('%d-%m-%Y'), str(o.viajero), str(o.restaurante),
            o.fecha.strftime('%d-%m-%Y'), o.hora.strftime('%H:%M'),
            o.personas, o.get_estado_display(),
        ]


class ListaInscripcionesCursoView(ListaOperacionView):
    permission_required = 'operaciones.view_inscripcioncurso'
    permiso_crear = 'operaciones.add_inscripcioncurso'
    model = InscripcionCurso
    titulo = 'Inscripciones a cursos'
    columnas = ['Registrada', 'Viajero', 'Curso', 'Monto', 'Estado']
    relaciones = ['viajero', 'curso']
    campos_busqueda = ['viajero__nombre', 'viajero__correo', 'curso__titulo', 'curso__instructor']
    url_nueva = 'operaciones:curso_nueva'

    def fila(self, o):
        monto = 'Gratis' if o.monto_clp == 0 else clp(o.monto_clp)
        return [
            o.creada.strftime('%d-%m-%Y'), str(o.viajero), str(o.curso),
            monto, o.get_estado_display(),
        ]


class ListaSuscripcionesBlogView(ListaOperacionView):
    permission_required = 'operaciones.view_suscripcionblog'
    permiso_crear = 'operaciones.add_suscripcionblog'
    model = SuscripcionBlog
    titulo = 'Suscripciones al blog'
    columnas = ['Registrada', 'Viajero', 'Categoría', 'Estado']
    relaciones = ['viajero', 'categoria']
    campos_busqueda = ['viajero__nombre', 'viajero__correo', 'categoria__nombre']
    url_nueva = 'operaciones:blog_nueva'

    def fila(self, o):
        return [
            o.creada.strftime('%d-%m-%Y'), str(o.viajero), str(o.categoria),
            o.get_estado_display(),
        ]
