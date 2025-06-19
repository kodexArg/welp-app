#!/usr/bin/env python
"""
Script para inicializar usuarios y roles con datos del archivo usuarios.yaml.
Uso: uv run init_users.py

cada usuario en 'usuarios.yaml' se ve así:

```
  - username: gabriel.cavedal
    nombre: Gabriel
    apellido: Cavedal
    email: gcavedal@gmail.com
    roles:
      - udn: "Km 1151"
        sector: "Full"
        permissions: "RCSAO"  # Lectura, Comentar, Solucionar, Autorizar, Abrir
      - udn: "Las Bóvedas"
        sector: "Full"
        permissions: "RCSAO"
      - udn: "Oficina Espejo"  # Tiene tanto solucionar como autorizar
        sector: "Administración"
        permissions: "RCSAO"
```



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
    """Carga los datos del archivo usuarios.yaml"""
    yaml_path = os.path.join(os.path.dirname(__file__), '..', 'excluded', 'usuarios.yaml')
    with open(yaml_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def parse_permissions(permission_string):
    """Convierte string de permisos (ej: 'RCSAO') a diccionario de booleanos"""
    return {
        'can_read': 'R' in permission_string,
        'can_comment': 'C' in permission_string,
        'can_solve': 'S' in permission_string,
        'can_authorize': 'A' in permission_string,
        'can_open': 'O' in permission_string,
        'can_close': 'X' in permission_string,
    }

def create_users_and_roles(data):
    """Crea usuarios y asigna roles según los datos del YAML"""
    from core.models import User
    from welp_desk.models import UDN, Sector, Roles
    
    try:
        with transaction.atomic():
            # Limpiar datos existentes de usuarios y roles
            logger.info("Limpiando usuarios y roles existentes...")
            Roles.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()  # Solo usuarios normales
            
            users_created = 0
            roles_created = 0
            
            # Crear mapas de UDN y Sectores para referencia rápida
            udns_map = {udn.name: udn for udn in UDN.objects.all()}
            sectors_map = {sector.name: sector for sector in Sector.objects.all()}
            
            logger.info("\nCreando usuarios y roles...")
            
            for user_data in data.get('usuarios', []):
                # Crear usuario
                username = user_data['username']
                user = User.objects.create_user(
                    username=username,
                    password=username,  # Contraseña inicial = username
                    first_name=user_data['nombre'],
                    last_name=user_data['apellido'],
                    email=user_data['email']
                )
                users_created += 1
                logger.info(f"  ✓ Usuario creado: {username} ({user_data['nombre']} {user_data['apellido']})")
                
                # Crear roles para este usuario
                for role_data in user_data.get('roles', []):
                    udn_name = role_data['udn']
                    sector_name = role_data['sector']
                    permissions_str = role_data['permissions']
                    
                    # Validar que UDN y Sector existan
                    if udn_name not in udns_map:
                        logger.warning(f"    ⚠️  UDN '{udn_name}' no encontrada, saltando rol")
                        continue
                    
                    if sector_name not in sectors_map:
                        logger.warning(f"    ⚠️  Sector '{sector_name}' no encontrado, saltando rol")
                        continue
                    
                    # Crear rol con permisos
                    permissions = parse_permissions(permissions_str)
                    role = Roles.objects.create(
                        user=user,
                        udn=udns_map[udn_name],
                        sector=sectors_map[sector_name],
                        **permissions
                    )
                    roles_created += 1
                    
                    perm_list = [k[4:].upper()[0] for k, v in permissions.items() if v]  # can_read -> R
                    logger.info(f"    → Rol: {udn_name} - {sector_name} [{'/'.join(perm_list)}]")
            
            # Resumen final
            logger.info("\nResumen de la inicialización de usuarios:")
            logger.info(f"  ✓ Usuarios creados: {users_created}")
            logger.info(f"  ✓ Roles creados: {roles_created}")
            logger.info(f"  ✓ Total usuarios en sistema: {User.objects.count()}")
            logger.info(f"  ✓ Total roles en sistema: {Roles.objects.count()}")
            
            # Verificar que UDNs y Sectores existen
            missing_udns = set()
            missing_sectors = set()
            for user_data in data.get('usuarios', []):
                for role_data in user_data.get('roles', []):
                    if role_data['udn'] not in udns_map:
                        missing_udns.add(role_data['udn'])
                    if role_data['sector'] not in sectors_map:
                        missing_sectors.add(role_data['sector'])
            
            if missing_udns:
                logger.warning(f"\n⚠️  UDNs no encontradas: {', '.join(missing_udns)}")
            if missing_sectors:
                logger.warning(f"⚠️  Sectores no encontrados: {', '.join(missing_sectors)}")

    except Exception as e:
        logger.error(f"\n✗ Error durante la creación de usuarios y roles: {str(e)}")
        raise

def main():
    """Función principal del script"""
    logger.info("Iniciando script de inicialización de usuarios...")
    
    # Configurar Django
    setup_django()
    
    # Cargar datos YAML y crear usuarios/roles
    data = load_yaml_data()
    create_users_and_roles(data)
    
    logger.info("\n✓ Inicialización de usuarios completada exitosamente.")
    logger.info("💡 Todos los usuarios tienen contraseña inicial = username")

if __name__ == "__main__":
    main()
