from django import forms

from cuentas.crud import SlugAutomaticoMixin
from cuentas.forms import BootstrapModelForm
from .models import Restaurante


class RestauranteForm(SlugAutomaticoMixin, BootstrapModelForm):
    class Meta:
        model = Restaurante
        fields = ['nombre', 'tipo_cocina', 'ciudad', 'direccion', 'rango_precio',
                  'calificacion', 'descripcion', 'imagen']
        labels = {'nombre': 'Nombre', 'tipo_cocina': 'Tipo de cocina', 'ciudad': 'Ciudad',
                  'direccion': 'Dirección', 'rango_precio': 'Rango de precio',
                  'calificacion': 'Calificación (0 a 5)', 'descripcion': 'Descripción',
                  'imagen': 'Imagen (ruta en static)'}
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'calificacion': forms.NumberInput(attrs={'step': '0.1', 'min': '0', 'max': '5'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre

    def clean_calificacion(self):
        nota = self.cleaned_data['calificacion']
        if nota < 0 or nota > 5:
            raise forms.ValidationError('La calificación debe estar entre 0 y 5.')
        return nota

    def clean(self):
        datos = super().clean()
        nombre, ciudad = datos.get('nombre'), (datos.get('ciudad') or '').strip()
        if nombre and ciudad:
            repetido = Restaurante.objects.filter(
                nombre__iexact=nombre, ciudad__iexact=ciudad
            ).exclude(pk=self.instance.pk)
            if repetido.exists():
                raise forms.ValidationError(
                    'Ya existe un restaurante con ese nombre en esa ciudad.')
        return datos
