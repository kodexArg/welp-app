# dj-apprunner-template

Template para proyectos Django en AWS App Runner, incluyendo integración con RDS (PostgreSQL) y S3 con CloudFront.

Incluye:
- Django 5
- Vite + django-vite
- Tailwind CSS v4
- HTMX + django-htmx
- django-components


## 📋 Estado del Proyecto

### Infraestructura Core ✅
- App Runner configurado con Python 3.11
- Variables de entorno y secretos
- Gunicorn como servidor WSGI
- Gestión de dependencias con uv
- Configuración de IAM roles y políticas
- Secrets Manager configurado
- **Build de frontend optimizado en AppRunner** ✅
- **Desarrollo local con Vite** ✅

### Servicios AWS ✅
- Secrets Manager con secretos configurados
- RDS (PostgreSQL) con acceso configurado
- S3 + CloudFront con políticas de acceso
- IAM roles y políticas necesarias

### Frontend ✅
- [x] Instalación de django-vite
- [x] Integración de favicon con Vite
- [x] Build de frontend integrado en AppRunner pre_build
- [x] Desarrollo local con Vite (npm run dev)
- [x] Configuración de Tailwind CSS v4
- [x] Integración de HTMX
- [x] **Implementación de django-components** ✅
  - [x] Configuración completa en settings.py
  - [x] Componente de prueba "ping" funcional
  - [x] Estructura de archivos optimizada
  - [x] CSS/JS específicos por componente

> **Nota Técnica:** El stack frontend está diseñado para ser completamente autónomo en producción. Todos los assets (JS, CSS, imágenes) se sirven desde S3/CloudFront, sin dependencias de CDNs externos. HTMX, Vite, Tailwind y django-components funcionan 100% offline una vez desplegados.

### Welp Desk ✅
- [x] Sistema de tickets y mesa de ayuda
- [x] Admin panel organizado por categorías
- [x] Estados de tickets configurados
- [x] Template tags para UI
- [x] Clases CSS para estados
- [x] Sistema de colores consistente
- [x] Validación de transiciones de estado
- [x] Funciones utilitarias para flujo de trabajo

**Estados de Tickets Disponibles:**
- `open`: Abierto (rojo) → feedback, solved, closed
- `feedback`: Comentado (azul) → solved, closed  
- `solved`: Solucionado (verde) → authorized, rejected, closed
- `authorized`: Autorizado (verde claro) → closed
- `rejected`: Rechazado (amarillo) → feedback, solved
- `closed`: Cerrado (gris) → [estado final]

**Sistema de Clases CSS:**
```css
/* Badges básicos (fondo suave) */
.status-open, .status-feedback, .status-solved, 
.status-authorized, .status-rejected, .status-closed

/* Badges con fondo sólido (mayor contraste) */
.status-solid.status-[estado]

/* Clases utilitarias por contexto */
.text-status-[estado]     /* Color de texto */
.bg-status-[estado]       /* Color de fondo */
.border-status-[estado]   /* Color de borde */
.hover-status-[estado]    /* Efectos hover */
```

**Funciones Utilitarias Python:**
```python
from welp_desk.constants import DESK_STATUSES
from welp_desk.utils import get_available_desk_transitions

# Acceso directo a estados
DESK_STATUSES['open']['label']  # 'Abierto'
DESK_STATUSES['open']['color']  # '#dc2626'

# Transiciones disponibles
get_available_desk_transitions('solved')  # ['authorized', 'rejected', 'closed']

# Métodos del modelo Ticket
ticket.can_transition_to_status('closed')  # Boolean
ticket.get_available_status_transitions()  # Lista
ticket.is_active  # Boolean
ticket.is_final   # Boolean
```

**Uso en Templates:**
```html
{% load core_tags %}

<!-- Badge básico -->
{% status_badge ticket.status %}

<!-- Badge con fondo sólido para mayor contraste -->
{% status_badge ticket.status variant="solid" %}

<!-- Badge con etiqueta personalizada -->
{% status_badge "authorized" label="Aprobado" variant="solid" %}
```

### Próximos Pasos 🚧
1. Sistema de Autenticación
   - [ ] Implementación de autenticación Django
   - [ ] Integración con OAuth2
2. API REST
   - [ ] Desarrollo de endpoints
   - [ ] Implementación de seguridad JWT
   - [ ] Documentación con Swagger/OpenAPI

## 📝 Stack Tecnológico

- **Backend**: Python 3.11, Django, Gunicorn
- **Base de datos**: PostgreSQL (RDS)
- **Almacenamiento**: S3 + CloudFront
- **Despliegue**: AWS App Runner
- **Frontend**: Vite, Tailwind v4, HTMX, Django Components
- **Desarrollo**: Hot-reload con Vite

## 🔧 Proceso de Build y Desarrollo

### Desarrollo Local
1. Instalar dependencias:
```bash
uv venv
source .venv/bin/activate  # o .venv\Scripts\activate en Windows
uv pip install -r requirements.txt
npm install
```

