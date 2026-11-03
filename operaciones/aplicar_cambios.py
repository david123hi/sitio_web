#!/usr/bin/env python3
"""
Integra la app 'operaciones' en el proyecto.

Uso (desde la carpeta que contiene manage.py, con el venv activado):
    python3 operaciones/aplicar_cambios.py

Hace 4 cosas (cada archivo modificado queda respaldado como .bak):
 1. Agrega 'operaciones' a INSTALLED_APPS.
 2. Agrega la ruta operaciones/ al urls.py principal.
 3. Agrega el menu "Operaciones" en templates/base_gestion.html.
 4. Agrega las 4 transacciones al panel "Transacciones" de cada dashboard.
Se puede ejecutar mas de una vez: no repite lo que ya esta hecho.
"""
import re
import shutil
from pathlib import Path

RAIZ = Path.cwd()


def leer(ruta):
    return ruta.read_text(encoding='utf-8')


def guardar(ruta, texto):
    respaldo = ruta.with_name(ruta.name + '.bak')
    if not respaldo.exists():
        shutil.copy(ruta, respaldo)
    ruta.write_text(texto, encoding='utf-8')


# ---------------------------------------------------------------- 1 y 2
def parchear_settings_y_urls():
    manage = RAIZ / 'manage.py'
    if not manage.exists():
        print('[!] No encuentro manage.py. Ejecuta el script desde la carpeta del proyecto.')
        return
    m = re.search(r"DJANGO_SETTINGS_MODULE['\"]\s*,\s*['\"]([\w.]+)['\"]", leer(manage))
    if not m:
        print('[!] No pude detectar el módulo de settings en manage.py.')
        return
    settings = RAIZ / (m.group(1).replace('.', '/') + '.py')
    if not settings.exists():
        print(f'[!] No existe {settings}. Agrega "operaciones" a INSTALLED_APPS a mano.')
        return

    texto = leer(settings)
    if re.search(r"['\"]operaciones['\"]", texto):
        print(f'[=] {settings.relative_to(RAIZ)}: "operaciones" ya está en INSTALLED_APPS.')
    else:
        nuevo, n = re.subn(r"(INSTALLED_APPS\s*=\s*\[)", r"\1\n    'operaciones',", texto, count=1)
        if n:
            guardar(settings, nuevo)
            print(f'[+] {settings.relative_to(RAIZ)}: agregado "operaciones" a INSTALLED_APPS.')
        else:
            print(f'[!] {settings.relative_to(RAIZ)}: no encontré INSTALLED_APPS = [ ... ]. Agrégalo a mano.')

    m = re.search(r"ROOT_URLCONF\s*=\s*['\"]([\w.]+)['\"]", texto)
    if not m:
        print('[!] No encontré ROOT_URLCONF. Agrega la ruta de operaciones al urls.py a mano.')
        return
    urls = RAIZ / (m.group(1).replace('.', '/') + '.py')
    if not urls.exists():
        print(f'[!] No existe {urls}. Agrega la ruta de operaciones a mano.')
        return
    texto = leer(urls)
    if 'operaciones.urls' in texto:
        print(f'[=] {urls.relative_to(RAIZ)}: la ruta de operaciones ya existe.')
        return
    nuevo, n = re.subn(r"(urlpatterns\s*=\s*\[)",
                       r"\1\n    path('operaciones/', include('operaciones.urls')),", texto, count=1)
    if not n:
        print(f'[!] {urls.relative_to(RAIZ)}: no encontré urlpatterns = [ ... ]. Agrégalo a mano.')
        return
    guardar(urls, nuevo)
    print(f'[+] {urls.relative_to(RAIZ)}: agregada la ruta operaciones/.')
    if not re.search(r"\binclude\b", texto.split('urlpatterns')[0]):
        print('[!] Revisa que "include" y "path" estén importados en ese archivo '
              '(from django.urls import path, include).')


