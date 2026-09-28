"""
Comando de gestión: python manage.py cargar_cursos

Carga los datos de ejemplo de data/cursos.json en la base de datos
usando el ORM (Area y Curso). Es seguro ejecutarlo varias veces: usa
get_or_create/update_or_create para no duplicar registros.
"""
import json

from django.conf import settings
from django.core.management.base import BaseCommand

from cursos.models import Area, Curso


class Command(BaseCommand):
    help = "Carga data/cursos.json en la base de datos (Area y Curso)."

    def handle(self, *args, **options):
        ruta_json = settings.BASE_DIR / 'data' / 'cursos.json'

        if not ruta_json.exists():
            self.stderr.write(self.style.ERROR(f"No se encontró {ruta_json}"))
            return

        with open(ruta_json, 'r', encoding='utf-8') as archivo:
            cursos_json = json.load(archivo)

        creados = 0
        actualizados = 0

        for item in cursos_json:
            area, _ = Area.objects.get_or_create(nombre=item['area'])

            _, fue_creado = Curso.objects.update_or_create(
                titulo=item['titulo'],
                defaults={
                    'area': area,
                    'instructor': item['instructor'],
                    'nivel': item['nivel'],
                    'duracion_horas': item['duracion_horas'],
                    'precio_clp': item['precio_clp'],
                    'descripcion': item['descripcion'],
                    'imagen': item.get('imagen', ''),
                }
            )
            creados += 1 if fue_creado else 0
            actualizados += 0 if fue_creado else 1

        self.stdout.write(self.style.SUCCESS(
            f"Carga completada: {creados} curso(s) creado(s), "
            f"{actualizados} actualizado(s). "
            f"Áreas en BD: {Area.objects.count()}."
        ))
