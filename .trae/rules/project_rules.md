---
description: Reglas TRAE del Proyecto - Infraestructura y Organización Completa
tags: ["Project", "Infrastructure", "Django", "Frontend", "Backend"]
slug: project-rules
alwaysApply: true
---

# Reglas TRAE del Proyecto

## Infraestructura

### Desarrollo (dev)
- **Entorno**: Local con PostgreSQL + Django:8000 + Vite:5173
- **Ejecución**: `scripts/dev.sh` para iniciar desarrollo
- **Base de datos**: PostgreSQL local + inicialización automática con `scripts/init_app.py`
- **Dependencias**: `uv` para Python, `npm` para Node.js
- **Scripts importantes**:
  - `scripts/dev.sh`: Script principal de desarrollo (inicia npm + Django)
  - `scripts/dev.ps1`: Script de desarrollo para Windows PowerShell
  - `scripts/init_app.py`: Inicializa datos de PayFlow desde `init_payflow.yaml`
  - `scripts/seed_payflow.py`: Puebla tickets de ejemplo desde YAML

### Producción (prod)
- **Plataforma**: AWS AppRunner + RDS PostgreSQL (expuesto a internet)
- **Servidor**: Gunicorn:8080 sirviendo Django
- **Rama**: `prod` branch con deployment automático
- **Configuración**: `apprunner.yaml` + Vite build automático
- **Infraestructura AWS**:
  - **S3**: `alvs-virginia-s3` para almacenamiento de archivos
  - **CloudFront**: `d2g4tf0q5e3v42.cloudfront.net` para CDN
  - **Secrets Manager**: Gestión segura de credenciales y variables sensibles
  - **RDS**: PostgreSQL en `database-free-tier.cccpxuiv6n1v.us-east-1.rds.amazonaws.com`
- **Scripts de deployment**:
  - `scripts/build-for-production.sh`: Prepara assets frontend para producción
  - `scripts/start.sh`: Script de inicio en AppRunner (migraciones + collectstatic + init)
  - `scripts/update_supervisors.py`: Actualiza permisos de supervisores

## Organización del Proyecto Full-stack

**Visión holística**: Este es un proyecto Django full-stack donde Gunicorn sirve tanto el backend como el frontend integrado. Vite compila los assets frontend (CSS, JS, fonts) y los deposita en `static/dist/` para que Django los sirva como archivos estáticos.

**Flujo de assets**: 
- Desarrollo: Vite:5173 (hot reload) + Django:8000 (backend)
- Producción: Vite build → `static/dist/` → Django collectstatic → Gunicorn sirve todo

**Stack tecnológico**: Django 5.2.3 + Vite 5.4.19 + HTMX 2.0.4 + Tailwind 4.1.8 + PostgreSQL

**Estructura del proyecto**:
```
welp-app/
├── core/                  # Funcionalidades base y componentes
├── welp_desk/             # Sistema de helpdesk  
├── welp_payflow/          # Circuito de compras y pagos
├── api/                   # API REST endpoints
├── frontend/              # Assets frontend (CSS, JS, fonts)
├── templates/             # Templates Django
├── static/dist/           # Assets compilados por Vite
├── project/               # Configuración Django
├── scripts/               # Scripts de desarrollo y despliegue
└── tests/                 # Tests de integración del proyecto
```

**Documentación del proyecto**:
- `README.md`: Documentación principal del sistema, arquitectura y características
- `PAYFLOW.md`: Documentación específica del módulo Welp Payflow
- `LICENSE`: Licencia del proyecto

**Gestión de dependencias**:
- `pyproject.toml`: Configuración del proyecto Python y dependencias
- `uv.lock`: Lock file de dependencias Python (uv)
- `package.json`: Dependencias Node.js y scripts npm
- `package-lock.json`: Lock file de dependencias Node.js

## Backend

**Configuración Django**:
- **Versión**: Django 5.2.3 con configuración en `project/settings.py`
- **Variables de entorno**: `.env` (desarrollo) / `apprunner.yaml` (producción)
- **Archivos estáticos**: `static/dist/` (compilados por Vite)
- **Estructura de aplicaciones**:
```python
app_name/
├── models.py          # Modelos de datos
├── forms.py           # Formularios Django
├── views/             # Vistas organizadas por módulos
├── utils.py           # Funciones auxiliares (presente en welp_payflow)
├── constants.py       # Constantes y variables de entorno
├── urls.py            # Routing de URLs
├── admin.py           # Interface administrativa
├── apps.py            # Configuración de la aplicación
├── templatetags/      # Template tags personalizados
├── tests/             # Tests organizados (core) o tests.py (welp_payflow)
├── management/        # Comandos Django personalizados (welp_payflow)
└── migrations/        # Migraciones de base de datos
```

