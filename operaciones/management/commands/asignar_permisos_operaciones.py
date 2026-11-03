"""
Asigna a los grupos Administrador, Supervisor y Administrativo los
permisos de las transacciones de la app 'operaciones'.

Uso: python manage.py asignar_permisos_operaciones
"""
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

MODELOS = ['reservadestino', 'reservamesa', 'inscripcioncurso', 'suscripcionblog']

ACCIONES_POR_GRUPO = {
    'Administrador': ['view', 'add', 'change', 'delete'],
    'Supervisor': ['view', 'add', 'change'],
    'Administrativo': ['view', 'add'],
}


class Command(BaseCommand):
    help = 'Asigna los permisos de las transacciones a los grupos de perfiles.'

    def handle(self, *args, **options):
        for nombre, acciones in ACCIONES_POR_GRUPO.items():
            try:
                grupo = Group.objects.get(name=nombre)
            except Group.DoesNotExist:
                self.stderr.write(self.style.WARNING(f'No existe el grupo "{nombre}", se omite.'))
                continue
            for modelo in MODELOS:
                for accion in acciones:
                    permiso = Permission.objects.get(
                        content_type__app_label='operaciones',
                        codename=f'{accion}_{modelo}',
                    )
                    grupo.permissions.add(permiso)
            self.stdout.write(self.style.SUCCESS(f'Permisos asignados a {nombre}: {", ".join(acciones)}'))
