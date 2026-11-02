from cuentas.crud import mantenedor
from .forms import DestinoForm
from .models import Destino

destinos = mantenedor(
    Destino, DestinoForm,
    columnas=[('Destino', 'nombre'), ('País', 'pais'), ('Continente', 'continente.nombre'),
              ('Precio (CLP)', 'precio_clp'), ('Días', 'duracion_dias')],
    busqueda=['nombre', 'pais', 'continente__nombre'],
    singular='destino', plural='Destinos',
)
