"""
Configuración del proyecto Django "config".

Sitio Web Modular con Django e Inteligencia Artificial
Evaluación Sumativa #2 - Programación Back End (TI3041)

A partir de esta evaluación:
- Las configuraciones sensibles (SECRET_KEY, credenciales de BD) ya no
  están escritas en el código: se cargan desde un archivo .env mediante
  la librería python-decouple.
- La base de datos deja de ser solo "interna" de Django: ahora almacena
  también la información del sitio (Categoria, Articulo, Continente,
  Destino), migrada desde los archivos JSON de la Evaluación N°1.
"""

from pathlib import Path
from decouple import config, Csv

# Directorio raíz del proyecto (donde está manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------
# Seguridad (valores reales en el archivo .env, no versionado en git)
# ------------------------------------------------------------------
SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())

# ------------------------------------------------------------------
# Aplicaciones instaladas
# ------------------------------------------------------------------
INSTALLED_APPS = [
    'operaciones',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicaciones propias del proyecto
    'blog',
    'destinos',
    'cursos',
    'restaurantes',
    'travelers',
    'travel_advisories',

    # Evaluación N°3: autenticación, perfiles (grupos) y dashboards
    'cuentas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Carpeta de plantillas global del proyecto (contiene base.html)
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,  # también busca en <app>/templates/
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cuentas.context_processors.perfil',   # expone `rol_usuario`
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ------------------------------------------------------------------
# Base de datos
# ------------------------------------------------------------------
# Por defecto usa sqlite3 (funciona en cualquier equipo sin instalar
# nada más). En la instancia EC2 se configura MySQL vía variables de
# entorno en el archivo .env (DB_ENGINE, DB_NAME, DB_USER, etc.),
# para poder verificar las tablas desde phpMyAdmin.
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=str(BASE_DIR / 'db.sqlite3')),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------
# Archivos estáticos (CSS, JS, imágenes, Bootstrap local)
# ------------------------------------------------------------------
STATIC_URL = 'static/'

# Carpeta adicional de estáticos a nivel de proyecto (bootstrap local, css propio)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Carpeta donde se recolectan los estáticos para producción (collectstatic)
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ------------------------------------------------------------------
# Ruta a los archivos JSON originales de la Evaluación N°1.
# Se conservan solo como fuente de datos para los comandos de
# migración (cargar_articulos / cargar_destinos); el sitio ya NO lee
# directamente desde aquí.
# ------------------------------------------------------------------
DATA_DIR = BASE_DIR / 'data'


# ------------------------------------------------------------------
# Evaluación Sumativa N°3: autenticación y recuperación de contraseña
# ------------------------------------------------------------------
LOGIN_URL = 'cuentas:login'
LOGIN_REDIRECT_URL = 'cuentas:dashboard'
LOGOUT_REDIRECT_URL = 'cuentas:login'

# El enlace de recuperación (token firmado) vence a la hora.
PASSWORD_RESET_TIMEOUT = 60 * 60

# Correo saliente. Por defecto los correos se imprimen en la consola del
# servidor (útil en desarrollo). Para enviarlos de verdad (EC2 / demo),
# definir en el .env: EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# y las variables EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD.
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER or 'no-responder@viajesjuanito.local')
