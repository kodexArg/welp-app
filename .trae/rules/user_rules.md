---
description: Reglas TRAE del Usuario - Formato, Chat y Comportamiento
tags: ["User", "Communication", "Format", "Documentation", "Prohibitions"]
slug: user-rules
alwaysApply: true
---

# Reglas TRAE del Usuario

Reglas de formato, comunicación, documentación y prohibiciones para el desarrollo del proyecto Welp App.

## Documentación a consultar

### Framework Principal
- [Django 5.0+ Documentation](https://docs.djangoproject.com/en/5.0/)
  - [Models](https://docs.djangoproject.com/en/5.0/topics/db/models/)
  - [Views](https://docs.djangoproject.com/en/5.0/topics/http/views/)
  - [Templates](https://docs.djangoproject.com/en/5.0/topics/templates/)
  - [Forms](https://docs.djangoproject.com/en/5.0/topics/forms/)

### Frontend y Estilos
- [Tailwind CSS v4](https://tailwindcss.com/docs)
  - [Utility Classes](https://tailwindcss.com/docs/utility-first)
  - [Customization](https://tailwindcss.com/docs/configuration)
- [Vite Documentation](https://vitejs.dev/guide/)
- [HTMX Documentation](https://htmx.org/docs/)

### Herramientas de Desarrollo
- [uv Package Manager](https://docs.astral.sh/uv/)

### Infraestructura
- [AWS AppRunner](https://docs.aws.amazon.com/apprunner/)

## Comportamiento de la AI

### Metodología específica del proyecto
- **Componentes**: Reutilizar siempre los componentes existentes en `templates/core/components/` antes de crear nuevos
- **Datos iniciales**: Usar exclusivamente `scripts/init_payflow.yaml` para configurar UDNs, sectores y usuarios
- **Assets**: Respetar el flujo Vite → `static/dist/` → Django collectstatic

### Estilo de código
- **Python**: 
  - Seguir PEP 8 + type hints obligatorios
  - Docstrings muy breves de una sola frase SOLO SI el código es suficientemente original
  - **PROHIBIDO**: Escribir comentarios en el código en CUALQUIER archivo
- **Templates**: Usar componentes existentes antes de crear nuevos
- **CSS/Tailwind 4**: 
  - Solo Tailwind 4, usar layers apropiados (@layer base, components, utilities)
  - **PROHIBIDO**: Crear `tailwind.config.js` (obsoleto en Tailwind 4)
  - **PROHIBIDO**: CSS inline o frameworks diferentes a Tailwind 4
- **JavaScript**: Preferir HTMX sobre JavaScript vanilla

### Comunicación
- **Idioma**:
  - Funciones, clases y variables siempre en Inglés.
  - Responder en Español en el chat y documentación.
  - Usar inglés para términos precisos.
- **Formato**: Usar referencias de archivos con etiquetas `<mcfile>`, `<mcsymbol>`, `<mcfolder>` cuando sea apropiado
- **Explicaciones**: Ser conciso en las explicaciones

## Tareas obligatorias del usuario

- **Desarrollo**: SIEMPRE usar `scripts/dev.sh` para iniciar el entorno de desarrollo
- **Git**: Usar conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`)
- **README.md**: Mantener siempre actualizado con cambios del proyecto



## PROHIBICIONES para la AI

### 🚫 Comportamiento de desarrollo
- **NUNCA** sugerir iniciar servidores manualmente (siempre mencionar `scripts/dev.sh`)
- **NUNCA** proponer modificaciones a archivos críticos sin advertir al usuario
- **NUNCA** crear archivos fuera de la estructura establecida del proyecto
- **NUNCA** ignorar los patrones y convenciones existentes del proyecto

### 💻 Estilo de código
- **NUNCA** proponer JavaScript sin justificación (preferir HTMX)
- **NUNCA** dejar código comentado en las implementaciones
- **NUNCA** omitir type hints en código Python

### 🔒 Seguridad y buenas prácticas
- **NUNCA** hardcodear credenciales o secretos en el código
- **SIEMPRE** usar variables de entorno para configuración sensible

### ⚠️ Archivos críticos - CONSULTAR antes de modificar
- **project/settings.py**: Configuración principal de Django
- **apprunner.yaml**: Configuración de producción en AWS
- **scripts/init_payflow.yaml**: Datos iniciales del sistema
- **scripts/dev.sh** y **scripts/start.sh**: Scripts de ejecución principales

### 📁 Estructura y organización
- **SIEMPRE** reutilizar componentes existentes antes de crear nuevos
- **SIEMPRE** seguir la estructura de directorios establecida
- **SIEMPRE** usar las convenciones de naming del proyecto