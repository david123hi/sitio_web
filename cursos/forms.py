from django import forms

from cuentas.forms import BootstrapModelForm
from .models import Curso


class CursoForm(BootstrapModelForm):
    class Meta:
        model = Curso
        fields = ['titulo', 'area', 'instructor', 'nivel', 'duracion_horas',
                  'precio_clp', 'descripcion', 'imagen']
        labels = {'titulo': 'Título', 'area': 'Área', 'instructor': 'Instructor',
                  'nivel': 'Nivel', 'duracion_horas': 'Duración (horas)',
                  'precio_clp': 'Precio (CLP, 0 = gratuito)', 'descripcion': 'Descripción',
                  'imagen': 'Imagen (ruta en static)'}
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 4})}

    def clean_titulo(self):
        titulo = self.cleaned_data['titulo'].strip()
        if len(titulo) < 3:
            raise forms.ValidationError('El título debe tener al menos 3 caracteres.')
        return titulo

    def clean_duracion_horas(self):
        horas = self.cleaned_data['duracion_horas']
        if horas < 1:
            raise forms.ValidationError('La duración debe ser de al menos 1 hora.')
        return horas

    def clean(self):
        datos = super().clean()
        titulo, instructor = datos.get('titulo'), (datos.get('instructor') or '').strip()
        if titulo and instructor:
            repetido = Curso.objects.filter(
                titulo__iexact=titulo, instructor__iexact=instructor
            ).exclude(pk=self.instance.pk)
            if repetido.exists():
                raise forms.ValidationError(
                    'Ya existe un curso con ese título dictado por ese instructor.')
        return datos
