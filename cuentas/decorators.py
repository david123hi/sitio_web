from django.contrib.auth.decorators import login_required, permission_required


def requiere_permiso(*permisos):
    """
    Protege una vista: exige sesión iniciada (si no, redirige al login) y
    que el usuario tenga TODOS los permisos indicados (si no, responde 403).
    """
    def decorador(vista):
        return login_required(permission_required(permisos, raise_exception=True)(vista))
    return decorador
