# Sitio Informativo — Proyecto Django

**Evaluación Sumativa N°2 — Aplicación web con Django Admin**
Asignatura: Programación Back End (TI3041) · INACAP sede La Serena
Repositorio: <https://github.com/david123hi/sitio_web>

## Integrantes y responsabilidades

| Integrante                        | Módulos (aplicaciones Django) a cargo |
| --------------------------------- | ------------------------------------- |
| Brian David Monroy Araya          | `blog`, `destinos`                    |
| Diego Alexis Carvajal Cerda       | `restaurantes`, `cursos`              |
| Fernando Nicolás Bernales Ibáñez  | `travelers`, `travel_advisories`      |

## Descripción del proyecto

### Objetivo

Evolucionar el sitio web modular de la Evaluación Sumativa N°1, que leía su
información desde archivos JSON, hacia una aplicación web funcional con **base de datos relacional**, administrable desde **Django Admin** y
desplegada en infraestructura cloud (**AWS EC2**), usando **Git y GitHub** como control de versiones y mecanismo de distribución.

### Temática

Sitio informativo con seis módulos (aplicaciones Django) independientes:

- **blog**: artículos de tecnología clasificados por categoría.
- **destinos**: destinos de viaje clasificados por continente.
- **cursos**: catálogo de cursos online agrupados por área de conocimiento.
- **restaurantes**: guía de restaurantes agrupados por tipo de cocina.
- **travelers**: viajes programados hacia un destino, viajeros y su participación en cada viaje.
- **travel_advisories**: alertas de viaje por destino y requisitos de vacunación.

### Funcionalidades implementadas

