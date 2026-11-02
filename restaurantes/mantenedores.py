from cuentas.crud import mantenedor
from .forms import RestauranteForm
from .models import Restaurante

restaurantes = mantenedor(
    Restaurante, RestauranteForm,
    columnas=[('Restaurante', 'nombre'), ('Cocina', 'tipo_cocina.nombre'), ('Ciudad', 'ciudad'),
              ('Precio', 'rango_precio'), ('Calificación', 'calificacion')],
    busqueda=['nombre', 'ciudad', 'tipo_cocina__nombre'],
    singular='restaurante', plural='Restaurantes',
)
