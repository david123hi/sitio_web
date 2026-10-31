from django import forms
from .models import Viaje


class ViajeForm(forms.ModelForm):
    class Meta:
        model = Viaje
        fields = ['actividad', 'destino', 'inicio', 'fin', 'cupos', 'estado']
        labels = {
            'actividad': 'Actividad',
            'destino': 'Destino',
            'inicio': 'Fecha de inicio',
            'fin': 'Fecha de término',
            'cupos': 'Cupos totales',
            'estado': 'Estado',
        }
        widgets = {
            'actividad': forms.TextInput(attrs={'class': 'form-control'}),
            'destino': forms.Select(attrs={'class': 'form-select'}),
            'inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'cupos': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_actividad(self):
        actividad = self.cleaned_data['actividad'].strip()
        if len(actividad) < 3:
            raise forms.ValidationError('La actividad debe tener al menos 3 caracteres.')
        return actividad

    def clean_cupos(self):
        cupos = self.cleaned_data['cupos']
        if cupos < 1:
            raise forms.ValidationError('El viaje debe tener al menos 1 cupo.')
        if self.instance.pk:
            confirmados = self.instance.participaciones.filter(estado='C').count()
            if cupos < confirmados:
                raise forms.ValidationError(
                    f'Ya hay {confirmados} participantes confirmados; los cupos no pueden ser menos.'
                )
        return cupos

    def clean(self):
        cleaned = super().clean()
        inicio, fin = cleaned.get('inicio'), cleaned.get('fin')
        if inicio and fin and fin < inicio:
            self.add_error('fin', 'La fecha de término no puede ser anterior a la de inicio.')
        return cleaned
