#!/usr/bin/env python
"""Crea usuarios de ejemplo en PayFlow para pruebas locales.

Ejecutar con:
    uv run scripts/init_payflow_users.py

Asume que las UDN y sectores ya existen (ejecute primero init_payflow.py).
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

USERS_DATA = [
    {
        'username': 'pato.moro', 'first_name': 'Pato', 'last_name': 'Moro',
        'role': 'end_user', 'udn': 'KM 1151', 'sector': 'Administración'
    },
    {
        'username': 'vino.tes', 'first_name': 'Vino', 'last_name': 'Tes',
        'role': 'end_user', 'udn': 'KM 1151', 'sector': 'Operaciones'
    },
    {
        'username': 'coco.zen', 'first_name': 'Coco', 'last_name': 'Zen',
        'role': 'end_user', 'udn': 'Las Bóvedas', 'sector': 'Administración'
    },
    {
        'username': 'lili.per', 'first_name': 'Lili', 'last_name': 'Per',
        'role': 'end_user', 'udn': 'Las Bóvedas', 'sector': 'Operaciones'
    },
    {
        'username': 'pepe.kid', 'first_name': 'Pepe', 'last_name': 'Kid',
        'role': 'end_user', 'udn': 'Parador', 'sector': 'Parrilla'
    },
    {
        'username': 'pili.box', 'first_name': 'Pili', 'last_name': 'Box',
        'role': 'end_user', 'udn': 'KCBD', 'sector': 'Operaciones'
    },
    {
        'username': 'yoyo.vis', 'first_name': 'Yoyo', 'last_name': 'Vis',
        'role': 'end_user', 'udn': 'Espejo', 'sector': 'Sistemas'
    },
    {
        'username': 'colo.yin', 'first_name': 'Colo', 'last_name': 'Yin',
        'role': 'end_user', 'udn': 'VW', 'sector': 'Campo'
    },
    {
        'username': 'luna.mani', 'first_name': 'Luna', 'last_name': 'Mani',
        'role': 'technician', 'udn': 'KM 1151', 'sector': 'Administración'
    },
    {
        'username': 'tito.ban', 'first_name': 'Tito', 'last_name': 'Ban',
        'role': 'technician', 'udn': 'KM 1151', 'sector': 'Operaciones'
    },
    {
        'username': 'dani.tux', 'first_name': 'Dani', 'last_name': 'Tux',
        'role': 'technician', 'udn': 'Las Bóvedas', 'sector': 'Operaciones'
    },
    {
        'username': 'riko.caz', 'first_name': 'Riko', 'last_name': 'Caz',
        'role': 'technician', 'udn': 'Parador', 'sector': 'Mantenimiento'
    },
    {
        'username': 'riki.lux', 'first_name': 'Riki', 'last_name': 'Lux',
        'role': 'supervisor', 'udn': 'KM 1151', 'sector': 'Administración'
    },
    {
        'username': 'lola.pox', 'first_name': 'Lola', 'last_name': 'Pox',
        'role': 'supervisor', 'udn': 'KM 1151', 'sector': 'Operaciones'
    },
    {
        'username': 'mimo.san', 'first_name': 'Mimo', 'last_name': 'San',
        'role': 'supervisor', 'udn': 'Las Bóvedas', 'sector': 'Administración'
    },
    {
        'username': 'nana.hup', 'first_name': 'Nana', 'last_name': 'Hup',
        'role': 'supervisor', 'udn': 'Parador', 'sector': 'Mantenimiento'
    },
    {
        'username': 'teo.mor', 'first_name': 'Teo', 'last_name': 'Mor',
        'role': 'manager', 'udn': 'KM 1151', 'sector': None
    },
    {
        'username': 'jupi.vec', 'first_name': 'Jupi', 'last_name': 'Vec',
        'role': 'manager', 'udn': 'Las Bóvedas', 'sector': None
    },
    {
        'username': 'melo.tux', 'first_name': 'Melo', 'last_name': 'Tux',
        'role': 'manager', 'udn': 'Espejo', 'sector': None
    },
    {
        'username': 'natalia.cobucci', 'first_name': 'Natalia', 'last_name': 'Cobucci',
        'role': 'purchase_manager', 'udn': None, 'sector': None
    },
]


def setup_django():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    django.setup()


def create_users():
    from core.models import User
    from welp_payflow.models import UDN, Sector, Roles

    with transaction.atomic():
        logger.info("Borrando usuarios de PayFlow anteriores...")
        Roles.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        for data in USERS_DATA:
            user = User.objects.create_user(
                username=data['username'],
                password=data['username'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=f"{data['username']}@example.com",
            )

            udn = UDN.objects.get(name=data['udn']) if data['udn'] else None
            sector = Sector.objects.get(name=data['sector']) if data['sector'] else None

            role = Roles(user=user, udn=udn, sector=sector)
            role.set_permissions_from_role_type(data['role'])
            role.save()
            logger.info(f"  ✓ Creado {user.username} como {data['role']}")

        logger.info(f"Total de usuarios creados: {len(USERS_DATA)}")


def main():
    logger.info("Inicializando usuarios de ejemplo para PayFlow...")
    setup_django()
    create_users()
    logger.info("✓ Usuarios de ejemplo listos. Contraseña= username")


if __name__ == '__main__':
    main()
