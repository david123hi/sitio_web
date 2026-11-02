from .roles import rol_de


def perfil(request):
    """Expone `rol_usuario` en todas las plantillas (para el menú y el dashboard)."""
    return {'rol_usuario': rol_de(request.user)}
