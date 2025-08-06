# Reglas del Proyecto Welp

## 1. Especificaciones Técnicas

### Stack Tecnológico Principal
- **Backend**: Django 5.0+ con Python 3.11
- **Frontend**: Vite + Tailwind CSS v4 + HTMX 2.0
- **Base de Datos**: PostgreSQL (AWS RDS)
- **Servidor Web**: Gunicorn
- **Gestión de Dependencias**: `uv` para Python, `npm` para Node.js

### Tecnologías de Soporte
- **Logging**: Loguru con configuración centralizada
- **Componentes**: django-components para reutilización
- **API**: Django REST Framework
- **Testing**: pytest + pytest-django
- **Almacenamiento**: AWS S3 + CloudFront
- **Autenticación**: Django Auth con modelo User personalizado

## 2. Arquitectura del Sistema

### Estructura Modular
El proyecto sigue una arquitectura modular con aplicaciones especializadas:

```
welp-app/
├── core/           # Funcionalidades base y autenticación
├── welp_desk/      # Sistema de helpdesk
├── welp_payflow/   # Circuito de compras y pagos
├── api/            # API REST endpoints
├── project/        # Configuración Django
├── frontend/       # Assets frontend (CSS, JS, fonts)
├── templates/      # Templates Django organizados por app
└── static/         # Archivos estáticos compilados
```

### Principios Arquitectónicos
- **Separación de responsabilidades**: Cada aplicación maneja un dominio específico
- **Modelo de datos unificado**: UDN → Sector con herencia de permisos
- **Frontend reactivo**: HTMX para interactividad sin JavaScript pesado
- **Componentes reutilizables**: django-components para UI consistente

## 3. Entorno de Desarrollo y Despliegue

### Desarrollo Local
- **Requisitos**: Python 3.11+, Node.js 20+, `uv`
- **Configuración**: Variables de entorno en `.env`
- **Servidores**: Django runserver (8000) + Vite dev server (5173)
- **Base de datos**: PostgreSQL local o contenedor

### Despliegue en Producción
- **Plataforma**: AWS App Runner
- **Build**: Automatizado via `apprunner.yaml`
- **Secrets**: AWS Secrets Manager
- **Almacenamiento**: S3 + CloudFront para assets
- **Base de datos**: AWS RDS PostgreSQL

### Pipeline de Build
1. **Pre-build**: Instalación Node.js + `npm install` + `npm run build`
2. **Build**: Instalación Python + `uv pip install`
3. **Runtime**: Migraciones + collectstatic + Gunicorn

## 4. Estándares de Código

### Estructura de Aplicaciones Django
```python
app_name/
├── models.py      # Solo modelos, sin lógica de negocio
├── forms.py       # Formularios Django con validación
├── views.py       # Solo coordinación, delegar a services/
├── services.py    # Lógica de negocio completa
├── utils.py       # Funciones auxiliares específicas
├── constants.py   # SOLO imports de variables de entorno
├── urls.py        # Routing clean y RESTful
├── admin.py       # Interface administrativa
└── migrations/    # Solo automáticas desde CI
```

### Reglas de Desarrollo
- **Settings**: `project/settings.py` es de SOLO LECTURA
- **Constantes**: NUNCA hardcodear, usar variables de entorno
- **Utils**: Cada app mantiene su `utils.py` independiente
- **HTMX Views**: Basadas en funciones, lógica en services
- **Testing**: 95% coverage en services, 100% en utils

### Gestión de Variables de Entorno
```python
# constants.py - CORRECTO
import os
from django.conf import settings

DEFAULT_TIMEOUT = int(os.environ.get('DEFAULT_TIMEOUT', '300'))
API_BASE_URL = settings.API_BASE_URL

# INCORRECTO - NUNCA hacer esto
# DEFAULT_TIMEOUT = 300  # ❌ Constante hardcodeada
```

## 5. Frontend y Assets

### Tailwind CSS v4
- **Configuración**: Sin `tailwind.config.js` (obsoleto en v4)
- **Utilities first**: Preferir clases Tailwind directas
- **Mobile first**: Base para móvil, breakpoints para desktop
- **Purging**: Automático via Vite

### Vite Configuration
- **Build**: `frontend/main.js` y `frontend/main.css` como entry points
- **Assets**: Fonts y favicon copiados via `vite-plugin-static-copy`
- **Output**: `static/dist/` para integración con Django
- **Development**: Hot reload en puerto 5173

### Performance Standards
- **Bundle size**: Máximo 250KB por chunk
- **CSS size**: Máximo 50KB después de purge
- **Load time**: First Contentful Paint < 1.5s

## 6. Configuración de Seguridad

### Variables de Entorno Críticas
```yaml
# Desarrollo (.env)
DEBUG=True
IS_LOCAL=True
SECRET_KEY=your-secret-key
DB_HOST=localhost

# Producción (apprunner.yaml secrets)
SECRET_KEY: ARN de Secrets Manager
DB_USERNAME: ARN de RDS secrets
DB_PASSWORD: ARN de RDS secrets
```

### Configuración de Seguridad
- **CSRF**: Cookies seguras, SameSite=Strict
- **SSL**: Proxy headers para HTTPS
- **CORS**: Dominios específicos en CSRF_TRUSTED_ORIGINS
- **Sessions**: Cookies seguras en producción

## 7. Roles y Permisos

### Jerarquía de Roles
1. **Usuario Final**: Crea solicitudes propias
2. **Técnico**: Resuelve incidencias, presupuesta
3. **Supervisor**: Primera autorización
4. **Gestor de Compras**: Gestión completa de Payflow
5. **Manager**: Autorización final de pagos
6. **Director**: Segunda firma en autorizaciones críticas

### Modelo de Permisos
- **Herencia**: UDN → Sector → Usuario
- **Automático**: Permisos se propagan por jerarquía
- **Granular**: Control específico por módulo

## 8. Testing y Calidad

### Estrategia de Testing
- **Unit tests**: Services layer (95% coverage)
- **Integration tests**: Flujos críticos de usuario
- **Utils functions**: 100% coverage (funciones puras)
- **Framework**: pytest + pytest-django

### Comandos de Testing
```bash
# Ejecutar tests
pytest

# Con coverage
pytest --cov=core --cov=welp_desk --cov=welp_payflow

# Tests específicos
pytest core/tests/test_models.py
```

## 9. Comandos de Desarrollo

### Desarrollo Local
```bash
# Activar entorno
source .venv/bin/activate

# Instalar dependencias
uv pip install -e .
npm install

# Desarrollo (2 terminales)
npm run dev          # Terminal 1: Vite
python manage.py runserver  # Terminal 2: Django
```

### Scripts Útiles
```bash
# Windows
.\scripts\dev.ps1    # Inicia ambos servidores

# Linux/Mac
./scripts/dev.sh     # Inicia desarrollo
./scripts/start.sh   # Script de producción
```

## 10. Documentación del Proyecto

### Archivos de Referencia
- **README.md**: Visión general y setup
- **PAYFLOW.md**: Documentación específica del módulo de pagos
- **apprunner.yaml**: Configuración de despliegue AWS
- **.cursor/rules/**: Reglas específicas para desarrollo

### Flujos Documentados
- **Ticket Flow**: Flujo general de tickets
- **Payflow**: Circuito completo de compras
- **Purchase Workflow**: Manual técnico interactivo

Esta documentación debe mantenerse actualizada con cada cambio significativo en la arquitectura o configuración del proyecto.