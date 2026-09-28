# Sitio Informativo — Proyecto Django

**Evaluación Sumativa #2 — Aplicación web con Django Admin**
Asignatura: Programación Back End (TI3041) · INACAP sede La Serena
Repositorio: https://github.com/david123hi/sitio_web

## Descripción del proyecto

### Objetivo
Evolucionar el sitio web modular de la Evaluación Sumativa N°1, que leía su
información desde archivos JSON, hacia una aplicación web funcional con
**base de datos relacional**, administrable desde **Django Admin** y
desplegada en infraestructura cloud (**AWS EC2**), usando **Git y GitHub**
como control de versiones y mecanismo de distribución.

### Temática
Sitio informativo con dos módulos independientes:

- **blog**: artículos de tecnología clasificados por categoría.
- **destinos**: destinos de viaje clasificados por continente.

### Funcionalidades implementadas
- Modelos Django con relaciones (`ForeignKey`) y migraciones.
- Migración completa de los datos JSON hacia la base de datos
  (comandos `cargar_articulos` y `cargar_destinos`).
- Todas las entidades registradas en Django Admin (crear, modificar,
  eliminar, visualizar, buscar y navegar entre entidades relacionadas).
- Vistas que obtienen la información mediante consultas Django ORM y la
  muestran con plantillas Django y Bootstrap (tarjetas y tablas).
- Filtro por categoría/continente y búsqueda por nombre en los listados.
- Barra de navegación Bootstrap entre los módulos.
- Botones **Agregar, Modificar, Eliminar y Buscar** visibles en cada
  listado (marcadores visuales con enlace `#`; su funcionamiento real se
  implementa en la siguiente evaluación sumativa).
- Configuración sensible fuera del código, mediante variables de entorno.

## Arquitectura

### Estructura de carpetas
```
sitio_web/
├── manage.py
├── requirements.txt
├── .env.example          # plantilla de variables de entorno (se sube a GitHub)
├── .gitignore
├── config/               # configuración del proyecto (settings, urls, wsgi)
├── templates/            # plantilla base global (base.html)
├── static/               # Bootstrap local y estilos propios
├── data/                 # JSON originales de la Evaluación N°1 (origen de datos)
├── blog/                 # app 1
│   ├── models.py         # Categoria, Articulo
│   ├── admin.py
│   ├── views.py / urls.py
│   ├── migrations/
│   ├── templates/blog/
│   └── management/commands/cargar_articulos.py
└── destinos/             # app 2
    ├── models.py         # Continente, Destino
    ├── admin.py
    ├── views.py / urls.py
    ├── migrations/
    ├── templates/destinos/
    └── management/commands/cargar_destinos.py
```

### Base de datos y modelo de datos
- **Local (desarrollo):** SQLite, para poder ejecutar el proyecto sin instalar nada.
- **EC2 (producción):** MySQL, administrado y verificado desde phpMyAdmin.

El motor se elige solo con variables de entorno; el código no cambia.

| App | Tabla | Finalidad | Relación |
|---|---|---|---|
| blog | `blog_categoria` | Clasifica los artículos (Backend, Frontend, IA) | 1 categoría → N artículos |
| blog | `blog_articulo` | Guarda cada artículo (título, autor, fecha, contenido) | FK a `Categoria` |
| destinos | `destinos_continente` | Clasifica los destinos (Asia, Europa, ...) | 1 continente → N destinos |
| destinos | `destinos_destino` | Guarda cada destino (país, precio, duración) | FK a `Continente` |

Las llaves foráneas usan `on_delete=PROTECT`, por lo que no se puede eliminar
una categoría o continente que aún tenga registros asociados.

## Variables de entorno

Las configuraciones sensibles (`SECRET_KEY`, credenciales de la base de datos)
**no están escritas en el código**: se cargan desde un archivo `.env` con la
librería `python-decouple`.

- `.env` contiene los valores reales y **no se sube a GitHub** (está en `.gitignore`).
- `.env.example` es la plantilla que sí se versiona.
- Quien clone el repositorio debe **crear su propio `.env`** copiando `.env.example`.

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Django |
| `DEBUG` | `True` en desarrollo/demostración |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por coma (en EC2 incluir la IP pública) |
| `DB_ENGINE` | `django.db.backends.sqlite3` (local) o `django.db.backends.mysql` (EC2) |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Conexión a la base de datos |

