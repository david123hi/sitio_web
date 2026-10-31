from django import forms
from .models import Alerta


class AlertaForm(forms.ModelForm):
    """Formulario del mantenedor de Alertas de viaje (crear y modificar)."""

    class Meta:
        model = Alerta
        fields = ['titulo', 'pais', 'nivel', 'emision', 'expiracion', 'descripcion', 'activo']
        labels = {
            'titulo': 'Título',
            'pais': 'Destino',
            'nivel': 'Nivel de alerta',
            'emision': 'Fecha de emisión',
            'expiracion': 'Fecha de expiración',
            'descripcion': 'Descripción',
            'activo': 'Alerta activa',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.Select(attrs={'class': 'form-select'}),
            'nivel': forms.Select(attrs={'class': 'form-select'}),
            'emision': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'expiracion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_titulo(self):
        titulo = self.cleaned_data['titulo'].strip()
        if len(titulo) < 3:
            raise forms.ValidationError('El título debe tener al menos 3 caracteres.')
        return titulo

    def clean(self):
        cleaned = super().clean()
        emision, expiracion = cleaned.get('emision'), cleaned.get('expiracion')
        if emision and expiracion and expiracion < emision:
            self.add_error('expiracion', 'La fecha de expiración no puede ser anterior a la de emisión.')
        return cleaned
