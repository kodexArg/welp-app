# Welp: Sistema Integrado de Gestión Interna

Welp es una plataforma unificada diseñada para centralizar y optimizar los flujos de trabajo internos de una organización. Se compone de dos módulos principales construidos sobre una arquitectura compartida: **Welp Desk** para soporte técnico y **Welp Payflow** para un circuito completo de compras y pagos.

El proyecto está construido con un stack moderno que incluye Django 5, Vite, Tailwind CSS v4 y HTMX, desplegado de forma nativa en AWS a través de App Runner.

## 🚀 Aplicaciones Principales

| Módulo | Descripción | Enfoque |
| :--- | :--- | :--- |
| **Welp Desk** | Sistema de helpdesk para la gestión de incidencias y solicitudes técnicas. | **Resolución de problemas**: agiliza la comunicación entre usuarios y equipos técnicos para resolver incidencias recurrentes de manera eficiente. |
| **Welp Payflow** | Circuito completo para solicitudes de compras y pagos, desde la requisición inicial hasta la aprobación final. | **Control financiero y operativo**: acelera el proceso de compras, garantiza las aprobaciones necesarias y mantiene un registro claro para toda la cadena. |

## ✨ Características Arquitectónicas

- **Stack Moderno y Reactivo**: La combinación de **Django** con **HTMX** y **Tailwind CSS** permite crear interfaces de usuario ricas y dinámicas sin la complejidad de un framework JavaScript pesado. **Vite** gestiona el frontend, ofreciendo *hot-reloading* en desarrollo y un build optimizado para producción.
- **Componentes Reutilizables**: `django-components` se utiliza para encapsular la lógica y el renderizado del frontend, promoviendo un código más limpio y mantenible.
- **Despliegue Nativo en AWS**: El sistema está diseñado para **AWS App Runner**, utilizando **IAM Roles** para una gestión segura de permisos, **Secrets Manager** para las credenciales, **RDS (PostgreSQL)** para la base de datos y **S3 + CloudFront** para el almacenamiento y distribución de archivos estáticos.
- **Arquitectura de Datos Unificada**: Ambas aplicaciones comparten un modelo de datos basado en `UDN (Unidad de Negocio) → Sector`, donde los permisos se heredan automáticamente, simplificando drásticamente la administración.

## 👥 Roles del Sistema

El sistema define roles claros con responsabilidades específicas para garantizar un flujo de trabajo ordenado:

- **Usuario Final**: Empleados que crean solicitudes para sí mismos.
- **Técnico**: Especialistas de sistemas que resuelven incidencias y pueden presupuestar en `Payflow`.
- **Supervisor**: Líder de área que realiza la primera autorización de las solicitudes.
- **Gestor de Compras**: Rol central en `Payflow` que gestiona presupuestos, pagos y logística.
- **Manager**: Gerente de UDN o CEO, responsable de la autorización final de pagos.
- **Director**: Grupo con permisos especiales para actuar como segunda firma en autorizaciones críticas.

> Para un análisis técnico detallado del flujo más complejo, consulta el **[Manual de Workflow de Compras](/dev/purchase-workflow)**.

## 🛠️ Stack Tecnológico

| Categoría | Tecnología |
| :--- | :--- |
| **Backend** | Python 3.11, Django 5, Gunicorn |
| **Frontend** | Vite, Tailwind CSS v4, HTMX, django-components |
| **Base de Datos** | PostgreSQL (AWS RDS) |
| **Infraestructura** | AWS App Runner, S3, CloudFront, IAM, Secrets Manager |
| **Build Tools** | `uv` (para Python), `npm` (para Node.js) |

## 🚀 Desarrollo y Despliegue

### Entorno de Desarrollo Local

**1. Requisitos:**
   - Python 3.11+
   - Node.js 20+
   - `uv` (instalador de paquetes de Python)

**2. Instalación:**
   ```bash
   # 1. Crear y activar el entorno virtual
   uv venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate

   # 2. Instalar dependencias de Python y Node.js
   uv pip install -r requirements.txt
   npm install
   ```

**3. Ejecución:**
   El entorno de desarrollo requiere dos procesos en paralelo:

   ```bash
   # Terminal 1: Iniciar el servidor de desarrollo de Vite (Frontend)
   npm run dev
   ```

   ```bash
   # Terminal 2: Iniciar el servidor de Django (Backend)
   python manage.py runserver
   ```
   > 💡 **Tip para Windows:** El script `.\scripts\dev.ps1` automatiza el inicio de ambos servidores.

### Proceso de Build en AWS App Runner

El despliegue está optimizado para máxima velocidad a través de `apprunner.yaml`:

1.  **`build` (Backend)**: Instala `uv` y las dependencias de Python únicamente.
2.  **`runtime` (Ejecución)**: Ejecuta las migraciones de la base de datos, recolecta los archivos estáticos (`collectstatic`) y finalmente inicia el servidor Gunicorn para servir la aplicación.

> 🚀 **Optimización**: Los assets del frontend se construyen localmente antes del despliegue usando `./scripts/build-for-production.sh`, eliminando la necesidad de Node.js en el contenedor y reduciendo el tiempo de build en ~70%.

## 📚 Documentación del Proyecto

- **[TICKET_FLOW.md](./TICKET_FLOW.md)**: Visión general de la arquitectura y los flujos.
- **[TICKET_FLOW_PAYFLOW.md](./TICKET_FLOW_PAYFLOW.md)**: Documentación detallada del módulo de compras y pagos.
- **[FLUJO_DE_TICKETS.md](./FLUJO_DE_TICKETS.md)**: Guía de usuario simplificada para entender el funcionamiento general.
- **[Manual Técnico de Payflow](/dev/purchase-workflow)**: Análisis técnico interactivo del flujo de compras, disponible en el entorno de desarrollo.