## Ejecución local

```bash
# 1. Clonar el repositorio
git clone https://github.com/david123hi/sitio_web.git
cd sitio_web

# 2. Crear y activar el entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac / Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear el archivo .env desde la plantilla
copy .env.example .env         # Windows
cp .env.example .env           # Mac / Linux

# 5. Crear las tablas (migraciones)
python manage.py migrate

# 6. Migrar los datos de los JSON hacia la base de datos
python manage.py cargar_articulos
python manage.py cargar_destinos

# 7. Crear el superusuario de Django Admin
python manage.py createsuperuser

# 8. Levantar el servidor
python manage.py runserver
```

> En Windows, `pip install -r requirements.txt` puede fallar al instalar
> `mysqlclient`. Solo se necesita para MySQL (EC2); en local con SQLite se
> puede omitir instalando manualmente `Django` y `python-decouple`.

Rutas del sitio:

| Ruta | Descripción |
|---|---|
| `/` | Inicio (app blog) |
| `/articulos/` | Listado de artículos (filtro y buscador) |
| `/articulos/<id>/` | Detalle de un artículo |
| `/destinos/` | Listado de destinos (filtro y buscador) |
| `/destinos/<slug>/` | Detalle de un destino |
| `/admin/` | Django Admin (CRUD completo) |

## Despliegue en AWS EC2 (Ubuntu Linux)

### 1. Instancia y acceso
En el *Security Group* de la instancia abrir los puertos **22** (SSH),
**80** (phpMyAdmin) y **8000** (Django).

```bash
ssh -i "clave.pem" ubuntu@IP_PUBLICA_EC2
```

### 2. Dependencias del sistema
```bash
sudo apt update
sudo apt install -y python3-venv python3-pip git default-libmysqlclient-dev pkg-config build-essential mysql-server
```

### 3. Base de datos MySQL
```bash
sudo mysql
```
```sql
CREATE DATABASE sitio_web CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'django_user'@'localhost' IDENTIFIED BY 'UNA_CLAVE_SEGURA';
GRANT ALL PRIVILEGES ON sitio_web.* TO 'django_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. phpMyAdmin
```bash
sudo apt install -y apache2 php libapache2-mod-php php-mysql phpmyadmin
```
Se accede desde `http://IP_PUBLICA_EC2/phpmyadmin` con `django_user`.

### 5. Clonar el proyecto desde GitHub
```bash
git clone https://github.com/david123hi/sitio_web.git
cd sitio_web
```

### 6. Entorno virtual y dependencias
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 7. Variables de entorno
```bash
cp .env.example .env
nano .env
```
Valores a completar:
```
SECRET_KEY=una-clave-larga-y-unica
DEBUG=True
ALLOWED_HOSTS=IP_PUBLICA_EC2,localhost
DB_ENGINE=django.db.backends.mysql
DB_NAME=sitio_web
DB_USER=django_user
DB_PASSWORD=UNA_CLAVE_SEGURA
DB_HOST=localhost
DB_PORT=3306
```

### 8. Migraciones, datos y superusuario
```bash
python manage.py migrate
python manage.py cargar_articulos
python manage.py cargar_destinos
python manage.py createsuperuser
```

### 9. Ejecutar el servidor
```bash
python manage.py runserver 0.0.0.0:8000
```
El sitio queda disponible en `http://IP_PUBLICA_EC2:8000/`.

### 10. Verificación en phpMyAdmin
En la base `sitio_web` deben existir las tablas `blog_categoria`,
`blog_articulo`, `destinos_continente` y `destinos_destino`, con sus
registros y sus llaves foráneas (además de las tablas internas de Django).

## Control de versiones

Todo el proyecto está versionado con Git y alojado en GitHub. El proyecto se
obtiene en EC2 con:

```bash
git clone https://github.com/david123hi/sitio_web.git
```

## Uso de Inteligencia Artificial

Se utilizó IA como apoyo al desarrollo para: diseñar el modelo de datos
relacional a partir de la estructura de los JSON originales, generar el
código de modelos, administración y vistas, escribir el comando de migración
de datos, y configurar las variables de entorno y el despliegue. Los prompts
utilizados, las respuestas obtenidas y su aplicación en el proyecto se
documentan en el Documento Técnico entregado junto al proyecto.
