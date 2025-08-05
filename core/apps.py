from django.apps import AppConfig
import importlib
import os
from pathlib import Path


class CoreConfig(AppConfig):
    """Configuración de la aplicación core"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """Inicialización de la aplicación y carga de componentes"""
        components_dir = Path(__file__).parent.parent / "components" / "core"
        if components_dir.exists():
            for component_dir in components_dir.iterdir():
                if component_dir.is_dir() and not component_dir.name.startswith('_'):
                    py_file = component_dir / f"{component_dir.name}.py"
                    if py_file.exists():
                        module_path = f"components.core.{component_dir.name}.{component_dir.name}"
                        try:
                            importlib.import_module(module_path)
                        except ImportError:
                            pass
