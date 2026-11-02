from django import forms

from cuentas.crud import SlugAutomaticoMixin
from cuentas.forms import BootstrapModelForm
from .models import Destino


class DestinoForm(SlugAutomaticoMixin, BootstrapModelForm):
    class Meta:
        model = Destino
        fields = ['nombre', 'pais', 'continente', 'precio_clp', 'duracion_dias',
                  'descripcion', 'imagen']
        labels = {'nombre': 'Nombre', 'pais': 'País', 'continente': 'Continente',
                  'precio_clp': 'Precio referencial (CLP)', 'duracion_dias': 'Duración (días)',
                  'descripcion': 'Descripción', 'imagen': 'Imagen (ruta en static)'}
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 4})}

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre

    def clean_precio_clp(self):
        precio = self.cleaned_data['precio_clp']
        if precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor que cero.')
        return precio

    def clean_duracion_dias(self):
        dias = self.cleaned_data['duracion_dias']
        if dias < 1:
            raise forms.ValidationError('La duración debe ser de al menos 1 día.')
        return dias
