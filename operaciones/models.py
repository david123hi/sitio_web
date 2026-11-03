"""
operaciones/models.py

Transacciones operacionales del sitio. Cada una relaciona a un Viajero
con una entidad de un catalogo (Destino, Restaurante o Curso):

- ReservaDestino   -> Viajero + Destino
- ReservaMesa      -> Viajero + Restaurante
- InscripcionCurso -> Viajero + Curso
- SuscripcionBlog  -> Viajero + Categoria del blog
"""
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

ESTADOS_RESERVA = [
    ('confirmada', 'Confirmada'),
    ('cancelada', 'Cancelada'),
]

ESTADOS_INSCRIPCION = [
    ('activa', 'Activa'),
    ('cancelada', 'Cancelada'),
]


class ReservaDestino(models.Model):
    """Reserva de un viaje a un destino del catalogo."""
    viajero = models.ForeignKey(
        'travelers.Viajero', on_delete=models.PROTECT,
        related_name='reservas_destino',
    )
    destino = models.ForeignKey(
        'destinos.Destino', on_delete=models.PROTECT,
        related_name='reservas',
    )
    fecha_viaje = models.DateField()
    cantidad_personas = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    # Se calcula al guardar: precio del destino x cantidad de personas.
    total_clp = models.PositiveIntegerField()
    estado = models.CharField(
        max_length=12, choices=ESTADOS_RESERVA, default='confirmada'
    )
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reserva de destino'
        verbose_name_plural = 'Reservas de destino'
        ordering = ['-creada']

    def __str__(self):
        return f'{self.viajero} - {self.destino} ({self.fecha_viaje})'


class ReservaMesa(models.Model):
    """Reserva de mesa en un restaurante de la guia."""
    viajero = models.ForeignKey(
        'travelers.Viajero', on_delete=models.PROTECT,
        related_name='reservas_mesa',
    )
    restaurante = models.ForeignKey(
        'restaurantes.Restaurante', on_delete=models.PROTECT,
        related_name='reservas',
    )
    fecha = models.DateField()
    hora = models.TimeField()
    personas = models.PositiveSmallIntegerField(
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
    )
    estado = models.CharField(
        max_length=12, choices=ESTADOS_RESERVA, default='confirmada'
    )
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reserva de mesa'
        verbose_name_plural = 'Reservas de mesa'
        ordering = ['-creada']

    def __str__(self):
        return f'{self.viajero} - {self.restaurante} ({self.fecha} {self.hora:%H:%M})'


class InscripcionCurso(models.Model):
    """Inscripcion de un viajero a un curso online."""
    viajero = models.ForeignKey(
        'travelers.Viajero', on_delete=models.PROTECT,
        related_name='inscripciones_curso',
    )
    curso = models.ForeignKey(
        'cursos.Curso', on_delete=models.PROTECT,
        related_name='inscripciones',
    )
    # Se copia el precio del curso al momento de inscribirse (0 = gratuito).
    monto_clp = models.PositiveIntegerField(default=0)
    estado = models.CharField(
        max_length=12, choices=ESTADOS_INSCRIPCION, default='activa'
    )
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Inscripcion a curso'
        verbose_name_plural = 'Inscripciones a cursos'
        ordering = ['-creada']

    def __str__(self):
        return f'{self.viajero} - {self.curso}'


class SuscripcionBlog(models.Model):
    """Suscripcion de un viajero a una categoria del blog."""
    viajero = models.ForeignKey(
        'travelers.Viajero', on_delete=models.PROTECT,
        related_name='suscripciones_blog',
    )
    categoria = models.ForeignKey(
        'blog.Categoria', on_delete=models.PROTECT,
        related_name='suscripciones',
    )
    estado = models.CharField(
        max_length=12, choices=ESTADOS_INSCRIPCION, default='activa'
    )
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Suscripcion al blog'
        verbose_name_plural = 'Suscripciones al blog'
        ordering = ['-creada']

    def __str__(self):
        return f'{self.viajero} - {self.categoria}'
