"""
Comando de gestión: python manage.py cargar_restaurantes

Carga los datos de ejemplo de data/restaurantes.json en la base de
datos usando el ORM (TipoCocina y Restaurante). Es seguro ejecutarlo
varias veces: usa get_or_create/update_or_create para no duplicar.
"""
import json
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand

from restaurantes.models import Restaurante, TipoCocina


class Command(BaseCommand):
    help = "Carga data/restaurantes.json en la base de datos (TipoCocina y Restaurante)."

    def handle(self, *args, **options):
        ruta_json = settings.BASE_DIR / 'data' / 'restaurantes.json'

        if not ruta_json.exists():
            self.stderr.write(self.style.ERROR(f"No se encontró {ruta_json}"))
            return

        with open(ruta_json, 'r', encoding='utf-8') as archivo:
            restaurantes_json = json.load(archivo)

        creados = 0
        actualizados = 0

        for item in restaurantes_json:
            tipo, _ = TipoCocina.objects.get_or_create(nombre=item['tipo_cocina'])

            _, fue_creado = Restaurante.objects.update_or_create(
                slug=item['slug'],
                defaults={
                    'nombre': item['nombre'],
                    'tipo_cocina': tipo,
                    'ciudad': item['ciudad'],
                    'direccion': item['direccion'],
                    'rango_precio': item['rango_precio'],
                    'calificacion': Decimal(item['calificacion']),
                    'descripcion': item['descripcion'],
                    'imagen': item.get('imagen', ''),
                }
            )
            creados += 1 if fue_creado else 0
            actualizados += 0 if fue_creado else 1

        self.stdout.write(self.style.SUCCESS(
            f"Carga completada: {creados} restaurante(s) creado(s), "
            f"{actualizados} actualizado(s). "
            f"Tipos de cocina en BD: {TipoCocina.objects.count()}."
        ))
