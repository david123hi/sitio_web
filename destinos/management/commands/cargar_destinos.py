"""
Comando de gestión: python manage.py cargar_destinos

Migra los datos que en la Evaluación Sumativa N°1 vivían en
data/destinos.json hacia la base de datos relacional, usando el
Django ORM (Continente y Destino). Es seguro ejecutarlo varias veces:
usa get_or_create/update_or_create para no duplicar registros.
"""
import json

from django.conf import settings
from django.core.management.base import BaseCommand

from destinos.models import Destino, Continente


class Command(BaseCommand):
    help = "Migra data/destinos.json hacia la base de datos (Continente y Destino)."

    def handle(self, *args, **options):
        ruta_json = settings.BASE_DIR / 'data' / 'destinos.json'

        if not ruta_json.exists():
            self.stderr.write(self.style.ERROR(f"No se encontró {ruta_json}"))
            return

        with open(ruta_json, 'r', encoding='utf-8') as archivo:
            destinos_json = json.load(archivo)

        creados = 0
        actualizados = 0

        for item in destinos_json:
            continente, _ = Continente.objects.get_or_create(nombre=item['continente'])

            _, fue_creado = Destino.objects.update_or_create(
                slug=item['slug'],
                defaults={
                    'nombre': item['nombre'],
                    'pais': item['pais'],
                    'continente': continente,
                    'precio_clp': item['precio_clp'],
                    'duracion_dias': item['duracion_dias'],
                    'descripcion': item['descripcion'],
                    'imagen': item.get('imagen', ''),
                }
            )
            creados += 1 if fue_creado else 0
            actualizados += 0 if fue_creado else 1

        self.stdout.write(self.style.SUCCESS(
            f"Migración completada: {creados} destino(s) creado(s), "
            f"{actualizados} actualizado(s). "
            f"Continentes en BD: {Continente.objects.count()}."
        ))
