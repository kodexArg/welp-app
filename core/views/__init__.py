"""
Estructura modular de vistas para la aplicación core.

Organización por responsabilidad específica:

- home.py: Vistas principales (index, dashboard)
- auth.py: Autenticación y gestión de sesiones  
- health.py: Health checks y diagnósticos del sistema
- demos.py: Demostraciones y pruebas de funcionalidades
- dev.py: Herramientas de desarrollo y documentación técnica

Para usar las vistas, importe directamente desde el módulo específico:
    from .views.home import index, dashboard_view
    from .views.auth import login_view, logout_view
    
Esta estructura facilita el mantenimiento, testing y colaboración en equipo.
"""