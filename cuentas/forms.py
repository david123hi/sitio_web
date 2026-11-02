"""Formularios de la app cuentas (login, recuperación y gestión de usuarios)."""
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordResetForm, SetPasswordForm, UserCreationForm,
)
from django.contrib.auth.models import Group, User

from .roles import PERFILES


def aplicar_bootstrap(form):
    """Agrega las clases de Bootstrap a todos los campos de un formulario."""
    for campo in form.fields.values():
        widget = campo.widget
        if isinstance(widget, forms.CheckboxInput):
            clase = 'form-check-input'
        elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
            clase = 'form-select'
        else:
            clase = 'form-control'
        actuales = widget.attrs.get('class', '')
        if clase not in actuales.split():
            widget.attrs['class'] = f'{actuales} {clase}'.strip()


class BootstrapModelForm(forms.ModelForm):
    """ModelForm base: aplica Bootstrap automáticamente."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_bootstrap(self)


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Usuario'
        self.fields['password'].label = 'Contraseña'
        aplicar_bootstrap(self)


class RecuperarForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = 'Correo electrónico'
        aplicar_bootstrap(self)


class NuevaClaveForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_bootstrap(self)


def _grupos_de_perfil():
    return Group.objects.filter(name__in=PERFILES).order_by('name')


class UsuarioCrearForm(UserCreationForm):
    """Alta de usuario con asignación de grupo (perfil)."""
    grupo = forms.ModelChoiceField(
        queryset=Group.objects.none(), label='Perfil (grupo)',
        empty_label='Seleccione un perfil...',
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grupo'].queryset = _grupos_de_perfil()
        self.fields['email'].required = True
        self.fields['first_name'].label = 'Nombres'
        self.fields['last_name'].label = 'Apellidos'
        self.fields['email'].label = 'Correo electrónico'
        self.fields['username'].label = 'Usuario'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Repetir contraseña'
        aplicar_bootstrap(self)

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe un usuario con este correo.')
        return email

    def save(self, commit=True):
        usuario = super().save(commit=commit)
        if commit:
            usuario.groups.set([self.cleaned_data['grupo']])
        return usuario


class UsuarioEditarForm(forms.ModelForm):
    """Modificación de un usuario: datos, estado y perfil."""
    grupo = forms.ModelChoiceField(
        queryset=Group.objects.none(), label='Perfil (grupo)',
        empty_label='Seleccione un perfil...',
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'is_active')
        labels = {
            'first_name': 'Nombres', 'last_name': 'Apellidos',
            'email': 'Correo electrónico', 'is_active': 'Usuario activo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grupo'].queryset = _grupos_de_perfil()
        self.fields['email'].required = True
        if self.instance.pk:
            self.fields['grupo'].initial = self.instance.groups.filter(name__in=PERFILES).first()
        aplicar_bootstrap(self)

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe otro usuario con este correo.')
        return email

    def save(self, commit=True):
        usuario = super().save(commit=commit)
        if commit:
            # Reemplaza solo los perfiles del sistema; conserva otros grupos si los hubiera.
            otros = usuario.groups.exclude(name__in=PERFILES)
            usuario.groups.set([self.cleaned_data['grupo'], *otros])
        return usuario
