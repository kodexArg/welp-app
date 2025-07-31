#!/usr/bin/env python
"""
Script para actualizar supervisores existentes y darles acceso a todos los sectores.

Este script busca todos los usuarios con rol 'supervisor' y les asigna acceso
a todos los sectores disponibles en sus UDNs correspondientes.

Uso: uv run scripts/update_supervisors.py
"""
import os
import sys
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

def update_supervisors():
    """Actualiza todos los supervisores para que tengan acceso a todos los sectores"""
    from welp_payflow.models import Roles, UDN, Sector
    from core.models import User
    
    logger.info("Iniciando actualización de supervisores...")
    
    # Obtener todos los roles de supervisor
    supervisor_roles = Roles.objects.filter(role='supervisor')
    
    if not supervisor_roles.exists():
        logger.info("No se encontraron supervisores en el sistema.")
        return
    
    # Agrupar por usuario y UDN
    supervisors_by_user_udn = {}
    for role in supervisor_roles:
        key = (role.user.id, role.udn.id)
        if key not in supervisors_by_user_udn:
            supervisors_by_user_udn[key] = {
                'user': role.user,
                'udn': role.udn,
                'existing_roles': []
            }
        supervisors_by_user_udn[key]['existing_roles'].append(role)
    
    total_updated = 0
    total_created = 0
    
    with transaction.atomic():
        for (user_id, udn_id), data in supervisors_by_user_udn.items():
            user = data['user']
            udn = data['udn']
            existing_roles = data['existing_roles']
            
            logger.info(f"\nProcesando supervisor: {user.first_name} {user.last_name} ({user.username})")
            logger.info(f"UDN: {udn.name}")
            
            # Obtener todos los sectores de esta UDN
            all_sectors_in_udn = list(udn.payflow_sectors.all())
            
            if not all_sectors_in_udn:
                logger.warning(f"  ⚠️  La UDN '{udn.name}' no tiene sectores asociados.")
                continue
            
            logger.info(f"  Sectores disponibles en {udn.name}: {[s.name for s in all_sectors_in_udn]}")
            
            # Sectores que ya tiene asignados
            existing_sectors = {role.sector for role in existing_roles}
            logger.info(f"  Sectores actuales: {[s.name for s in existing_sectors]}")
            
            # Sectores que necesita
            missing_sectors = set(all_sectors_in_udn) - existing_sectors
            
            if missing_sectors:
                logger.info(f"  Sectores a agregar: {[s.name for s in missing_sectors]}")
                
                # Crear roles para sectores faltantes
                for sector in missing_sectors:
                    role, created = Roles.objects.get_or_create(
                        user=user,
                        udn=udn,
                        sector=sector,
                        defaults={'role': 'supervisor'}
                    )
                    
                    if created:
                        logger.info(f"    ✓ Rol creado para sector: {sector.name}")
                        total_created += 1
                    else:
                        # Actualizar el rol si existe pero no es supervisor
                        if role.role != 'supervisor':
                            role.role = 'supervisor'
                            role.save()
                            logger.info(f"    ✓ Rol actualizado para sector: {sector.name}")
                            total_updated += 1
                        else:
                            logger.info(f"    → Rol ya existe para sector: {sector.name}")
            else:
                logger.info(f"  ✓ El supervisor ya tiene acceso a todos los sectores de {udn.name}")
    
    logger.info(f"\n✓ Actualización completada:")
    logger.info(f"  • Roles creados: {total_created}")
    logger.info(f"  • Roles actualizados: {total_updated}")
    logger.info(f"  • Total supervisores procesados: {len(supervisors_by_user_udn)}")

def main():
    """Función principal del script"""
    logger.info("Iniciando script de actualización de supervisores...")
    
    setup_django()
    update_supervisors()
    
    logger.info("\n✓ Script completado exitosamente.")

if __name__ == "__main__":
    main()