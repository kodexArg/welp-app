#!/usr/bin/env python
"""
Script para inicializar la base de datos de welp_payflow con UDNs, Sectores,
Categorías Contables, Usuarios y Roles desde init_payflow.yaml.

Uso: uv run scripts/init_payflow.py
"""
import os
import sys
import yaml
import django
import logging
from django.db import transaction

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def setup_django():
    """Configura Django para poder usar los modelos"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(project_root)
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    django.setup()

def load_yaml_data():
    """Carga los datos del archivo YAML"""
    yaml_path = os.path.join(os.path.dirname(__file__), 'init_payflow.yaml')
    with open(yaml_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def populate_database(data):
    """Puebla la base de datos con los datos del YAML"""
    from welp_payflow.models import UDN, Sector, AccountingCategory, Roles
    from core.models import User

    try:
        with transaction.atomic():
            logger.info("Limpiando datos existentes de welp_payflow...")
            Roles.objects.all().delete()
            AccountingCategory.objects.all().delete()
            Sector.objects.all().delete()
            UDN.objects.all().delete()
            
            # Borrar solo los usuarios que están en el YAML para no afectar a superusuarios
            usernames_in_yaml = {u['username'] for u in data.get('users', [])}
            User.objects.filter(username__in=usernames_in_yaml, is_superuser=False).delete()
            logger.info("Usuarios de PayFlow anteriores borrados.")

            udns_map = {}
            logger.info("\nCreando UDNs de Payflow...")
            for udn_data in data.get('UDNs', []):
                udn_name = udn_data['name']
                udn = UDN.objects.create(name=udn_name)
                udns_map[udn_name] = udn
                logger.info(f"  ✓ UDN creada: {udn_name}")

            sectors_map = {}
            logger.info("\nCreando Sectores de Payflow...")
            for sector_data in data.get('Sectors', []):
                sector_name = sector_data['name']
                sector = Sector.objects.create(name=sector_name)
                sectors_map[sector_name] = sector
                
                for udn_name in sector_data.get('udns', []):
                    if udn_name in udns_map:
                        sector.udn.add(udns_map[udn_name])
                    else:
                        logger.warning(f"    ⚠️  UDN '{udn_name}' no encontrada para sector '{sector_name}'")
                logger.info(f"  ✓ Sector creado: {sector_name}")

            logger.info("\nCreando Categorías Contables...")
            for category_data in data.get('AccountingCategories', []):
                category_name = category_data['name']
                category_description = category_data.get('description', '')
                category = AccountingCategory.objects.create(
                    name=category_name,
                    description=category_description
                )
                
                for sector in sectors_map.values():
                    category.sector.add(sector)
                
                logger.info(f"  ✓ Categoría creada: {category_name} (disponible para todos los sectores)")
                if 'description' in category_data:
                    logger.info(f"    {category_data['description']}")

            logger.info("\nResumen de la inicialización de Payflow:")
            logger.info(f"  ✓ UDNs creadas: {UDN.objects.count()}")
            logger.info(f"  ✓ Sectores creados: {Sector.objects.count()}")
            logger.info(f"  ✓ Categorías Contables creadas: {AccountingCategory.objects.count()}")

            logger.info("\nResumen de relaciones:")
            logger.info("UDNs por Sector:")
            for sector in Sector.objects.all():
                udn_names = [udn.name for udn in sector.udn.all()]
                logger.info(f"  • {sector.name}: {', '.join(udn_names)}")
            
            logger.info(f"\nCategorías Contables:")
            logger.info(f"  • Todas las {AccountingCategory.objects.count()} categorías están disponibles para todos los {Sector.objects.count()} sectores")
            
            # --- Creación de Usuarios y Roles ---
            logger.info("\nCreando usuarios y asignando roles...")
            udn_map_for_users = {udn.name: udn for udn in UDN.objects.all()}
            sector_map_for_users = {sector.name: sector for sector in Sector.objects.all()}
            
            for user_data in data.get('users', []):
                create_user_and_assign_roles(user_data, udn_map_for_users, sector_map_for_users)

            logger.info("\nResumen de Usuarios y Roles:")
            logger.info(f"  ✓ Usuarios en YAML procesados: {len(data.get('users', []))}")
            logger.info(f"  ✓ Total de roles creados: {Roles.objects.count()}")

    except Exception as e:
        logger.error(f"\n✗ Error durante la población de la base de datos: {str(e)}")
        raise

def create_user_and_assign_roles(user_data, udn_map, sector_map):
    """Crea un usuario y le asigna roles según los datos."""
    from core.models import User
    from welp_payflow.models import Roles
    
    username = user_data['username']
    
    user, created = User.objects.update_or_create(
        username=username,
        defaults={
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'email': f"{username}@example.com",
        }
    )
    if created:
        user.set_password(username)
        user.save()
        logger.info(f"  ✓ Usuario creado: {username}")
    else:
        logger.info(f"  → Usuario actualizado: {username}")

    role_type = user_data['role']
    udns_to_process = []
    
    if user_data.get('udns') == 'all':
        udns_to_process = list(udn_map.values())
    elif 'udns' in user_data:
        udns_to_process = [udn_map[name] for name in user_data['udns'] if name in udn_map]
    elif 'udn' in user_data:
        udn_name = user_data['udn']
        if udn_name in udn_map:
            udns_to_process = [udn_map[udn_name]]
    
    specific_sector = sector_map.get(user_data.get('sector'))

    for udn in udns_to_process:
        sectors_in_udn = [s for s in udn.payflow_sectors.all()]
        sectors_to_assign = []
        
        if specific_sector:
            if specific_sector in sectors_in_udn:
                sectors_to_assign = [specific_sector]
            else:
                logger.warning(f"    ⚠️  Sector '{specific_sector.name}' no está asociado a la UDN '{udn.name}' para '{user.username}'. No se asignará rol.")
        else:
            sectors_to_assign = sectors_in_udn
            
        for sector in sectors_to_assign:
            role, r_created = Roles.objects.update_or_create(
                user=user,
                udn=udn,
                sector=sector,
            )
            role.set_permissions_from_role_type(role_type)
            role.save()
            log_msg = f"    ✓ Rol '{role_type}' asignado en {udn.name}/{sector.name}"
            if not r_created:
                log_msg = f"    → Rol '{role_type}' actualizado en {udn.name}/{sector.name}"
            logger.info(log_msg)

def main():
    """Función principal del script"""
    logger.info("Iniciando script de inicialización de base de datos Payflow...")
    
    setup_django()
    
    data = load_yaml_data()
    populate_database(data)
    
    logger.info("\n✓ Inicialización de base de datos Payflow completada exitosamente.")
    logger.info("💡 Todos los usuarios tienen contraseña inicial = username")

if __name__ == "__main__":
    main() 