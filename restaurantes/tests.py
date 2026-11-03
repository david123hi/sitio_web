"""
Pruebas automáticas del mantenedor de Restaurantes.

Ejecutar:  python manage.py test restaurantes
"""
from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Restaurante, TipoCocina


class MantenedorRestaurantesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('crear_perfiles', verbosity=0)
        cls.cocina = TipoCocina.objects.create(nombre='Chilena')
        cls.restaurante = Restaurante.objects.create(
            slug='sabores', nombre='Sabores del Sur', tipo_cocina=cls.cocina,
            ciudad='La Serena', direccion='Av. Principal 123',
            rango_precio='$$', calificacion=4.5, descripcion='Comida tradicional.',
        )
        for nombre in ('Administrador', 'Supervisor', 'Administrativo'):
            usuario = User.objects.create_user(nombre.lower(), password='clave-segura-123')
            usuario.groups.add(Group.objects.get(name=nombre))

    def datos(self, **cambios):
        base = {
            'nombre': 'Mar y Tierra', 'tipo_cocina': self.cocina.pk,
            'ciudad': 'Coquimbo', 'direccion': 'Calle 1', 'rango_precio': '$$',
            'calificacion': '4.0', 'descripcion': 'Mariscos frescos.', 'imagen': '',
        }
        base.update(cambios)
        return base

    def entrar(self, usuario):
        self.client.login(username=usuario, password='clave-segura-123')

    # --- Acceso ---
    def test_sin_sesion_redirige_al_login(self):
        respuesta = self.client.get(reverse('restaurantes:restaurante_lista'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('login', respuesta.url)

    def test_todos_los_perfiles_pueden_listar(self):
        for usuario in ('administrador', 'supervisor', 'administrativo'):
            self.entrar(usuario)
            respuesta = self.client.get(reverse('restaurantes:restaurante_lista'))
            self.assertEqual(respuesta.status_code, 200, usuario)

    def test_administrativo_no_puede_crear_ni_eliminar(self):
        self.entrar('administrativo')
        self.assertEqual(self.client.get(reverse('restaurantes:restaurante_crear')).status_code, 403)
        url = reverse('restaurantes:restaurante_eliminar', args=[self.restaurante.pk])
        self.assertEqual(self.client.post(url).status_code, 403)
        self.assertTrue(Restaurante.objects.filter(pk=self.restaurante.pk).exists())

    def test_supervisor_puede_crear_pero_no_eliminar(self):
        self.entrar('supervisor')
        self.assertEqual(self.client.get(reverse('restaurantes:restaurante_crear')).status_code, 200)
        url = reverse('restaurantes:restaurante_eliminar', args=[self.restaurante.pk])
        self.assertEqual(self.client.post(url).status_code, 403)

    # --- CRUD ---
    def test_crear_genera_slug_automatico(self):
        self.entrar('administrador')
        respuesta = self.client.post(reverse('restaurantes:restaurante_crear'), self.datos())
        self.assertRedirects(respuesta, reverse('restaurantes:restaurante_lista'))
        self.assertEqual(Restaurante.objects.get(nombre='Mar y Tierra').slug, 'mar-y-tierra')

    def test_modificar(self):
        self.entrar('administrador')
        url = reverse('restaurantes:restaurante_editar', args=[self.restaurante.pk])
        self.client.post(url, self.datos(nombre='Sabores del Sur', ciudad='Ovalle'))
        self.restaurante.refresh_from_db()
        self.assertEqual(self.restaurante.ciudad, 'Ovalle')

    def test_eliminar(self):
        self.entrar('administrador')
        url = reverse('restaurantes:restaurante_eliminar', args=[self.restaurante.pk])
        self.client.post(url)
        self.assertFalse(Restaurante.objects.filter(pk=self.restaurante.pk).exists())

    def test_buscar(self):
        self.entrar('administrador')
        url = reverse('restaurantes:restaurante_lista')
        self.assertEqual(len(self.client.get(url, {'q': 'sabores'}).context['filas']), 1)
        self.assertEqual(len(self.client.get(url, {'q': 'inexistente'}).context['filas']), 0)

    # --- Validaciones ---
    def test_rechaza_nombre_corto(self):
        self.entrar('administrador')
        respuesta = self.client.post(reverse('restaurantes:restaurante_crear'), self.datos(nombre='ab'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Restaurante.objects.filter(nombre='ab').exists())

    def test_rechaza_calificacion_fuera_de_rango(self):
        self.entrar('administrador')
        respuesta = self.client.post(reverse('restaurantes:restaurante_crear'), self.datos(calificacion='6'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Restaurante.objects.filter(nombre='Mar y Tierra').exists())

    def test_rechaza_nombre_y_ciudad_repetidos(self):
        self.entrar('administrador')
        datos = self.datos(nombre='sabores del sur', ciudad='la serena')
        respuesta = self.client.post(reverse('restaurantes:restaurante_crear'), datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Restaurante.objects.filter(nombre__iexact='sabores del sur').count(), 1)
