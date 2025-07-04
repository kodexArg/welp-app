---
description: Estándares para documentación automática en welp-app
globs: ["README.md", "docs/**/*", "templates/core/home.html", "**/*.py", "**/*.html"]
alwaysApply: true
---

# Documentation - Documentation Standards

# Automatic README Maintenance
Cursor DEBE actualizar README.md y templates/core/home.html INMEDIATAMENTE cuando detecte:

# Cambios en Configuración
- apprunner.yaml modificado: actualizar Integración AWS y Orden de Implementación
- requirements.txt modificado: actualizar Dependencias y Notas técnicas
- settings.py modificado: actualizar Configuración y Características
- package.json modificado: actualizar Frontend Dependencies

# Cambios en Estructura
- Nuevos archivos creados: actualizar Orden de Implementación
- Aplicaciones agregadas: actualizar Características de la Aplicación
- URLs modificadas: actualizar Estructura de API
- Nuevos templates: actualizar UI Components

# Cambios en Funcionalidad
- Nuevas vistas implementadas: marcar como [x] en Orden de Implementación
- Modelos modificados: actualizar Características de la Aplicación
- Templates creados: actualizar estado de completitud
- Components agregados: actualizar Sistema de Componentes

# Protocolo de Actualización
- PASO 1: Identificar archivo modificado, determinar sección que necesita cambios, evaluar criticidad
- PASO 2: Determinar qué secciones específicas necesitan cambios
- PASO 3: Mantener secciones críticas: Estado de Tareas, Integración AWS, Características Técnicas

# Code Documentation Obligatorio
- Docstrings Python en español: función, argumentos, retorno, excepciones documentadas
- Template documentation: componente, descripción, parámetros documentados en comentarios HTML
- API documentation: usar drf_spectacular.utils.extend_schema para endpoints

# Referencias
- ADR Guidelines: https://adr.github.io/
- Django Documentation Best Practices: https://docs.djangoproject.com/en/5.0/internals/contributing/writing-documentation/ 