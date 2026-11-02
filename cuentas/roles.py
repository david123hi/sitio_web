"""
cuentas/roles.py

Define los tres perfiles del sistema (grupos de Django) y los permisos
que tiene cada uno. Es la ÚNICA fuente de verdad: el comando
`python manage.py crear_perfiles` lee este archivo y deja los grupos
creados en la base de datos (local o EC2).

Perfiles (Evaluación Sumativa N°3):
- Administrador : acceso total, incluida la gestión de usuarios.
- Supervisor    : ver, agregar y modificar; NO elimina ni gestiona usuarios.
- Administrativo: permisos mínimos (ver todo, registrar viajeros y
                  participaciones); sin modificar ni eliminar.
"""

ADMINISTRADOR = 'Administrador'
SUPERVISOR = 'Supervisor'
ADMINISTRATIVO = 'Administrativo'

PERFILES = (ADMINISTRADOR, SUPERVISOR, ADMINISTRATIVO)

# (app, modelo) de todas las entidades de negocio del sitio
MODELOS_NEGOCIO = [
    ('blog', 'categoria'), ('blog', 'articulo'),
    ('destinos', 'continente'), ('destinos', 'destino'),
    ('cursos', 'area'), ('cursos', 'curso'),
    ('restaurantes', 'tipococina'), ('restaurantes', 'restaurante'),
    ('travelers', 'viaje'), ('travelers', 'viajero'), ('travelers', 'participacion'),
    ('travel_advisories', 'alerta'), ('travel_advisories', 'vacuna'),
    ('travel_advisories', 'requisitovacuna'),
]

TODAS = ('view', 'add', 'change', 'delete')


def _permisos_administrador():
    permisos = [(app, modelo, TODAS) for app, modelo in MODELOS_NEGOCIO]
    # Gestión de usuarios y grupos (modelos de django.contrib.auth)
    permisos.append(('auth', 'user', TODAS))
    permisos.append(('auth', 'group', ('view',)))
    return permisos


def _permisos_supervisor():
    # Ver, agregar y modificar todo; sin eliminar y sin gestionar usuarios.
    return [(app, modelo, ('view', 'add', 'change')) for app, modelo in MODELOS_NEGOCIO]


def _permisos_administrativo():
    # Solo consulta, más el registro de viajeros y de participaciones.
    permisos = [(app, modelo, ('view',)) for app, modelo in MODELOS_NEGOCIO]
    reforzados = {('travelers', 'viajero'), ('travelers', 'participacion')}
    return [
        (app, modelo, ('view', 'add') if (app, modelo) in reforzados else acciones)
        for app, modelo, acciones in permisos
    ]


PERMISOS_POR_PERFIL = {
    ADMINISTRADOR: _permisos_administrador(),
    SUPERVISOR: _permisos_supervisor(),
    ADMINISTRATIVO: _permisos_administrativo(),
}


def rol_de(user):
    """Devuelve el perfil principal del usuario (o None si no tiene)."""
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return ADMINISTRADOR
    nombres = set(user.groups.values_list('name', flat=True))
    for perfil in PERFILES:
        if perfil in nombres:
            return perfil
    return None
