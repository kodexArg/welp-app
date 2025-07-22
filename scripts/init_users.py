#!/usr/bin/env python
"""
Script para inicializar usuarios y roles de welp_payflow desde init_payflow.yaml.

Este script crea usuarios y les asigna roles explícitos basándose en la configuración
del archivo YAML. Requiere que las UDNs, Sectores y Categorías ya estén creados.

Uso: uv run scripts/init_users.py
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
    if not os.path.exists(yaml_path):
        logger.error(f"Archivo {yaml_path} no encontrado")
        sys.exit(1)
    
    with open(yaml_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def verify_prerequisites():
    """Verifica que las UDNs, Sectores y Categorías existan en la base de datos"""
    from welp_payflow.models import UDN, Sector, AccountingCategory
    
    udn_count = UDN.objects.count()
    sector_count = Sector.objects.count()
    category_count = AccountingCategory.objects.count()
    
    if udn_count == 0:
        logger.error("No se encontraron UDNs en la base de datos. Ejecute init_app.py primero.")
        sys.exit(1)
    
    if sector_count == 0:
        logger.error("No se encontraron Sectores en la base de datos. Ejecute init_app.py primero.")
        sys.exit(1)
    
    if category_count == 0:
        logger.error("No se encontraron Categorías Contables en la base de datos. Ejecute init_app.py primero.")
        sys.exit(1)
    
    logger.info(f"✓ Prerrequisitos verificados: {udn_count} UDNs, {sector_count} Sectores, {category_count} Categorías")

def create_users_and_roles(data):
    """Crea usuarios y les asigna roles según los datos del YAML"""
    from welp_payflow.models import UDN, Sector, Roles
    from core.models import User

    users_data = data.get('users', [])
    if not users_data:
        logger.warning("No se encontraron usuarios en el archivo YAML")
        return

    # Crear mapas de UDNs y Sectores para búsqueda rápida
    udn_map = {udn.name: udn for udn in UDN.objects.all()}
    sector_map = {sector.name: sector for sector in Sector.objects.all()}

    try:
        with transaction.atomic():
            logger.info("\nLimpiando roles existentes...")
            Roles.objects.all().delete()
            
            # Borrar solo los usuarios que están en el YAML para no afectar a superusuarios
            usernames_in_yaml = {u['username'] for u in users_data}
            deleted_users = User.objects.filter(username__in=usernames_in_yaml, is_superuser=False)
            deleted_count = deleted_users.count()
            deleted_users.delete()
            
            if deleted_count > 0:
                logger.info(f"✓ {deleted_count} usuarios de PayFlow anteriores eliminados.")

            logger.info(f"\nCreando {len(users_data)} usuarios y asignando roles...")
            
            created_users = 0
            updated_users = 0
            total_roles = 0
            
            for user_data in users_data:
                user_created, roles_created = create_user_and_assign_roles(user_data, udn_map, sector_map)
                if user_created:
                    created_users += 1
                else:
                    updated_users += 1
                total_roles += roles_created

            logger.info("\n" + "="*60)
            logger.info("RESUMEN DE CREACIÓN DE USUARIOS Y ROLES")
            logger.info("="*60)
            logger.info(f"✓ Usuarios creados: {created_users}")
            logger.info(f"✓ Usuarios actualizados: {updated_users}")
            logger.info(f"✓ Total de roles asignados: {total_roles}")
            logger.info(f"✓ Usuarios procesados del YAML: {len(users_data)}")
            
            # Mostrar resumen por tipo de rol
            role_summary = {}
            for role in Roles.objects.all():
                role_type = role.role
                if role_type not in role_summary:
                    role_summary[role_type] = 0
                role_summary[role_type] += 1
            
            logger.info("\nDistribución de roles:")
            for role_type, count in sorted(role_summary.items()):
                logger.info(f"  • {role_type}: {count} asignaciones")

    except Exception as e:
        logger.error(f"\n✗ Error durante la creación de usuarios: {str(e)}")
        raise

def create_user_and_assign_roles(user_data, udn_map, sector_map):
    """Crea un usuario y le asigna roles según los datos"""
    from core.models import User
    from welp_payflow.models import Roles
    
    username = user_data['username']
    
    # Crear o actualizar usuario
    user, user_created = User.objects.update_or_create(
        username=username,
        defaults={
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'email': f"{username}@example.com",
        }
    )
    
    if user_created:
        user.set_password(username)  # Contraseña inicial = username
        user.save()
        logger.info(f"  ✓ Usuario creado: {username}")
    else:
        logger.info(f"  → Usuario actualizado: {username}")

    # Determinar UDNs a procesar
    role_type = user_data['role']
    udns_to_process = []
    
    if user_data.get('udns') == 'all':
        udns_to_process = list(udn_map.values())
        logger.info(f"    • Asignando rol '{role_type}' a todas las UDNs")
    elif isinstance(user_data.get('udns'), list):
        udns_to_process = [udn_map[name] for name in user_data['udns'] if name in udn_map]
        logger.info(f"    • Asignando rol '{role_type}' a UDNs específicas: {user_data['udns']}")
    elif 'udn' in user_data:
        udn_name = user_data['udn']
        if udn_name in udn_map:
            udns_to_process = [udn_map[udn_name]]
            logger.info(f"    • Asignando rol '{role_type}' a UDN: {udn_name}")
    else:
        logger.warning(f"  ⚠️  Usuario '{username}' no tiene UDN asignada. Saltando.")
        return user_created, 0
    
    # Determinar sector específico (si aplica)
    specific_sector = sector_map.get(user_data.get('sector'))
    
    roles_created = 0
    
    # Crear roles para cada UDN
    for udn in udns_to_process:
        sectors_in_udn = list(udn.payflow_sectors.all())
        sectors_to_assign = []
        
        if specific_sector:
            # Usuario con sector específico
            if specific_sector in sectors_in_udn:
                sectors_to_assign = [specific_sector]
            else:
                logger.warning(f"    ⚠️  Sector '{specific_sector.name}' no está asociado a la UDN '{udn.name}' para '{username}'. No se asignará rol.")
                continue
        else:
            # Usuario con acceso a todos los sectores de la UDN
            sectors_to_assign = sectors_in_udn
            
        # Crear rol para cada sector
        for sector in sectors_to_assign:
            role, role_created = Roles.objects.update_or_create(
                user=user,
                udn=udn,
                sector=sector,
                defaults={'role': role_type}
            )
            
            if role_created:
                log_msg = f"    ✓ Rol '{role_type}' asignado en {udn.name}/{sector.name}"
                roles_created += 1
            else:
                log_msg = f"    → Rol '{role_type}' actualizado en {udn.name}/{sector.name}"
            
            logger.info(log_msg)
    
    return user_created, roles_created

def main():
    """Función principal del script"""
    logger.info("Iniciando script de inicialización de usuarios y roles de Payflow...")
    
    setup_django()
    verify_prerequisites()
    
    data = load_yaml_data()
    create_users_and_roles(data)
    
    logger.info("\n✓ Inicialización de usuarios y roles completada exitosamente.")
    logger.info("💡 Todos los usuarios tienen contraseña inicial = username")
    logger.info("💡 Para crear la estructura de UDNs/Sectores/Categorías, ejecute: uv run scripts/init_app.py")

if __name__ == "__main__":
    main() 