from django import forms

from cuentas.forms import BootstrapModelForm, aplicar_bootstrap
from .models import Participacion, Viaje, Viajero


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


class ViajeConOrganizadorForm(ViajeForm):
    """
    TRANSACCIÓN "Programar viaje": crea el Viaje y registra en el mismo paso
    al organizador (Participacion con rol Organizador, confirmado).
    """
    organizador = forms.ModelChoiceField(
        queryset=Viajero.objects.all(), label='Organizador del viaje',
        empty_label='Seleccione un viajero...',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


class ViajeroForm(BootstrapModelForm):
    class Meta:
        model = Viajero
        fields = ['nombre', 'correo']
        labels = {'nombre': 'Nombre completo', 'correo': 'Correo electrónico'}

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre

    def clean_correo(self):
        correo = self.cleaned_data['correo'].strip().lower()
        if Viajero.objects.filter(correo__iexact=correo).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe un viajero con este correo.')
        return correo


class ParticipacionForm(forms.ModelForm):
    """Inscripción de un viajero en un viaje (el viaje viene fijo desde la URL)."""

    class Meta:
        model = Participacion
        fields = ['viajero', 'rol', 'estado']
        labels = {'viajero': 'Viajero', 'rol': 'Rol en el viaje', 'estado': 'Estado de la participación'}

    def __init__(self, *args, viaje, **kwargs):
        super().__init__(*args, **kwargs)
        self.viaje = viaje
        aplicar_bootstrap(self)

    def clean(self):
        cleaned = super().clean()
        viajero, rol, estado = cleaned.get('viajero'), cleaned.get('rol'), cleaned.get('estado')
        otras = self.viaje.participaciones.exclude(pk=self.instance.pk)

        if self.viaje.estado == 'F':
            raise forms.ValidationError('El viaje está finalizado: no admite cambios en sus participantes.')
        if viajero and otras.filter(viajero=viajero).exists():
            self.add_error('viajero', 'Este viajero ya participa en el viaje.')
        if rol == 'O' and otras.filter(rol='O').exists():
            self.add_error('rol', 'El viaje ya tiene un organizador.')
        if estado == 'C' and otras.filter(estado='C').count() >= self.viaje.cupos:
            self.add_error('estado', 'No quedan cupos disponibles para confirmar esta participación.')
        return cleaned