# ---------------------------------------------------------------- 3
ANCLA_NAV = '{% if perms.auth.view_user %}<li class="nav-item">'
BLOQUE_NAV = """{% if perms.operaciones.view_reservadestino or perms.operaciones.view_reservamesa or perms.operaciones.view_inscripcioncurso or perms.operaciones.view_suscripcionblog %}
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle {% if ns == 'operaciones' %}active{% endif %}" href="#" role="button" data-bs-toggle="dropdown">Operaciones</a>
                        <ul class="dropdown-menu">
                            {% if perms.operaciones.view_reservadestino %}<li><a class="dropdown-item" href="{% url 'operaciones:destino_lista' %}">Reservas de destinos</a></li>{% endif %}
                            {% if perms.operaciones.view_reservamesa %}<li><a class="dropdown-item" href="{% url 'operaciones:mesa_lista' %}">Reservas de mesa</a></li>{% endif %}
                            {% if perms.operaciones.view_inscripcioncurso %}<li><a class="dropdown-item" href="{% url 'operaciones:curso_lista' %}">Inscripciones a cursos</a></li>{% endif %}
                            {% if perms.operaciones.view_suscripcionblog %}<li><a class="dropdown-item" href="{% url 'operaciones:blog_lista' %}">Suscripciones al blog</a></li>{% endif %}
                        </ul>
                    </li>
                    {% endif %}"""


def parchear_navbar():
    ruta = RAIZ / 'templates' / 'base_gestion.html'
    if not ruta.exists():
        print('[!] No encuentro templates/base_gestion.html.')
        return
    texto = leer(ruta)
    if 'operaciones:destino_lista' in texto:
        print('[=] base_gestion.html: el menú Operaciones ya existe.')
        return
    if ANCLA_NAV not in texto:
        print('[!] base_gestion.html: no encontré el punto de inserción (enlace de Usuarios). Agrégalo a mano.')
        return
    guardar(ruta, texto.replace(ANCLA_NAV, BLOQUE_NAV + '\n                    ' + ANCLA_NAV, 1))
    print('[+] base_gestion.html: agregado el menú Operaciones.')


# ---------------------------------------------------------------- 4
ITEMS = [
    ('view_reservadestino', 'destino_lista', 'bi-geo-alt', 'Reservas de destinos'),
    ('view_reservamesa', 'mesa_lista', 'bi-egg-fried', 'Reservas de mesa'),
    ('view_inscripcioncurso', 'curso_lista', 'bi-mortarboard', 'Inscripciones a cursos'),
    ('view_suscripcionblog', 'blog_lista', 'bi-newspaper', 'Suscripciones al blog'),
]
PANEL = re.compile(
    r'<div class="panel-head">\s*<i class="bi bi-arrow-left-right"></i>\s*Transacciones\s*</div>')
CIERRE = re.compile(r'\n[ \t]*</div>')


def parchear_dashboards():
    carpeta = RAIZ / 'cuentas' / 'templates' / 'cuentas'
    archivos = sorted(carpeta.glob('dashboard_*.html'))
    if not archivos:
        print('[!] No encontré los dashboards en cuentas/templates/cuentas/.')
        return
    for ruta in archivos:
        texto = leer(ruta)
        if 'operaciones:destino_lista' in texto:
            print(f'[=] {ruta.name}: ya tiene los enlaces de operaciones.')
            continue
        panel = PANEL.search(texto)
        if not panel:
            print(f'[!] {ruta.name}: no encontré el panel "Transacciones". Agrégalo a mano.')
            continue
        cierre = CIERRE.search(texto, panel.end())
        if not cierre:
            print(f'[!] {ruta.name}: no pude ubicar el final del panel. Agrégalo a mano.')
            continue
        lineas = ''
        for permiso, url, icono, etiqueta in ITEMS:
            lineas += (
                f"\n            {{% if perms.operaciones.{permiso} %}}"
                f"<a class=\"quick-item\" href=\"{{% url 'operaciones:{url}' %}}\">"
                f"<span class=\"qi\"><i class=\"bi {icono}\"></i></span>{etiqueta}"
                f"<i class=\"bi bi-chevron-right\"></i></a>{{% endif %}}"
            )
        guardar(ruta, texto[:cierre.start()] + lineas + texto[cierre.start():])
        print(f'[+] {ruta.name}: agregadas las transacciones al panel.')


if __name__ == '__main__':
    parchear_settings_y_urls()
    parchear_navbar()
    parchear_dashboards()
    print('\nListo. Revisa los cambios con: git diff')
