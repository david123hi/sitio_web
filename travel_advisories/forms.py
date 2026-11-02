from datetime import date

from django import forms

from cuentas.forms import BootstrapModelForm, aplicar_bootstrap
from .models import Alerta, RequisitoVacuna, Vacuna


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
            'descripcion': 'Descripción (máx. 100 caracteres)',
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

    def clean_descripcion(self):
        descripcion = self.cleaned_data['descripcion'].strip()
        if len(descripcion) < 5:
            raise forms.ValidationError('La descripción debe tener al menos 5 caracteres.')
        return descripcion

    def clean(self):
        cleaned = super().clean()
        emision, expiracion = cleaned.get('emision'), cleaned.get('expiracion')
        if emision and expiracion and expiracion < emision:
            self.add_error('expiracion', 'La fecha de expiración no puede ser anterior a la de emisión.')
        return cleaned


class VacunaForm(BootstrapModelForm):
    class Meta:
        model = Vacuna
        fields = ['nombre', 'descripcion']
        labels = {'nombre': 'Nombre de la vacuna', 'descripcion': 'Descripción'}
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 3})}

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        if Vacuna.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe una vacuna con este nombre.')
        return nombre

    def clean_descripcion(self):
        descripcion = self.cleaned_data['descripcion'].strip()
        if len(descripcion) < 10:
            raise forms.ValidationError('La descripción debe tener al menos 10 caracteres.')
        return descripcion


class RequisitoVacunaForm(forms.ModelForm):
    """
    TRANSACCIÓN "Requisitos de vacunación": asocia una Vacuna a una Alerta
    (la alerta viene fija desde la URL).
    """

    class Meta:
        model = RequisitoVacuna
        fields = ['vacuna', 'tipo', 'notas']
        labels = {'vacuna': 'Vacuna', 'tipo': 'Tipo de requisito', 'notas': 'Notas adicionales'}
        widgets = {'notas': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, alerta, **kwargs):
        super().__init__(*args, **kwargs)
        self.alerta = alerta
        aplicar_bootstrap(self)

    def clean(self):
        cleaned = super().clean()
        vacuna = cleaned.get('vacuna')
        if not self.instance.pk and self.alerta.expiracion < date.today():
            raise forms.ValidationError('La alerta ya expiró: no se pueden agregar nuevos requisitos.')
        if vacuna and RequisitoVacuna.objects.filter(
                pais=self.alerta, vacuna=vacuna).exclude(pk=self.instance.pk).exists():
            self.add_error('vacuna', 'Esta vacuna ya está registrada como requisito de la alerta.')
        return cleaned
