# Sitio Informativo — Proyecto Django (Evaluación Sumativa #2, TI3041)

Evolución del proyecto de la Evaluación Sumativa N°1: dos aplicaciones
(**blog** y **destinos**) que antes leían datos desde archivos JSON, ahora
con **persistencia en base de datos relacional**, **Django Admin** y
consultas mediante **Django ORM**.

## Aplicaciones y modelo de datos

### `blog`
| Modelo      | Descripción                                    | Relaciones |
|-------------|--------------------------------------------------|------------|
| `Categoria` | Categoría de un artículo (Backend, Frontend, IA) | 1 categoría → N artículos |
| `Articulo`  | Artículo del blog (título, autor, fecha, contenido) | FK a `Categoria` |

### `destinos`
| Modelo       | Descripción                              | Relaciones |
|--------------|--------------------------------------------|------------|
| `Continente` | Continente de un destino (Asia, Europa...) | 1 continente → N destinos |
| `Destino`    | Destino de viaje (país, precio, duración)  | FK a `Continente` |

Todas las entidades están registradas y son 100% administrables (crear,
modificar, eliminar, buscar y navegar entre relacionadas) desde
**Django Admin** (`/admin/`).

## Variables de entorno

Las configuraciones sensibles (`SECRET_KEY`, credenciales de base de datos)
**no están escritas en el código**. Se cargan desde un archivo `.env`
mediante `python-decouple`. El archivo `.env` ya viene incluido y
funcional para correr en local con sqlite3; `.env.example` es la plantilla
de referencia (y la que se sube a GitHub, `.env` está en `.gitignore`).

## Instalación y ejecución local

```bash
# 1. Clonar el repositorio
git clone URL_DEL_REPOSITORIO
cd sitio_web

# 2. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac / Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Variables de entorno (ya viene un .env listo; si quieres regenerarlo)
copy .env.example .env       # Windows
cp .env.example .env         # Mac / Linux

# 5. Aplicar migraciones (crea las tablas en la base de datos)
python manage.py migrate

# 6. Migrar los datos originales de los JSON hacia la base de datos
python manage.py cargar_articulos
python manage.py cargar_destinos

# 7. Crear superusuario para Django Admin
python manage.py createsuperuser

# 8. Levantar el servidor de desarrollo
python manage.py runserver
```

Luego abre en tu navegador:

- `http://127.0.0.1:8000/` → Inicio (app blog)
- `http://127.0.0.1:8000/articulos/` → Listado de artículos (desde BD)
- `http://127.0.0.1:8000/destinos/` → Listado de destinos (desde BD)
- `http://127.0.0.1:8000/admin/` → Panel de administración (CRUD completo)

Los comandos `cargar_articulos` y `cargar_destinos` leen `data/articulos.json`
y `data/destinos.json` (se conservan como evidencia del origen de los datos
de la Evaluación N°1) y los insertan en la base de datos usando el ORM.
Se pueden ejecutar varias veces sin duplicar registros.

## Despliegue en AWS EC2 (Linux)

```bash
# Conectarse a la instancia
ssh -i "clave.pem" ubuntu@IP_PUBLICA_EC2

# Dependencias del sistema
sudo apt update
sudo apt install -y python3-venv python3-pip git default-libmysqlclient-dev pkg-config mysql-server

# Clonar el proyecto
git clone URL_DEL_REPOSITORIO
cd sitio_web

# Entorno virtual + dependencias
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Variables de entorno (usar datos de la BD MySQL creada en la instancia)
cp .env.example .env
nano .env   # DB_ENGINE=django.db.backends.mysql, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST=localhost, DB_PORT=3306

# Migraciones + carga de datos + superusuario
python manage.py migrate
python manage.py cargar_articulos
python manage.py cargar_destinos
python manage.py createsuperuser

# Levantar el servidor (accesible desde fuera de la instancia)
python manage.py runserver 0.0.0.0:8000
```

Verificar en `phpMyAdmin` que las tablas `blog_categoria`, `blog_articulo`,
`destinos_continente` y `destinos_destino` existen, con sus registros y
llaves foráneas.

## Rutas principales

| Ruta               | Descripción                          |
|---------------------|----------------------------------------|
| `/`                 | Inicio del blog                        |
| `/articulos/`       | Listado de artículos (filtro y buscador) |
| `/articulos/<id>/`  | Detalle de un artículo                 |
| `/destinos/`        | Listado de destinos (filtro y buscador) |
| `/destinos/<slug>/` | Detalle de un destino                  |
| `/admin/`           | Django Admin (CRUD completo)           |

Cada vista de listado incluye botones **Agregar / Modificar / Eliminar /
Buscar** (marcadores visuales de la interfaz; su funcionalidad completa se
implementará en la siguiente evaluación sumativa).

## Uso de Inteligencia Artificial

Se utilizó IA como apoyo para: diseñar el modelo de datos relacional a
partir de la estructura de los JSON originales, generar el código de
modelos/admin/vistas y el comando de migración de datos siguiendo buenas
prácticas de Django, y para la configuración de variables de entorno. Los
prompts y respuestas utilizados se documentan en el informe técnico
entregado junto al proyecto.
