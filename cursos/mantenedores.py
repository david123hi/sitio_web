from cuentas.crud import mantenedor
from .forms import CursoForm
from .models import Curso

cursos = mantenedor(
    Curso, CursoForm,
    columnas=[('Título', 'titulo'), ('Área', 'area.nombre'), ('Instructor', 'instructor'),
              ('Nivel', 'get_nivel_display'), ('Horas', 'duracion_horas'), ('Precio (CLP)', 'precio_clp')],
    busqueda=['titulo', 'instructor', 'area__nombre'],
    singular='curso', plural='Cursos',
)
