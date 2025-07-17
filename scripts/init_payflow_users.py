#!/usr/bin/env python
"""Crea usuarios de ejemplo en PayFlow para pruebas locales.

Ejecutar con:
    uv run scripts/init_payflow_users.py

Asume que las UDN y sectores ya existen (ejecute primero init_payflow.py).
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
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    django.setup()

def load_user_data():
    """Carga los datos de usuarios desde el archivo YAML."""
    yaml_path = os.path.join(os.path.dirname(__file__), 'payflow_users.yaml')
    with open(yaml_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file).get('users', [])

def create_or_update_user(user_data):
    """Crea o actualiza un usuario. Devuelve el objeto User y si fue creado."""
    from core.models import User
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
        
    return user, created

def assign_roles(user, user_data, udn_map, sector_map):
    """Asigna roles a un usuario basándose en los datos del YAML."""
    from welp_payflow.models import Roles
    
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
            # Roles como 'manager' o globales, asignan todos los sectores de la UDN
            sectors_to_assign = sectors_in_udn
            
        for sector in sectors_to_assign:
            role, created = Roles.objects.update_or_create(
                user=user,
                udn=udn,
                sector=sector,
            )
            role.set_permissions_from_role_type(role_type)
            role.save()
            log_msg = f"    ✓ Rol '{role_type}' asignado en {udn.name}/{sector.name}"
            if not created:
                log_msg = f"    → Rol '{role_type}' actualizado en {udn.name}/{sector.name}"
            logger.info(log_msg)

def create_users_and_roles():
    """Función principal para crear usuarios y asignar roles."""
    from welp_payflow.models import UDN, Sector, Roles
    from core.models import User

    users_data = load_user_data()
    
    try:
        with transaction.atomic():
            logger.info("Borrando roles de PayFlow anteriores...")
            Roles.objects.all().delete()
            
            # Borrar solo los usuarios que están en el YAML para no afectar a superusuarios
            usernames_in_yaml = {data['username'] for data in users_data}
            User.objects.filter(username__in=usernames_in_yaml, is_superuser=False).delete()
            logger.info("Usuarios de PayFlow anteriores borrados.")

            udn_map = {udn.name: udn for udn in UDN.objects.all()}
            sector_map = {sector.name: sector for sector in Sector.objects.all()}
            
            created_count = 0
            for user_data in users_data:
                user, created = create_or_update_user(user_data)
                if created:
                    created_count += 1
                assign_roles(user, user_data, udn_map, sector_map)

            logger.info(f"\nResumen:")
            logger.info(f"  ✓ {created_count} usuarios nuevos creados.")
            logger.info(f"  → {len(users_data) - created_count} usuarios existentes actualizados.")
            logger.info(f"  ✓ Roles asignados: {Roles.objects.count()}")

    except Exception as e:
        logger.error(f"\n✗ Error durante la creación de usuarios y roles: {e}")
        raise

def main():
    """Punto de entrada del script."""
    logger.info("Iniciando script de creación de usuarios para PayFlow...")
    setup_django()
    create_users_and_roles()
    logger.info("\n✓ Creación de usuarios de PayFlow completada. Contraseña = username")

if __name__ == '__main__':
    main()