### Migraciones

**Desarrollo**: Las migraciones son ejecutadas únicamente por el usuario mediante `makemigrations` + `migrate`

**Producción**: Las migraciones se ejecutan automáticamente via AppRunner siguiendo el flujo: Build → Migrate → Start. El sistema las aplica durante el deployment sin intervención manual.

### Configuración de Datos Iniciales

**Archivo de configuración**: `scripts/init_payflow.yaml` contiene la estructura de UDNs, Sectores, Categorías Contables y Usuarios

**Scripts de inicialización**:
- `scripts/init_app.py`: Crea UDNs, Sectores, Categorías y Usuarios desde el YAML
- `scripts/init_users.py`: Script específico para crear solo usuarios y roles
- `scripts/update_supervisors.py`: Asigna acceso completo a supervisores

**Datos de prueba**: `scripts/seed_payflow.py` + archivos YAML para poblar tickets de ejemplo

## Frontend

**Estructuras de templates Django y Vite**:

**Templates Django**:
- **Directorio base**: `/templates` (configurado en settings)
- **Organización**: `core/`, `welp_desk/`, `welp_payflow/`, `components/`

**Vite**:
- **Versión**: Vite 5.4.19 con vite-plugin-static-copy 3.0.0
- **Configuración**: `vite.config.mjs` compila hacia `static/dist/` + genera `manifest.json`
- **Entry points**: `frontend/main.css` y `frontend/main.js`
- **Dependencias adicionales**: Mermaid 11.8.1 para diagramas

### Estilos globales y Tailwind 4

**Uso de CSS**: El directorio `/frontend/css/` contiene todos los estilos, con `frontend/main.css` como punto de entrada principal.

**Archivos CSS**: `variables.css`, `base.css`, `themes.css`, `utilities.css`, `ticket.css`, `components.css`, `navbar.css`, `animations.css`, `fontawesome.css`, `fontawesome-fonts.css`.

**Orden de importación en main.css**: Variables → Base → Themes → Utilities → Ticket → Components → Navbar → Animations → FontAwesome

**Organización**: Los estilos están organizados en layers de Tailwind (`@layer base`, `@layer components`, `@layer utilities`)

**Compilación**: Todos los estilos se importan en `main.css` y Vite los compila hacia `static/dist/`.

### Componentes templatetags

**Ubicación real**: 
- `core/templatetags/`: `core_tags.py`, `format_tags.py`, `ui_tags.py`
- `welp_payflow/templatetags/`: `payflow_tags.py`, `ticket_message_tags.py`

**Directorio de componentes reales**: 
- `templates/core/components/`: Componentes base (button.html, nav-link.html, user-toggle.html, etc.)
- `templates/welp_payflow/components/`: Componentes específicos de PayFlow (ticket_message.html, status-badge.html, etc.)

**Formato de componentes**: HTML + CSS (con `@apply` Tailwind) + HTMX

**Reutilización**: Los componentes se cargan con `{% load ui_tags %}` y se incluyen con `{% include %}`

## Sistema de Templates

**Configuración Django**: Definida en `project/settings.py` con `TEMPLATES` configurado para:
- **Backend**: `django.template.backends.django.DjangoTemplates`
- **Directorio base**: `BASE_DIR / 'templates'` (directorio `/templates` en la raíz del proyecto)
- **Template loaders**: 
  - Desarrollo: `filesystem.Loader` + `app_directories.Loader`
  - Producción: `cached.Loader` envolviendo los loaders anteriores para optimización

**Estructura de templates**:
```
templates/
├── core/                    # Templates base y componentes globales
│   ├── base.html           # Template base del proyecto
│   ├── components/         # Componentes reutilizables globales
│   │   ├── button.html
│   │   ├── nav-link.html
│   │   └── user-toggle.html
│   └── dev/                # Templates de desarrollo
├── welp_desk/              # Templates específicos de helpdesk
└── welp_payflow/           # Templates específicos de PayFlow
    ├── components/         # Componentes específicos de PayFlow
    ├── htmx/              # Fragmentos HTMX
    └── partials/          # Partials reutilizables
```

**Jerarquía de resolución**: Django busca templates en este orden:
1. `templates/` (directorio global configurado en DIRS)
2. `{app}/templates/` (auto-discovery por app_directories.Loader)

**Convenciones de naming**:
- Templates principales: `{app}/{view}.html`
- Componentes: `{app}/components/{component}.html`
- Partials HTMX: `{app}/htmx/{fragment}.html`
- Partials reutilizables: `{app}/partials/{partial}.html`