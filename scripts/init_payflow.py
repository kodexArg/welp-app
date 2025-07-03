#!/usr/bin/env python
"""
Script para inicializar la base de datos de welp_payflow con datos del archivo YAML.
Uso: uv run init_payflow.py
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
    yaml_path = os.path.join(os.path.dirname(__file__), 'init_payflow.yaml')
    with open(yaml_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def populate_database(data):
    """Puebla la base de datos con los datos del YAML"""
    from welp_payflow.models import UDN, Sector, AccountingCategory

    try:
        with transaction.atomic():
            # Limpiar datos existentes
            logger.info("Limpiando datos existentes de welp_payflow...")
            AccountingCategory.objects.all().delete()
            Sector.objects.all().delete()
            UDN.objects.all().delete()

            # UDNs
            udns_map = {}
            logger.info("\nCreando UDNs de Payflow...")
            for udn_data in data.get('UDNs', []):
                udn_name = udn_data['name']
                udn = UDN.objects.create(name=udn_name)
                udns_map[udn_name] = udn
                logger.info(f"  ✓ UDN creada: {udn_name}")

            # Sectores
            sectors_map = {}
            logger.info("\nCreando Sectores de Payflow...")
            for sector_data in data.get('Sectors', []):
                sector_name = sector_data['name']
                sector = Sector.objects.create(name=sector_name)
                sectors_map[sector_name] = sector
                
                # Asociar UDNs al sector
                for udn_name in sector_data.get('udns', []):
                    if udn_name in udns_map:
                        sector.udn.add(udns_map[udn_name])
                    else:
                        logger.warning(f"    ⚠️  UDN '{udn_name}' no encontrada para sector '{sector_name}'")
                logger.info(f"  ✓ Sector creado: {sector_name}")

            # Categorías Contables
            logger.info("\nCreando Categorías Contables...")
            for category_data in data.get('AccountingCategories', []):
                category_name = category_data['name']
                category_description = category_data.get('description', '')
                category = AccountingCategory.objects.create(
                    name=category_name,
                    description=category_description
                )
                
                # Hacer que todas las categorías estén disponibles para todos los sectores
                for sector in sectors_map.values():
                    category.sector.add(sector)
                
                logger.info(f"  ✓ Categoría creada: {category_name} (disponible para todos los sectores)")
                if 'description' in category_data:
                    logger.info(f"    {category_data['description']}")

            # Resumen final
            logger.info("\nResumen de la inicialización de Payflow:")
            logger.info(f"  ✓ UDNs creadas: {UDN.objects.count()}")
            logger.info(f"  ✓ Sectores creados: {Sector.objects.count()}")
            logger.info(f"  ✓ Categorías Contables creadas: {AccountingCategory.objects.count()}")

            # Mostrar relaciones
            logger.info("\nResumen de relaciones:")
            logger.info("UDNs por Sector:")
            for sector in Sector.objects.all():
                udn_names = [udn.name for udn in sector.udn.all()]
                logger.info(f"  • {sector.name}: {', '.join(udn_names)}")
            
            logger.info(f"\nCategorías Contables:")
            logger.info(f"  • Todas las {AccountingCategory.objects.count()} categorías están disponibles para todos los {Sector.objects.count()} sectores")

    except Exception as e:
        logger.error(f"\n✗ Error durante la población de la base de datos: {str(e)}")
        raise

def main():
    """Función principal del script"""
    logger.info("Iniciando script de inicialización de base de datos Payflow...")
    
    # Configurar Django
    setup_django()
    
    # Cargar datos YAML y poblar base de datos
    data = load_yaml_data()
    populate_database(data)
    
    logger.info("\n✓ Inicialización de base de datos Payflow completada exitosamente.")

if __name__ == "__main__":
    main() 