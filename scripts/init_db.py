#!/usr/bin/env python
"""
Script para inicializar la base de datos con datos del archivo YAML.
Uso: uv run init_db.py
"""

import os
import sys
import yaml
import django
import logging
from django.db import transaction

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def setup_django():
    """Configura Django para poder usar los modelos"""
    # Asegurarse que el script se ejecuta desde el directorio correcto
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(project_root)
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    django.setup()

def load_yaml_data():
    """Carga los datos del archivo YAML"""
    yaml_path = os.path.join(os.path.dirname(__file__), 'init_db.yaml')
    with open(yaml_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def populate_database(data):
    """Puebla la base de datos con los datos del YAML"""
    from welp_desk.models import UDN, Sector, IssueCategory, Issue

    try:
        with transaction.atomic():
            # Limpiar datos existentes
            logger.info("Limpiando datos existentes...")
            Issue.objects.all().delete()
            IssueCategory.objects.all().delete()
            Sector.objects.all().delete()
            UDN.objects.all().delete()

            # UDNs
            udns_map = {}
            logger.info("\nCreando UDNs...")
            for udn_data in data.get('UDNs', []):
                udn_name = udn_data['name']
                udn = UDN.objects.create(name=udn_name)
                udns_map[udn_name] = udn
                logger.info(f"  ✓ UDN creada: {udn_name}")

            # Sectores
            sectors_map = {}
            logger.info("\nCreando Sectores...")
            for sector_data in data.get('Sectors', []):
                sector_name = sector_data['name']
                sector = Sector.objects.create(name=sector_name)
                sectors_map[sector_name] = sector
                
                # Asociar UDNs al sector
                for udn_name in sector_data.get('udns', []):
                    sector.udn.add(udns_map[udn_name])
                logger.info(f"  ✓ Sector creado: {sector_name}")

            # Categorías de Incidencias
            categories_map = {}
            logger.info("\nCreando Categorías de Incidencias...")
            for category_data in data.get('IssueCategories', []):
                category_name = category_data['name']
                category = IssueCategory.objects.create(name=category_name)
                categories_map[category_name] = category
                
                # Asociar sectores a la categoría
                for sector_name in category_data.get('sectors', []):
                    category.sector.add(sectors_map[sector_name])
                logger.info(f"  ✓ Categoría creada: {category_name}")

            # Incidencias
            logger.info("\nCreando Incidencias...")
            for issue_data in data.get('Issues', []):
                Issue.objects.create(
                    name=issue_data['name'],
                    issue_category=categories_map[issue_data['issue_category']],
                    description=issue_data.get('description', ''),
                    display_name=issue_data.get('display_name', issue_data['name'])
                )

            # Resumen final
            logger.info("\nResumen de la inicialización:")
            logger.info(f"  ✓ UDNs creadas: {UDN.objects.count()}")
            logger.info(f"  ✓ Sectores creados: {Sector.objects.count()}")
            logger.info(f"  ✓ Categorías creadas: {IssueCategory.objects.count()}")
            logger.info(f"  ✓ Incidencias creadas: {Issue.objects.count()}")

    except Exception as e:
        logger.error(f"\n✗ Error durante la población de la base de datos: {str(e)}")
        raise

def main():
    """Función principal del script"""
    logger.info("Iniciando script de inicialización de base de datos...")
    
    # Configurar Django
    setup_django()
    
    # Cargar datos YAML y poblar base de datos
    data = load_yaml_data()
    populate_database(data)
    
    logger.info("\n✓ Inicialización de base de datos completada exitosamente.")

if __name__ == "__main__":
    main() 