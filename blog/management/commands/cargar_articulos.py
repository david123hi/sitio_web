"""
Comando de gestión: python manage.py cargar_articulos

Migra los datos que en la Evaluación Sumativa N°1 vivían en
data/articulos.json hacia la base de datos relacional, usando el
Django ORM (Categoria y Articulo). Es seguro ejecutarlo varias veces:
usa get_or_create/update_or_create para no duplicar registros.
"""
import json

from django.conf import settings
from django.core.management.base import BaseCommand

from blog.models import Articulo, Categoria


class Command(BaseCommand):
    help = "Migra data/articulos.json hacia la base de datos (Categoria y Articulo)."

    def handle(self, *args, **options):
        ruta_json = settings.BASE_DIR / 'data' / 'articulos.json'

        if not ruta_json.exists():
            self.stderr.write(self.style.ERROR(f"No se encontró {ruta_json}"))
            return

        with open(ruta_json, 'r', encoding='utf-8') as archivo:
            articulos_json = json.load(archivo)

        creados = 0
        actualizados = 0

        for item in articulos_json:
            categoria, _ = Categoria.objects.get_or_create(nombre=item['categoria'])

            _, fue_creado = Articulo.objects.update_or_create(
                titulo=item['titulo'],
                defaults={
                    'categoria': categoria,
                    'autor': item['autor'],
                    'fecha': item['fecha'],
                    'resumen': item['resumen'],
                    'contenido': item['contenido'],
                    'imagen': item.get('imagen', ''),
                }
            )
            creados += 1 if fue_creado else 0
            actualizados += 0 if fue_creado else 1

        self.stdout.write(self.style.SUCCESS(
            f"Migración completada: {creados} artículo(s) creado(s), "
            f"{actualizados} actualizado(s). "
            f"Categorías en BD: {Categoria.objects.count()}."
        ))
