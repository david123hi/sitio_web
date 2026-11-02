"""
Comando: python manage.py crear_perfiles

Crea (o actualiza) los grupos Administrador, Supervisor y Administrativo
con los permisos definidos en cuentas/roles.py. Es seguro ejecutarlo
varias veces. Debe correrse después de `migrate` (los permisos de cada
modelo los crea Django durante la migración).
"""
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from cuentas.roles import PERMISOS_POR_PERFIL


class Command(BaseCommand):
    help = "Crea los grupos Administrador, Supervisor y Administrativo con sus permisos."

    def handle(self, *args, **options):
        for perfil, especificaciones in PERMISOS_POR_PERFIL.items():
            grupo, creado = Group.objects.get_or_create(name=perfil)
            permisos = []
            for app, modelo, acciones in especificaciones:
                for accion in acciones:
                    codigo = f'{accion}_{modelo}'
                    try:
                        permisos.append(Permission.objects.get(
                            content_type__app_label=app, codename=codigo))
                    except Permission.DoesNotExist:
                        self.stderr.write(self.style.WARNING(
                            f'  Permiso {app}.{codigo} no existe (¿falta migrate?)'))
            grupo.permissions.set(permisos)
            estado = 'creado' if creado else 'actualizado'
            self.stdout.write(self.style.SUCCESS(
                f'Grupo "{perfil}" {estado} con {len(permisos)} permisos.'))
