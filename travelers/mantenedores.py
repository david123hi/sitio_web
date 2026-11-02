from cuentas.crud import mantenedor
from .forms import ViajeroForm
from .models import Viajero

viajeros = mantenedor(
    Viajero, ViajeroForm,
    columnas=[('Nombre', 'nombre'), ('Correo', 'correo')],
    busqueda=['nombre', 'correo'],
    singular='viajero', plural='Viajeros',
)
