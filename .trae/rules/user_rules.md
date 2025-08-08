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
  - [Installation](https://tailwindcss.com/docs/installation)
  - [Utility Classes](https://tailwindcss.com/docs/utility-first)
  - [Customization](https://tailwindcss.com/docs/configuration)
- [Vite Documentation](https://vitejs.dev/guide/)
- [HTMX Documentation](https://htmx.org/docs/)

### Herramientas de Desarrollo
- [uv Package Manager](https://docs.astral.sh/uv/)
- [pytest](https://docs.pytest.org/)
- [pytest-django](https://pytest-django.readthedocs.io/)

### Infraestructura
- [AWS AppRunner](https://docs.aws.amazon.com/apprunner/)

## Comportamiento de la AI

### Metodología de trabajo
- **Análisis**: Siempre revisar el contexto completo antes de hacer cambios
- **Implementación**: Seguir las estructuras y patrones existentes del proyecto
- **Validación**: Verificar que los cambios no rompan funcionalidades existentes
- **Documentación**: Actualizar documentación relevante cuando sea necesario

### Estilo de código
- **Python**: Seguir PEP 8 + type hints obligatorios
- **Templates**: Usar componentes existentes antes de crear nuevos
- **CSS**: Solo Tailwind 4, usar layers apropiados (@layer base, components, utilities)
- **JavaScript**: Preferir HTMX sobre JavaScript vanilla

### Comunicación
- **Idioma**: Responder en el idioma del usuario (español por defecto)
- **Formato**: Usar referencias de archivos con formato XML cuando sea apropiado
- **Explicaciones**: Ser conciso pero completo en las explicaciones

## Tareas obligatorias del usuario

- **Desarrollo**: SIEMPRE usar `scripts/dev.sh` para iniciar el entorno de desarrollo
- **Testing**: Escribir tests con pytest, mantener coverage > 80%
- **Git**: Usar conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`)
- **README.md**: Mantener siempre actualizado con cambios del proyecto



## PROHIBICIONES para la AI

### 🚫 Comportamiento de desarrollo
- **NUNCA** sugerir iniciar servidores manualmente (siempre mencionar `scripts/dev.sh`)
- **NUNCA** proponer modificaciones a archivos críticos sin advertir al usuario
- **NUNCA** crear archivos fuera de la estructura establecida del proyecto
- **NUNCA** ignorar los patrones y convenciones existentes del proyecto

### 💻 Estilo de código
- **NUNCA** usar CSS inline o frameworks diferentes a Tailwind 4
- **NUNCA** proponer JavaScript sin justificación (preferir HTMX)
- **NUNCA** dejar código comentado en las implementaciones
- **NUNCA** omitir type hints en código Python

### 🔒 Seguridad y buenas prácticas
- **NUNCA** hardcodear credenciales o secretos en el código
- **NUNCA** sugerir commitear archivos sensibles (.env, keys)
- **SIEMPRE** usar variables de entorno para configuración sensible
- **SIEMPRE** validar inputs y sanitizar datos

### ⚠️ Archivos críticos - CONSULTAR antes de modificar
- **project/settings.py**: Configuración principal de Django
- **apprunner.yaml**: Configuración de producción en AWS
- **scripts/init_payflow.yaml**: Datos iniciales del sistema
- **scripts/dev.sh** y **scripts/start.sh**: Scripts de ejecución principales

### 📁 Estructura y organización
- **SIEMPRE** reutilizar componentes existentes antes de crear nuevos
- **SIEMPRE** seguir la estructura de directorios establecida
- **SIEMPRE** usar las convenciones de naming del proyecto