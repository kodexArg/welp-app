# Configuración de Entorno - Proyecto Welp

## 1. Requisitos del Sistema

### Desarrollo Local

* **Python**: 3.11 o superior

* **Node.js**: 20.13.1 o superior

* **PostgreSQL**: 13+ (local o contenedor)

* **Git**: Para control de versiones

* **uv**: Gestor de paquetes Python

### Herramientas Recomendadas

* **IDE**: VS Code con extensiones Python y Django

* **Terminal**: Bash/Zsh en Linux/Mac, PowerShell en Windows

* **Cliente DB**: pgAdmin, DBeaver o psql

* **Cliente HTTP**: Postman, Insomnia o Thunder Client

## 2. Configuración Inicial

### Instalación de Dependencias

#### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd welp-app
```

#### 2. Configurar Python

```bash
# Instalar uv si no está instalado
curl -LsSf https://astral.sh/uv/install.sh | sh

# Crear entorno virtual
uv venv

# Activar entorno virtual
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Instalar dependencias
uv pip install -e .
```

#### 3. Configurar Node.js

```bash
# Instalar dependencias frontend
npm install

# Verificar instalación
npm run build
```

### Configuración de Base de Datos

#### Opción 1: PostgreSQL Local

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS (con Homebrew)
brew install postgresql
brew services start postgresql

# Crear base de datos
sudo -u postgres createdb welp_db
sudo -u postgres createuser welp_user
sudo -u postgres psql -c "ALTER USER welp_user WITH PASSWORD 'welp_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE welp_db TO welp_user;"
```

#### Opción 2: Docker

```bash
# Crear contenedor PostgreSQL
docker run --name welp-postgres \
  -e POSTGRES_DB=welp_db \
  -e POSTGRES_USER=welp_user \
  -e POSTGRES_PASSWORD=welp_password \
  -p 5432:5432 \
  -d postgres:15
```

## 3. Variables de Entorno

### Archivo .env para Desarrollo

Crear archivo `.env` en la raíz del proyecto:

```bash
# Django Core
DEBUG=True
IS_LOCAL=True
SECRET_KEY=tu-clave-secreta-local-muy-larga-y-segura
TIMEZONE=America/Argentina/Mendoza

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=welp_db
DB_USERNAME=welp_user
DB_PASSWORD=welp_password

# AWS (opcional en desarrollo)
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=
AWS_S3_CUSTOM_DOMAIN=
AWS_S3_OBJECT_PARAMETERS={"CacheControl": "max-age=86400"}

# Desarrollo
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@welp.local
DJANGO_SUPERUSER_PASSWORD=admin123
```

### Validación de Variables

```bash
# Verificar que todas las variables están configuradas
python -c "from project.settings import *; print('✅ Configuración válida')"
```

## 4. Inicialización del Proyecto

### Migraciones y Datos Iniciales

```bash
# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Cargar datos iniciales (opcional)
python scripts/init_app.py
python scripts/init_users.py
```

### Verificación de la Instalación

```bash
# Ejecutar tests
pytest

# Verificar que el servidor inicia
python manage.py runserver

# En otra terminal, verificar frontend
npm run dev
```

## 5. Flujo de Desarrollo

### Desarrollo Diario

#### Opción 1: Manual (2 terminales)

```bash
# Terminal 1: Backend Django
source .venv/bin/activate
python manage.py runserver

# Terminal 2: Frontend Vite
npm run dev
```

#### Opción 2: Scripts Automatizados

```bash
# Windows
.\scripts\dev.ps1

# Linux/Mac
./scripts/dev.sh
```

### Comandos Útiles

```bash
# Crear nueva migración
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Recolectar archivos estáticos
python manage.py collectstatic

# Shell interactivo
python manage.py shell

# Ejecutar tests específicos
pytest core/tests/test_models.py

# Build de producción
npm run build
```

## 6. Configuración de IDE

### VS Code

Crear `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "."
  ],
  "emmet.includeLanguages": {
    "django-html": "html"
  },
  "files.associations": {
    "*.html": "django-html"
  }
}
```

### Extensiones Recomendadas

* Python

* Django

* Tailwind CSS IntelliSense

* HTMX Attributes

* PostgreSQL

* GitLens

## 7. Troubleshooting

### Problemas Comunes

#### Error de Base de Datos

```bash
# Verificar conexión
psql -h localhost -U welp_user -d welp_db

# Recrear base de datos
dropdb welp_db
createdb welp_db
python manage.py migrate
```

#### Error de Dependencias Python

```bash
# Limpiar entorno
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -e .
```

#### Error de Assets Frontend

```bash
# Limpiar cache
rm -rf node_modules
rm package-lock.json
npm install
npm run build
```

#### Error de Permisos

```bash
# Linux: Verificar permisos de archivos
chmod +x scripts/*.sh

# Windows: Ejecutar como administrador
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Logs de Desarrollo

```bash
# Ver logs de Django
python manage.py runserver --verbosity=2

# Ver logs de Vite
npm run dev -- --debug

# Logs de base de datos
tail -f /var/log/postgresql/postgresql-*.log
```

## 8. Testing en Desarrollo

### Configuración de Tests

```bash
# Ejecutar todos los tests
pytest

# Tests con coverage
pytest --cov=core --cov=welp_desk --cov=welp_payflow

# Tests específicos
pytest core/tests/test_models.py::TestUserModel

# Tests en modo watch
pytest-watch
```

### Base de Datos de Test

```python
# settings.py - configuración automática
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
```

## 9. Deployment Local

### Simulación de Producción

```bash
# Build de producción
export DEBUG=False
export IS_LOCAL=False
npm run build
python manage.py collectstatic --noinput

# Servidor con Gunicorn
gunicorn project.wsgi:application --bind 0.0.0.0:8000
```

### Docker para Testing

```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

```bash
# Build y run
docker build -f Dockerfile.dev -t welp-dev .
docker run -p 8000:8000 welp-dev
```

## 10. Mantenimiento

### Actualizaciones Regulares

```bash
# Actualizar dependencias Python
uv pip list --outdated
uv pip install --upgrade <package>

# Actualizar dependencias Node.js
npm outdated
npm update

# Verificar seguridad
npm audit
npm audit fix
```

### Limpieza Periódica

```bash
# Limpiar archivos temporales
python manage.py clearsessions
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Limpiar cache de npm
npm cache clean --force

# Limpiar logs
truncate -s 0 /var/log/welp/*.log
```

Esta configuración garantiza un entorno de desarrollo robusto y consistente para todos los miembros del equipo
