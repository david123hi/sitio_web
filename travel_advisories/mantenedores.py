from cuentas.crud import mantenedor
from .forms import VacunaForm
from .models import Vacuna

vacunas = mantenedor(
    Vacuna, VacunaForm,
    columnas=[('Vacuna', 'nombre'), ('Descripción', 'descripcion')],
    busqueda=['nombre', 'descripcion'],
    singular='vacuna', plural='Vacunas',
)
