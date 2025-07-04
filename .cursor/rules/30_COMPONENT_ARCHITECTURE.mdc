---
description: Estándares para template tags y componentes Django
globs: ["templates/components/**/*.html", "core/templatetags/*.py", "templates/**/*.html"]
alwaysApply: false
---

# Component Architecture - Templates y Components

# Estructura de Templates
- Directorio base: /templates en root del proyecto
- Configurado en TEMPLATES['DIRS'] = [BASE_DIR / 'templates']
- Estructura por aplicación: templates/app_name/template.html
- Componentes compartidos: templates/components/core/component.html
- Templates base: templates/core/base.html

# Estructura de Componentes
- Template tags van en core/templatetags/
- Django los encuentra automáticamente en esta ubicación
- Componentes comunes/públicos: templates/components/core/
- Componentes específicos: templates/components/{app_name}/
- Todos los componentes en templates/components/core/ son públicos y reutilizables

# Formato de Componente Obligatorio
- Regla crítica: Un componente = Un archivo .html únicamente
- HTML PRIMERO - Siempre en div con clase del nombre del componente
- CSS SEGUNDO - Solo si necesario, usar @apply con clases de frontend
- JAVASCRIPT ÚLTIMO - Solo si necesario

# Template Tag Pattern
- Cada componente debe tener su template tag correspondiente en core/templatetags/core_tags.py
- Usar @register.inclusion_tag para registrar componentes
- Parámetros con defaults para flexibilidad

# Uso en Templates
- Cargar template tags con {% load core_tags %}
- Usar componentes con sintaxis de template tag
- Pasar parámetros como argumentos del template tag

# Component Lifecycle
- Creación: Identificar necesidad de reutilización
- Desarrollo: HTML + CSS (@apply) + JS (DOMContentLoaded)
- Template Tag: Registrar como inclusion_tag
- Testing: Verificar reutilización en múltiples contextos

# Referencias
- Django Inclusion Tags: https://docs.djangoproject.com/en/5.0/howto/custom-template-tags/#inclusion-tags
- Component Architecture Patterns: https://web.dev/component-architecture/ 