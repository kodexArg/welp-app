#!/usr/bin/env python
"""
Puebla la DB de Payflow con flujos de tickets definidos en un archivo YAML.

Uso: uv run scripts/seed_payflow.py <ruta_del_yaml>

El script es idempotente: borra los tickets existentes con los mismos títulos
del YAML antes de volver a crearlos.

Cada entrada en el YAML es un mensaje. El script los agrupa por la clave 'ticket'.
- 'post_date' se usa para fijar la fecha histórica del mensaje (`reported_on`).
- Los adjuntos se buscan en el directorio 'scripts/examples/'.
"""
import os
import sys
import yaml
import logging
import django
from collections import defaultdict
from django.db import transaction
from django.conf import settings
from django.core.files import File
from argparse import ArgumentParser

# --- Configuración de Django ---
def setup_django():
    """Configura el entorno de Django para poder usar los modelos."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(project_root)
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    django.setup()

# --- Configuración del Logger ---
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# --- Constantes ---
ATTACHMENT_SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'examples')

def process_scenarios(grouped_scenarios):
    """Procesa los escenarios agrupados, eliminando y creando tickets."""
    from welp_payflow.models import Ticket

    ticket_titles = list(grouped_scenarios.keys())
    logger.info(f"Limpiando {len(ticket_titles)} ticket(s) existentes antes de la carga...")
    
    existing_tickets = Ticket.objects.filter(title__in=ticket_titles)
    deleted_count, _ = existing_tickets.delete()
    logger.info(f"  → {deleted_count} ticket(s) eliminados.")

    logger.info("\nIniciando carga de nuevos tickets...")
    for title, messages_data in grouped_scenarios.items():
        process_single_ticket(title, messages_data)

def process_single_ticket(title, messages_data):
    """Procesa y crea un único ticket y su flujo de mensajes."""
    from welp_payflow.models import UDN, Sector, AccountingCategory, Ticket

    logger.info(f"\nProcesando ticket: '{title}'")
    
    messages_data.sort(key=lambda m: m['post_date'])
    
    first_message_data = next((m for m in messages_data if m.get('status') == 'open'), None)
    if not first_message_data:
        logger.error(f"  ✗ No se encontró mensaje de apertura ('status: open') para '{title}'. Omitiendo.")
        return

    try:
        udn = UDN.objects.get(name=first_message_data['udn'])
        sector = Sector.objects.get(name=first_message_data['sector'])
        category = AccountingCategory.objects.get(name=first_message_data['category'])

        ticket = Ticket.objects.create(
            title=title,
            udn=udn,
            sector=sector,
            accounting_category=category,
            estimated_amount=first_message_data.get('estimated_amount')
        )
        logger.info(f"  ✓ Ticket creado con ID: {ticket.id}")
        
        for msg_data in messages_data:
            create_message_from_data(ticket, msg_data)

    except UDN.DoesNotExist:
        logger.error(f"  ✗ UDN '{first_message_data['udn']}' no encontrada. Omitiendo ticket '{title}'.")
    except Sector.DoesNotExist:
        logger.error(f"  ✗ Sector '{first_message_data['sector']}' no encontrado. Omitiendo ticket '{title}'.")
    except AccountingCategory.DoesNotExist:
        logger.error(f"  ✗ Categoría '{first_message_data['category']}' no encontrada. Omitiendo ticket '{title}'.")
    except Exception as e:
        logger.error(f"  ✗ Error inesperado al crear el ticket '{title}': {e}")


def create_message_from_data(ticket, msg_data):
    """Crea un objeto Message y sus adjuntos a partir de los datos del YAML."""
    from core.models import User
    from welp_payflow.models import Message, Attachment
    
    try:
        user = User.objects.get(username=msg_data['user'])
        
        message = Message.objects.create(
            ticket=ticket,
            user=user,
            status=msg_data['status'],
            body=msg_data.get('comment', ''),
            message_type='status',
            reported_on=msg_data['post_date']
        )
        logger.info(f"    ✓ Mensaje creado [Status: {message.status}, User: {user.username}]")

        for filename in msg_data.get('attachments', []):
            attachment_path = os.path.join(ATTACHMENT_SAMPLES_DIR, filename)
            if os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    django_file = File(f, name=filename)
                    Attachment.objects.create(message=message, file=django_file)
                    logger.info(f"      ✓ Adjunto '{filename}' asociado.")
            else:
                logger.warning(f"      ✗ Adjunto '{filename}' no encontrado en {ATTACHMENT_SAMPLES_DIR}. Omitido.")

    except User.DoesNotExist:
        logger.error(f"    ✗ Usuario '{msg_data['user']}' no encontrado. Omitiendo mensaje.")
    except Exception as e:
        logger.error(f"    ✗ Error inesperado al crear mensaje para {ticket.title}: {e}")

def main():
    """Función principal para ejecutar el script."""
    parser = ArgumentParser(description='Puebla la base de datos de Payflow desde un archivo YAML.')
    parser.add_argument('yaml_file', type=str, help='Ruta al archivo YAML de escenarios.')
    args = parser.parse_args()
    
    yaml_file_path = args.yaml_file
    if not os.path.exists(yaml_file_path):
        logger.error(f"El archivo '{yaml_file_path}' no existe.")
        sys.exit(1)

    # Cargar y agrupar escenarios
    with open(yaml_file_path, 'r', encoding='utf-8') as file:
        scenarios = yaml.safe_load(file)
    
    if not isinstance(scenarios, list):
        logger.error("El YAML debe contener una lista de mensajes.")
        sys.exit(1)

    grouped_scenarios = defaultdict(list)
    for message_data in scenarios:
        ticket_title = message_data.get('ticket')
        if not ticket_title:
            logger.warning("Omitiendo entrada sin clave 'ticket'.")
            continue
        grouped_scenarios[ticket_title].append(message_data)
    
    # Configurar Django
    setup_django()
    
    # Procesar todo dentro de una transacción
    try:
        with transaction.atomic():
            process_scenarios(grouped_scenarios)
    except Exception as e:
        logger.error(f"Error durante la transacción, se revirtieron los cambios: {e}")
        sys.exit(1)

    logger.info("\n✓ Proceso de seeding de Payflow completado exitosamente.")

if __name__ == "__main__":
    main() 