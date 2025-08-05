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
            logger.info("Sincronizando UDNs, Sectores y Categorías de Payflow...")

            udns_map = {}
            for udn_data in data.get('UDNs', []):
                udn, created = UDN.objects.update_or_create(
                    name=udn_data['name'],
                    defaults={'name': udn_data['name']}
                )
                udns_map[udn.name] = udn
                if created:
                    logger.info(f"  ✓ UDN creada: {udn.name}")

            sectors_map = {}
            for sector_data in data.get('Sectors', []):
                sector, created = Sector.objects.update_or_create(
                    name=sector_data['name'],
                    defaults={'name': sector_data['name']}
                )
                sectors_map[sector.name] = sector
                if created:
                    logger.info(f"  ✓ Sector creado: {sector.name}")
                
                # Sincronizar UDNs asociadas
                current_udns = {udn.name for udn in sector.udn.all()}
                target_udns = set(sector_data.get('udns', []))
                
                udns_to_add = [udns_map[name] for name in target_udns - current_udns if name in udns_map]
                if udns_to_add:
                    sector.udn.add(*udns_to_add)

            for category_data in data.get('AccountingCategories', []):
                category, created = AccountingCategory.objects.update_or_create(
                    name=category_data['name'],
                    defaults={
                        'name': category_data['name'],
                        'description': category_data.get('description', '')
                    }
                )
                if created:
                    logger.info(f"  ✓ Categoría creada: {category.name}")
                
                # Las categorías son globales para todos los sectores
                all_sectors = Sector.objects.all()
                category.sector.set(all_sectors)

            logger.info("\nSincronización de datos base completada.")
            logger.info(f"  • UDNs: {UDN.objects.count()} | Sectores: {Sector.objects.count()} | Categorías: {AccountingCategory.objects.count()}")

            # --- Sincronización de Usuarios y Roles ---
            logger.info("\nSincronizando usuarios y asignando roles...")
            udn_map_for_users = {udn.name: udn for udn in UDN.objects.all()}
            sector_map_for_users = {sector.name: sector for sector in Sector.objects.all()}
            
            # Limpiar roles existentes de usuarios del YAML para evitar duplicados
            usernames_in_yaml = {u['username'] for u in data.get('users', [])}
            Roles.objects.filter(user__username__in=usernames_in_yaml).delete()
            
            for user_data in data.get('users', []):
                create_user_and_assign_roles(user_data, udn_map_for_users, sector_map_for_users)

            logger.info(f"\n✓ {len(data.get('users', []))} usuarios procesados. Total de roles: {Roles.objects.count()}")

    except Exception as e:
        logger.error(f"\n✗ Error durante la sincronización de la base de datos: {str(e)}")
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
    elif isinstance(user_data.get('udns'), list):
        udns_to_process = [udn_map[name] for name in user_data['udns'] if name in udn_map]
    elif 'udn' in user_data:
        udn_name = user_data['udn']
        if udn_name in udn_map:
            udns_to_process = [udn_map[udn_name]]
    else:
        logger.warning(f"  ⚠️  Usuario '{username}' no tiene UDN asignada. Saltando.")
        return
    
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
                defaults={'role': role_type}
            )
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