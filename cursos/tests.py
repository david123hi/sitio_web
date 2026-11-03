"""
Pruebas automáticas del mantenedor de Cursos.

Ejecutar:  python manage.py test cursos
"""
from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Area, Curso


class MantenedorCursosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('crear_perfiles', verbosity=0)
        cls.area = Area.objects.create(nombre='Programación')
        cls.curso = Curso.objects.create(
            titulo='Python Básico', area=cls.area, instructor='Ana Pérez',
            nivel='basico', duracion_horas=20, precio_clp=0, descripcion='Introducción.',
        )
        for nombre in ('Administrador', 'Supervisor', 'Administrativo'):
            usuario = User.objects.create_user(nombre.lower(), password='clave-segura-123')
            usuario.groups.add(Group.objects.get(name=nombre))

    def datos(self, **cambios):
        base = {
            'titulo': 'Django Avanzado', 'area': self.area.pk, 'instructor': 'Luis Soto',
            'nivel': 'basico', 'duracion_horas': '30', 'precio_clp': '25000',
            'descripcion': 'Proyecto completo.', 'imagen': '',
        }
        base.update(cambios)
        return base

    def entrar(self, usuario):
        self.client.login(username=usuario, password='clave-segura-123')

    # --- Acceso ---
    def test_sin_sesion_redirige_al_login(self):
        respuesta = self.client.get(reverse('cursos:curso_lista'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('login', respuesta.url)

    def test_administrativo_solo_lectura(self):
        self.entrar('administrativo')
        self.assertEqual(self.client.get(reverse('cursos:curso_lista')).status_code, 200)
        self.assertEqual(self.client.get(reverse('cursos:curso_crear')).status_code, 403)
        url = reverse('cursos:curso_eliminar', args=[self.curso.pk])
        self.assertEqual(self.client.post(url).status_code, 403)

    def test_supervisor_no_puede_eliminar(self):
        self.entrar('supervisor')
        url = reverse('cursos:curso_eliminar', args=[self.curso.pk])
        self.assertEqual(self.client.post(url).status_code, 403)
        self.assertTrue(Curso.objects.filter(pk=self.curso.pk).exists())

    # --- CRUD ---
    def test_crear(self):
        self.entrar('administrador')
        respuesta = self.client.post(reverse('cursos:curso_crear'), self.datos())
        self.assertRedirects(respuesta, reverse('cursos:curso_lista'))
        self.assertTrue(Curso.objects.filter(titulo='Django Avanzado').exists())

    def test_modificar(self):
        self.entrar('administrador')
        url = reverse('cursos:curso_editar', args=[self.curso.pk])
        self.client.post(url, self.datos(titulo='Python Básico', instructor='Ana Pérez', precio_clp='9990'))
        self.curso.refresh_from_db()
        self.assertEqual(self.curso.precio_clp, 9990)

    def test_eliminar(self):
        self.entrar('administrador')
        self.client.post(reverse('cursos:curso_eliminar', args=[self.curso.pk]))
        self.assertFalse(Curso.objects.filter(pk=self.curso.pk).exists())

    def test_buscar(self):
        self.entrar('administrador')
        url = reverse('cursos:curso_lista')
        self.assertEqual(len(self.client.get(url, {'q': 'python'}).context['filas']), 1)
        self.assertEqual(len(self.client.get(url, {'q': 'inexistente'}).context['filas']), 0)

    # --- Validaciones ---
    def test_rechaza_titulo_corto(self):
        self.entrar('administrador')
        respuesta = self.client.post(reverse('cursos:curso_crear'), self.datos(titulo='ab'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Curso.objects.filter(titulo='ab').exists())

    def test_rechaza_duracion_cero(self):
        self.entrar('administrador')
        respuesta = self.client.post(reverse('cursos:curso_crear'), self.datos(duracion_horas='0'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Curso.objects.filter(titulo='Django Avanzado').exists())

    def test_rechaza_titulo_e_instructor_repetidos(self):
        self.entrar('administrador')
        datos = self.datos(titulo='python básico', instructor='ana pérez')
        respuesta = self.client.post(reverse('cursos:curso_crear'), datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Curso.objects.filter(titulo__iexact='python básico').count(), 1)