2. Iniciar servidor de desarrollo:
```bash
# Opción recomendada: Script integrado (Windows)
.\scripts\dev.ps1

# O manualmente en terminales separadas:
# Terminal 1: Backend Django
python manage.py runserver

# Terminal 2: Frontend Vite
npm run dev
```

### AppRunner Build Process
El proceso de build se ha optimizado dividiendo las tareas entre las fases de AppRunner:

**Build environment variables** (apprunner.yaml):
- `NODE_VERSION`: Versión de Node.js (20.13.1)
- `NODE_DIST`: Distribución de Node.js (node-v20.13.1-linux-x64)
- `NODE_PATH`: Ruta de instalación de Node.js (/tmp/.node)

**Pre-build phase** (apprunner.yaml):
- Instalación de herramientas del sistema (tar, xz)
- Instalación de Node.js usando variables de entorno
- Instalación de dependencias frontend (`npm install`)
- Build de assets frontend (`npm run build`)

**Build phase** (apprunner.yaml):
- Instalación de uv
- Creación del entorno virtual Python
- Instalación de dependencias Python

**Runtime phase** (scripts/start.sh):
- Migraciones de Django
- Colección de archivos estáticos (`collectstatic`)
- Verificación/creación de superusuario
- Ejecución de pruebas
- Inicio del servidor Gunicorn

> **NOTAS TÉCNICAS:** 
> - El comando `collectstatic` se mantiene en runtime debido a que requiere acceso a variables de entorno AWS y secretos que no están disponibles durante la fase de build.
> - Las variables de entorno para Node.js (NODE_VERSION, NODE_DIST, NODE_PATH) se definen en el bloque `build.env` de AppRunner para mayor claridad y mantenibilidad.
> - En desarrollo, Vite proporciona hot-reload para cambios en el frontend mientras Django maneja el backend.

### Configuración Requerida

### IAM Roles y Políticas

El proyecto utiliza el rol de instancia `kdx-django-apprunner-instance-role` con las siguientes políticas:
- `kdx-AlvsVirginiaS3AccessPolicy`
- `kdx-django-apprunner-required-secrets`
- `kdx-Rds-db-free-tier-policy`

### Secrets Manager

Se requieren los siguientes secretos en AWS Secrets Manager:

1. `django-secret-3cNpZN`:
   - DJANGO_SUPERUSER_USERNAME
   - DJANGO_SUPERUSER_EMAIL
   - DJANGO_SUPERUSER_PASSWORD
   - SECRET_KEY

2. `rds!db-b2e1ff83-1545-4806-bd37-df9fd2a3de95`:
   - username
   - password

3. `pingping/secret-VcQsw5`:
   - PING (valor de prueba que devuelve "PONG")

### Política de Acceso a Secrets

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue"
            ],
            "Resource": [
                "arn:aws:secretsmanager:us-east-1:789650504128:secret:rds!db-b2e1ff83-1545-4806-bd37-df9fd2a3de95-SR96y6",
                "arn:aws:secretsmanager:us-east-1:789650504128:secret:django-secret-3cNpZN",
                "arn:aws:secretsmanager:us-east-1:789650504128:secret:pingping/secret-VcQsw5"
            ]
        }
    ]
}
```

## 📦 Instalación

1. Clonar el repositorio
2. Configurar los secretos en AWS Secrets Manager según la estructura descrita
3. Asegurar que el rol de instancia tenga las políticas necesarias
4. Configurar las variables de entorno en `apprunner.yaml`
5. Desplegar en AWS App Runner

## 🧪 Pruebas

<details>
<summary>Ver Tests</summary>

<pre>
1. Configuración (tests/test_timezone_config.py)
   ├── test_timezone_environment_variable_exists
   ├── test_timezone_is_valid_zoneinfo
   ├── test_apprunner_yaml_contains_timezone
   ├── test_apprunner_timezone_is_valid
   ├── test_settings_and_apprunner_timezone_match
   └── test_timezone_is_argentina_mendoza

2. Modelos (core/tests/test_models.py)
   ├── test_create_user
   ├── test_create_superuser
   └── test_user_str_representation

3. Vistas (core/tests/test_views.py)
   ├── test_hello_world
   ├── test_health_check
   ├── test_db_health_check_success
   └── test_db_health_check_failure

4. Integración
   ├── tests/test_ping_secret.py::test_ping_secret
   ├── tests/test_db.py::test_database_connection
   └── tests/test_s3.py::test_s3_write_and_read
</pre>
</details>

> **NOTA:** El home (`/`) ahora incluye un Dashboard de Verificación Tecnológica que muestra en tiempo real el estado de cada tecnología del stack. Si ves las 4 tecnologías marcadas como activas (Vite, Tailwind, HTMX, Components), la configuración es exitosa. El componente "ping" demuestra la funcionalidad completa de django-components con CSS/JS integrados.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## welp_payflow

Las vistas de welp_payflow están organizadas en el submódulo `welp_payflow/views/`:
- `views.py`: vistas principales (home, list, create)
- `htmx.py`: vistas HTMX (por implementar)
- `others.py`: vistas auxiliares (SelectOptionsView, etc.)

Actualizar imports y rutas según esta estructura.