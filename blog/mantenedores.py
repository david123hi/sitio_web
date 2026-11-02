from cuentas.crud import mantenedor
from .forms import ArticuloForm
from .models import Articulo

articulos = mantenedor(
    Articulo, ArticuloForm,
    columnas=[('Título', 'titulo'), ('Categoría', 'categoria.nombre'),
              ('Autor', 'autor'), ('Fecha', 'fecha')],
    busqueda=['titulo', 'autor', 'resumen'],
    singular='artículo', plural='Artículos',
)
