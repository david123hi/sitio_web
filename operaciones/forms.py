"""
operaciones/forms.py

Formularios de las transacciones. Cada formulario:
1. valida los datos ingresados,
2. permite elegir un viajero registrado O crear uno nuevo en el mismo paso,
3. guarda todo dentro de transaction.atomic(): si algo falla, no se crea
   ni el viajero ni la reserva (se guardan las dos entidades o ninguna).
"""
from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from blog.models import Categoria
from cursos.models import Curso
from destinos.models import Destino
from restaurantes.models import Restaurante
from travelers.models import Viajero

from .models import InscripcionCurso, ReservaDestino, ReservaMesa, SuscripcionBlog

# Maximo de personas que un restaurante recibe en un mismo horario.
AFORO_POR_HORARIO = 30

# Maximo de categorias del blog a las que puede suscribirse un viajero.
MAX_SUSCRIPCIONES_BLOG = 5


class OperacionBaseForm(forms.ModelForm):
    """Base: campos para elegir o crear al viajero + guardado atomico."""

    viajero_existente = forms.ModelChoiceField(
        queryset=Viajero.objects.all().order_by('nombre'),
        required=False,
        empty_label='— Seleccionar viajero registrado —',
        label='Viajero registrado',
    )
    nuevo_nombre = forms.CharField(
        max_length=100, required=False, label='Nombre del nuevo viajero'
    )
    nuevo_correo = forms.EmailField(
        required=False, label='Correo del nuevo viajero'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            clase = 'form-select' if isinstance(campo.widget, forms.Select) else 'form-control'
            campo.widget.attrs.setdefault('class', clase)

    def clean(self):
        datos = super().clean()
        existente = datos.get('viajero_existente')
        nombre = (datos.get('nuevo_nombre') or '').strip()
        correo = (datos.get('nuevo_correo') or '').strip().lower()

        if existente and (nombre or correo):
            raise ValidationError(
                'Selecciona un viajero registrado o ingresa uno nuevo, pero no ambos.'
            )
        if not existente:
            if not (nombre and correo):
                raise ValidationError(
                    'Selecciona un viajero registrado o ingresa el nombre y '
                    'el correo de uno nuevo.'
                )
            if Viajero.objects.filter(correo__iexact=correo).exists():
                self.add_error(
                    'nuevo_correo',
                    'Ya existe un viajero con ese correo. Selecciónalo en la lista.',
                )
        return datos

    def _obtener_viajero(self):
        existente = self.cleaned_data.get('viajero_existente')
        if existente:
            return existente
        return Viajero.objects.create(
            nombre=self.cleaned_data['nuevo_nombre'].strip(),
            correo=self.cleaned_data['nuevo_correo'].strip().lower(),
        )

    def validar_y_completar(self, objeto):
        """Validaciones finales bajo bloqueo. Las define cada formulario."""
        raise NotImplementedError

    def guardar(self):
        """Guarda viajero (si es nuevo) y operacion en una sola transaccion."""
        with transaction.atomic():
            viajero = self._obtener_viajero()
            objeto = self.save(commit=False)
            objeto.viajero = viajero
            self.validar_y_completar(objeto)
            objeto.save()
        return objeto


class ReservaDestinoForm(OperacionBaseForm):
    field_order = [
        'destino', 'fecha_viaje', 'cantidad_personas',
        'viajero_existente', 'nuevo_nombre', 'nuevo_correo',
    ]

    class Meta:
        model = ReservaDestino
        fields = ['destino', 'fecha_viaje', 'cantidad_personas']
        labels = {
            'destino': 'Destino',
            'fecha_viaje': 'Fecha del viaje',
            'cantidad_personas': 'Cantidad de personas',
        }
        widgets = {
            'fecha_viaje': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def clean_fecha_viaje(self):
        fecha = self.cleaned_data['fecha_viaje']
        if fecha < timezone.localdate():
            raise ValidationError('La fecha del viaje no puede estar en el pasado.')
        return fecha

    def validar_y_completar(self, objeto):
        # Se bloquea la fila del destino para que dos reservas simultaneas
        # no pasen la validacion de duplicados al mismo tiempo.
        destino = Destino.objects.select_for_update().get(pk=objeto.destino_id)
        duplicada = ReservaDestino.objects.filter(
            viajero=objeto.viajero, destino=destino,
            fecha_viaje=objeto.fecha_viaje, estado='confirmada',
        ).exists()
        if duplicada:
            raise ValidationError(
                'Este viajero ya tiene una reserva a ese destino en esa fecha.'
            )
        objeto.total_clp = destino.precio_clp * objeto.cantidad_personas
        objeto.estado = 'confirmada'


class ReservaMesaForm(OperacionBaseForm):
    field_order = [
        'restaurante', 'fecha', 'hora', 'personas',
        'viajero_existente', 'nuevo_nombre', 'nuevo_correo',
    ]

    class Meta:
        model = ReservaMesa
        fields = ['restaurante', 'fecha', 'hora', 'personas']
        labels = {
            'restaurante': 'Restaurante',
            'fecha': 'Fecha',
            'hora': 'Hora',
            'personas': 'Cantidad de personas',
        }
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'hora': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
        }

    def clean(self):
        datos = super().clean()
        fecha, hora = datos.get('fecha'), datos.get('hora')
        if fecha and hora:
            ahora = timezone.localtime()
            if fecha < ahora.date():
                self.add_error('fecha', 'La fecha no puede estar en el pasado.')
            elif fecha == ahora.date() and hora <= ahora.time():
                self.add_error('hora', 'Esa hora ya pasó. Elige una hora posterior.')
        return datos

    def validar_y_completar(self, objeto):
        restaurante = Restaurante.objects.select_for_update().get(pk=objeto.restaurante_id)
        del_horario = ReservaMesa.objects.filter(
            restaurante=restaurante, fecha=objeto.fecha,
            hora=objeto.hora, estado='confirmada',
        )
        if del_horario.filter(viajero=objeto.viajero).exists():
            raise ValidationError(
                'Este viajero ya tiene una reserva en ese restaurante a esa hora.'
            )
        ocupados = del_horario.aggregate(total=Sum('personas'))['total'] or 0
        libres = AFORO_POR_HORARIO - ocupados
        if objeto.personas > libres:
            raise ValidationError(
                f'No hay cupo suficiente para ese horario. '
                f'Quedan {max(libres, 0)} lugares disponibles.'
            )
        objeto.estado = 'confirmada'


class InscripcionCursoForm(OperacionBaseForm):
    field_order = [
        'curso', 'viajero_existente', 'nuevo_nombre', 'nuevo_correo',
    ]

    class Meta:
        model = InscripcionCurso
        fields = ['curso']
        labels = {'curso': 'Curso'}

    def validar_y_completar(self, objeto):
        curso = Curso.objects.select_for_update().get(pk=objeto.curso_id)
        ya_inscrito = InscripcionCurso.objects.filter(
            viajero=objeto.viajero, curso=curso, estado='activa'
        ).exists()
        if ya_inscrito:
            raise ValidationError('Este viajero ya está inscrito en ese curso.')
        objeto.monto_clp = curso.precio_clp
        objeto.estado = 'activa'


class SuscripcionBlogForm(OperacionBaseForm):
    field_order = [
        'categoria', 'viajero_existente', 'nuevo_nombre', 'nuevo_correo',
    ]

    class Meta:
        model = SuscripcionBlog
        fields = ['categoria']
        labels = {'categoria': 'Categoría del blog'}

    def validar_y_completar(self, objeto):
        # Se bloquea la fila del viajero: asi dos suscripciones simultaneas
        # no superan el maximo permitido.
        viajero = Viajero.objects.select_for_update().get(pk=objeto.viajero_id)
        activas = SuscripcionBlog.objects.filter(viajero=viajero, estado='activa')
        if activas.filter(categoria_id=objeto.categoria_id).exists():
            raise ValidationError('Este viajero ya está suscrito a esa categoría.')
        if activas.count() >= MAX_SUSCRIPCIONES_BLOG:
            raise ValidationError(
                f'Un viajero puede suscribirse como máximo a '
                f'{MAX_SUSCRIPCIONES_BLOG} categorías.'
            )
        objeto.estado = 'activa'