- Modelos Django con relaciones (`ForeignKey`) y migraciones en las seis aplicaciones (14 tablas propias).
- Migración completa de los datos JSON hacia la base de datos
(comandos `cargar_articulos`, `cargar_destinos`, `cargar_cursos` y `cargar_restaurantes`).
- Todas las entidades registradas en Django Admin (crear, modificar,
eliminar, visualizar, buscar y navegar entre entidades relacionadas).
- Vistas que obtienen la información mediante consultas Django ORM y la
muestran con plantillas Django y Bootstrap (tarjetas y tablas).
- Filtro por categoría, continente, área o tipo de cocina, y búsqueda por nombre en los listados de los módulos con filtros.
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
├── blog/                 # app 1: Categoria, Articulo
├── destinos/             # app 2: Continente, Destino
├── cursos/               # app 3: Area, Curso
├── restaurantes/         # app 4: TipoCocina, Restaurante
├── travelers/            # app 5: Viaje, Viajero, Participacion
└── travel_advisories/    # app 6: Alerta, Vacuna, RequisitoVacuna
```

Cada aplicación contiene su propio `models.py`, `admin.py`, `views.py`, `urls.py`,
carpeta `migrations/` y sus plantillas. Las aplicaciones `blog`, `destinos`, `cursos` y
`restaurantes` incluyen además un comando `management/commands/cargar_*.py` que migra
los datos desde `data/*.json` hacia la base de datos.

### Base de datos y modelo de datos

- **Local (desarrollo):** SQLite, para poder ejecutar el proyecto sin instalar nada.
- **EC2 (producción):** MariaDB (compatible con MySQL), administrado y verificado desde phpMyAdmin.

El motor se elige solo con variables de entorno; el código no cambia.

### Tablas y finalidad

| App               | Tabla                                 | Finalidad                                                          |
| ----------------- | ------------------------------------- | ------------------------------------------------------------------ |
| blog              | `blog_categoria`                      | Clasifica los artículos (Backend, Frontend, IA)                    |
| blog              | `blog_articulo`                       | Guarda cada artículo (título, autor, fecha, contenido)             |
| destinos          | `destinos_continente`                 | Clasifica los destinos (Asia, Europa, ...)                         |
| destinos          | `destinos_destino`                    | Guarda cada destino (país, precio, duración)                       |
| cursos            | `cursos_area`                         | Agrupa los cursos por área de conocimiento                         |
| cursos            | `cursos_curso`                        | Guarda cada curso (instructor, nivel, horas, precio)               |
| restaurantes      | `restaurantes_tipococina`             | Clasifica los restaurantes por tipo de cocina                      |
| restaurantes      | `restaurantes_restaurante`            | Guarda cada restaurante (ciudad, dirección, precio, calificación)  |
| travelers         | `travelers_viaje`                     | Viaje programado hacia un destino (fechas, cupos, estado)          |
| travelers         | `travelers_viajero`                   | Persona que puede participar en viajes (nombre, correo)            |
| travelers         | `travelers_participacion`             | Une viajes y viajeros indicando rol y estado de la participación   |
| travel_advisories | `travel_advisories_alerta`            | Alerta de viaje asociada a un destino (nivel, vigencia)            |
| travel_advisories | `travel_advisories_vacuna`            | Catálogo de vacunas                                                |
| travel_advisories | `travel_advisories_requisitovacuna`   | Indica qué vacuna exige o recomienda cada alerta                   |

### Relaciones entre tablas

| Relación                                                        | Tipo                          | `on_delete` |
| --------------------------------------------------------------- | ----------------------------- | ----------- |
| `Articulo` → `Categoria`                                        | N:1 (1 categoría → N artículos) | `PROTECT`   |
| `Destino` → `Continente`                                        | N:1                           | `PROTECT`   |
| `Curso` → `Area`                                                | N:1                           | `PROTECT`   |
| `Restaurante` → `TipoCocina`                                    | N:1                           | `PROTECT`   |
| `Viaje` → `Destino` (de la app destinos)                        | N:1                           | `CASCADE`   |
| `Participacion` → `Viaje` y `Participacion` → `Viajero`         | N:1 y N:1 (tabla intermedia)  | `CASCADE`   |
| `Alerta` → `Destino` (de la app destinos)                       | N:1                           | `CASCADE`   |
| `RequisitoVacuna` → `Alerta` y `RequisitoVacuna` → `Vacuna`     | N:1 y N:1 (tabla intermedia)  | `CASCADE`   |

Resumen de las relaciones:

- **Viajes y viajeros** forman una relación muchos a muchos: un viaje tiene varios
  viajeros y un viajero puede ir a varios viajes. La tabla `travelers_participacion`
  la resuelve y agrega el rol (organizador, viajero, invitado) y el estado (confirmado,
  pendiente, no viaja).
- **Alertas y vacunas** también son muchos a muchos, resueltos por `travel_advisories_requisitovacuna`,
  que indica si la vacuna es obligatoria o recomendada.
- Los módulos `travelers` y `travel_advisories` se conectan con `destinos` mediante llaves foráneas
  hacia `destinos_destino`.
- En `blog`, `destinos`, `cursos` y `restaurantes` las llaves foráneas usan `on_delete=PROTECT`, por lo que no se
  puede eliminar una categoría, continente, área o tipo de cocina que aún tenga registros asociados.

## Variables de entorno

Las configuraciones sensibles (`SECRET_KEY`, credenciales de la base de datos) **no están escritas en el código**: se cargan desde un archivo `.env` con la
librería `python-decouple`.

- `.env` contiene los valores reales y **no se sube a GitHub** (está en `.gitignore`).
- `.env.example` es la plantilla que sí se versiona.
- Quien clone el repositorio debe **crear su propio `.env`** copiando `.env.example`.

| Variable                                                  | Descripción                                                             |
| --------------------------------------------------------- | ----------------------------------------------------------------------- |
| `SECRET_KEY`                                              | Clave secreta de Django                                                 |
| `DEBUG`                                                   | `True` en desarrollo/demostración                                       |
| `ALLOWED_HOSTS`                                           | Hosts permitidos, separados por coma (en EC2 incluir la IP pública)     |
| `DB_ENGINE`                                               | `django.db.backends.sqlite3` (local) o `django.db.backends.mysql` (EC2) |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Conexión a la base de datos                                             |

## Ejecución local

```
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
python manage.py cargar_cursos
python manage.py cargar_restaurantes

# 7. Crear el superusuario de Django Admin
python manage.py createsuperuser

# 8. Levantar el servidor
python manage.py runserver
```

> En Windows, `pip install -r requirements.txt` puede fallar al instalar `mysqlclient`. Solo se necesita para MySQL (EC2); en local con SQLite se
> puede omitir instalando manualmente `Django` y `python-decouple`.

Los datos de `travelers` (viajes, viajeros y participaciones) y de `travel_advisories`
(alertas, vacunas y requisitos) se ingresan desde Django Admin. Ver la sección
*Datos de viajes y alertas*.

### Rutas del sitio

| Ruta                          | Descripción                                        |
| ----------------------------- | -------------------------------------------------- |
| `/`                           | Inicio (app blog)                                  |
| `/articulos/`                 | Listado de artículos (filtro y buscador)           |
| `/articulos/<id>/`            | Detalle de un artículo                             |
| `/destinos/`                  | Listado de destinos (filtro y buscador)            |
| `/destinos/<slug>/`           | Detalle de un destino                              |
| `/cursos/`                    | Listado de cursos                                  |
| `/cursos/<id>/`               | Detalle de un curso                                |
| `/restaurantes/`              | Listado de restaurantes                            |
| `/restaurantes/<slug>/`       | Detalle de un restaurante                          |
| `/viajes/`                    | Listado de viajes                                  |
| `/viajes/viajeros/`           | Listado de viajeros                                |
| `/viajes/<id>/`               | Detalle de un viaje y sus participantes            |
| `/travel_advisories/`         | Listado de alertas de viaje                        |
| `/admin/`                     | Django Admin (CRUD completo de las 14 tablas)      |

### Datos de viajes y alertas

Estos módulos no parten de archivos JSON. Se crean desde `/admin/` respetando el
orden de dependencias entre tablas:

1. Viajeros
2. Viajes (requiere un destino ya cargado)
3. Participaciones (requiere un viaje y un viajero)
4. Vacunas
5. Alertas (requiere un destino ya cargado)
6. Requisitos de vacunas (requiere una alerta y una vacuna)

Con 2 o 3 registros por tabla basta para demostrar las relaciones. Los mismos pasos se
repiten en la instancia EC2 después de ejecutar las migraciones y los comandos `cargar_*`.

## Despliegue en AWS EC2 (Amazon Linux)

### Sitio desplegado

La instancia tiene una **IP elástica**, por lo que la dirección no cambia aunque la
instancia se detenga y se vuelva a iniciar.

- **Sitio:** <http://34.237.28.226/>
- **Django Admin:** <http://34.237.28.226/admin/>
- **phpMyAdmin:** <http://34.237.28.226:8080/>

> Las credenciales de acceso se entregan en el Documento Técnico.

### Arquitectura del despliegue

```
Navegador ──► Nginx (puerto 80) ──► Gunicorn (socket unix) ──► Django ──► MariaDB
Navegador ──► Nginx (puerto 8080) ──► PHP-FPM ──► phpMyAdmin ──► MariaDB
```

| Componente | Servicio systemd     | Función                                              |
| ---------- | -------------------- | ---------------------------------------------------- |
| Django     | `gunicorn.service`   | Ejecuta la aplicación (`config.wsgi:application`)    |
| Nginx      | `nginx.service`      | Recibe las visitas y las reenvía a Gunicorn / phpMyAdmin |
| MariaDB    | `mariadb.service`    | Base de datos `sitio_web`                            |
| PHP-FPM    | `php-fpm.service`    | Ejecuta phpMyAdmin                                   |

El proyecto está en `/var/www/negocio` (clonado desde GitHub), con su entorno virtual
`venv/`, su archivo `.env` y la carpeta `staticfiles/` generada con `collectstatic`.
Gunicorn se ejecuta como servicio con:

```
/var/www/negocio/venv/bin/gunicorn --access-logfile - --workers 3 \
  --bind unix:/var/www/negocio/gunicorn.sock config.wsgi:application
```

Todos los servicios arrancan solos al iniciar la instancia, por lo que no hace falta
levantar nada a mano después de un reinicio.

### 1. Instancia y acceso

En el *Security Group* de la instancia abrir el puerto **22** (SSH, idealmente solo desde la IP propia), **80** (sitio Django) y **8080** (phpMyAdmin, idealmente restringido a la IP propia). No se abre el puerto 3306: la base de datos solo acepta conexiones locales.

```
ssh -i "clave.pem" ec2-user@34.237.28.226
```

### 2. Dependencias del sistema

```
sudo dnf update -y
sudo dnf install -y python3 python3-pip git gcc python3-devel pkgconf-pkg-config mariadb105-devel
```

### 3. Base de datos

Se utiliza MariaDB, con una base `sitio_web` y un usuario dedicado para Django:

```
CREATE DATABASE sitio_web CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'django_user'@'localhost' IDENTIFIED BY 'UNA_CLAVE_SEGURA';
GRANT ALL PRIVILEGES ON sitio_web.* TO 'django_user'@'localhost';
FLUSH PRIVILEGES;
```

La base se administra y verifica desde phpMyAdmin (puerto 8080).

### 4. Clonar el proyecto desde GitHub

```
cd /var/www
git clone https://github.com/david123hi/sitio_web.git negocio
cd negocio
```

### 5. Entorno virtual y dependencias

En Amazon Linux el comando es `python3` (fuera del entorno virtual no existe `python`).

```
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Variables de entorno

```
cp .env.example .env
nano .env
```

Valores a completar:

```
SECRET_KEY=una-clave-larga-y-unica
DEBUG=True
ALLOWED_HOSTS=34.237.28.226,localhost
DB_ENGINE=django.db.backends.mysql
DB_NAME=sitio_web
DB_USER=django_user
DB_PASSWORD=UNA_CLAVE_SEGURA
DB_HOST=localhost
DB_PORT=3306
```

### 7. Migraciones, datos, archivos estáticos y superusuario

```
python manage.py migrate
python manage.py cargar_articulos
python manage.py cargar_destinos
python manage.py cargar_cursos
python manage.py cargar_restaurantes
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Los viajes, viajeros, alertas y vacunas se crean después desde `/admin/`, siguiendo el orden
indicado en la sección *Datos de viajes y alertas*, ya que dependen de los destinos cargados.

### 8. Servicios

Gunicorn, Nginx, MariaDB y PHP-FPM quedan habilitados para iniciar con el sistema:

```
sudo systemctl enable --now gunicorn nginx mariadb php-fpm
sudo systemctl status gunicorn nginx mariadb php-fpm
```

### 9. Actualizar el sitio con cambios de GitHub

```
cd /var/www/negocio
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

### 10. Reinicio de la instancia

En AWS Academy el laboratorio detiene la instancia al terminar la sesión. Los datos y
la IP elástica se conservan y los servicios arrancan solos. Para reanudar basta con
iniciar el laboratorio y la instancia en EC2, esperar a que pasen las comprobaciones de
estado y abrir el sitio. Si algo no responde, revisar los servicios con
`sudo systemctl status gunicorn nginx mariadb php-fpm` y reiniciar el que esté detenido.

### 11. Verificación en phpMyAdmin

En la base `sitio_web` deben existir las 14 tablas propias:
`blog_categoria`, `blog_articulo`, `destinos_continente`, `destinos_destino`,
`cursos_area`, `cursos_curso`, `restaurantes_tipococina`, `restaurantes_restaurante`,
`travelers_viaje`, `travelers_viajero`, `travelers_participacion`,
`travel_advisories_alerta`, `travel_advisories_vacuna` y `travel_advisories_requisitovacuna`,
con sus registros y sus llaves foráneas (además de las tablas internas de Django).
Las relaciones se ven en la pestaña **Diseñador**.

## Control de versiones

Todo el proyecto está versionado con Git y alojado en GitHub. El proyecto se
obtiene en EC2 con:

```
git clone https://github.com/david123hi/sitio_web.git
```

El archivo `.gitignore` excluye el archivo `.env`, el entorno virtual (`venv/`),
las bases de datos locales (`*.sqlite3`) y los archivos temporales de Python.

## Uso de Inteligencia Artificial

Se utilizó IA como apoyo al desarrollo para: diseñar el modelo de datos
relacional a partir de la estructura de los JSON originales, generar el
código de modelos, administración y vistas, escribir el comando de migración
de datos, corregir errores de migraciones (por ejemplo, el error
`python: command not found` al desplegar en Amazon Linux) y configurar las
variables de entorno y el despliegue. Los prompts utilizados, las respuestas
obtenidas y su aplicación en el proyecto se documentan en el Documento Técnico
entregado junto al proyecto.
