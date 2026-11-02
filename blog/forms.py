from django import forms

from cuentas.forms import BootstrapModelForm
from .models import Articulo


class ArticuloForm(BootstrapModelForm):
    class Meta:
        model = Articulo
        fields = ['titulo', 'categoria', 'autor', 'fecha', 'resumen', 'contenido', 'imagen']
        labels = {'titulo': 'Título', 'categoria': 'Categoría', 'autor': 'Autor',
                  'fecha': 'Fecha de publicación', 'resumen': 'Resumen',
                  'contenido': 'Contenido', 'imagen': 'Imagen (ruta en static)'}
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'contenido': forms.Textarea(attrs={'rows': 6}),
            'resumen': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_titulo(self):
        titulo = self.cleaned_data['titulo'].strip()
        if len(titulo) < 5:
            raise forms.ValidationError('El título debe tener al menos 5 caracteres.')
        return titulo

    def clean_contenido(self):
        contenido = self.cleaned_data['contenido'].strip()
        if len(contenido) < 20:
            raise forms.ValidationError('El contenido debe tener al menos 20 caracteres.')
        return contenido
