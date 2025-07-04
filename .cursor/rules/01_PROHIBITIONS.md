---
description: Reglas de prohibición absoluta que fallan commits automáticamente
globs: ["**/*.py", "**/*.html", "**/*.js", "**/*.ts", "**/*.css", "requirements.txt", "package.json"]
alwaysApply: true
---

# Prohibitions - Reglas de Prohibición Absoluta

REGLA CRÍTICA: alwaysApply = true

# Prohibiciones de Código
- NUNCA comentar código innecesariamente. 
- NUNCA usar CSS inline con style="" o CSS embebido sin @apply
- NUNCA hardcodear credenciales, tokens o passwords en código
- NUNCA definir constantes en código. Usar variables de entorno exclusivamente

# Prohibiciones de Arquitectura
- NUNCA usar frameworks incompatibles fuera de Django 5 + Tailwind 4 + Vite + HTMX
- NUNCA agregar dependencias sin documentar justificación en requirements.txt y pyproject.toml

# Prohibiciones de Database
- NUNCA aplicar migraciones manualmente en producción
- NUNCA ejecutar python manage.py migrate directamente en servidores

# Prohibiciones de Archivos Críticos
- NUNCA editar settings.py sin autorización explícita del usuario
- NUNCA editar apprunner.yaml sin autorización explícita del usuario

# Referencias
- Django Security Best Practices: https://docs.djangoproject.com/en/5.0/topics/security/
- Tailwind CSS v4 Utilities: https://tailwindcss.com/blog/tailwindcss-v4 