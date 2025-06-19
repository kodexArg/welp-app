from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone
from .models import UDN, Sector, IssueCategory, Issue, Roles, Ticket, Message, Attachment

User = get_user_model()


class WelpDeskModelsTest(TestCase):
    """Tests para modelos críticos de welp_desk"""

    def setUp(self):
        """Datos de prueba para todos los tests"""
        self.superuser = User.objects.create_user(username='admin', is_superuser=True)
        self.regular_user = User.objects.create_user(username='user1')
        self.other_user = User.objects.create_user(username='user2')
        
        self.udn1 = UDN.objects.create(name='UDN TI')
        self.udn2 = UDN.objects.create(name='UDN RRHH')
        
        self.sector1 = Sector.objects.create(name='Desarrollo')
        self.sector1.udn.add(self.udn1)
        self.sector2 = Sector.objects.create(name='Recursos Humanos')
        self.sector2.udn.add(self.udn2)
        
        self.category1 = IssueCategory.objects.create(name='Bug Crítico')
        self.category1.sector.add(self.sector1)
        self.category2 = IssueCategory.objects.create(name='Consulta RRHH')
        self.category2.sector.add(self.sector2)
        
        self.issue1 = Issue.objects.create(name='Error en login', issue_category=self.category1)
        self.issue2 = Issue.objects.create(name='Consulta vacaciones', issue_category=self.category2)

    def test_ticket_manager_filters_by_user_roles(self):
        """TicketManager filtra por roles - test crítico de seguridad"""
        ticket1 = Ticket.objects.create(udn=self.udn1, sector=self.sector1, 
                                       issue_category=self.category1, issue=self.issue1)
        ticket2 = Ticket.objects.create(udn=self.udn2, sector=self.sector2,
                                       issue_category=self.category2, issue=self.issue2)
        
        Roles.objects.create(user=self.regular_user, udn=self.udn1, can_read=True)
        
        all_tickets = Ticket.objects.get_queryset(user=self.superuser)
        self.assertEqual(all_tickets.count(), 2)
        
        user_tickets = Ticket.objects.get_queryset(user=self.regular_user)
        self.assertEqual(user_tickets.count(), 1)
        self.assertEqual(user_tickets.first().id, ticket1.id)
        
        no_tickets = Ticket.objects.get_queryset(user=self.other_user)
        self.assertEqual(no_tickets.count(), 0)

    def test_roles_unique_together_constraint(self):
        """Constraint unique_together previene duplicación de permisos"""
        Roles.objects.create(user=self.regular_user, udn=self.udn1, sector=self.sector1,
                            issue_category=self.category1, can_read=True)
        
        with self.assertRaises(IntegrityError):
            Roles.objects.create(user=self.regular_user, udn=self.udn1, sector=self.sector1,
                                issue_category=self.category1, can_comment=True)

    def test_ticket_properties_calculation(self):
        """
        TEST #3 - Verificar que las properties created_by y status se calculan correctamente.
        Estas properties son fundamentales para la UX y lógica de negocio.
        """
        # Crear ticket
        ticket = Ticket.objects.create(udn=self.udn1, sector=self.sector1,
                                     issue_category=self.category1, issue=self.issue1)
        
        # Sin mensajes, properties deben retornar None
        self.assertIsNone(ticket.created_by)
        self.assertIsNone(ticket.status)
        
        # Crear primer mensaje
        message1 = Message.objects.create(ticket=ticket, user=self.regular_user, 
                                        status='open', body='Primer mensaje')
        
        # created_by debe ser el usuario del primer mensaje
        self.assertEqual(ticket.created_by, self.regular_user)
        self.assertEqual(ticket.status, 'open')
        
        # Crear segundo mensaje
        message2 = Message.objects.create(ticket=ticket, user=self.other_user,
                                        status='solved', body='Resuelto')
        
        # created_by sigue siendo el primer usuario, status es el último
        self.assertEqual(ticket.created_by, self.regular_user)
        self.assertEqual(ticket.status, 'solved')

    def test_message_save_auto_fill_reported_on(self):
        """
        TEST #4 - Verificar que Message.save() auto-llena reported_on cuando es None.
        Este override personalizado es crucial para mantener consistencia temporal.
        """
        ticket = Ticket.objects.create(udn=self.udn1, sector=self.sector1,
                                     issue_category=self.category1, issue=self.issue1)
        
        # Crear mensaje sin reported_on
        message = Message.objects.create(ticket=ticket, user=self.regular_user,
                                       body='Test mensaje', reported_on=None)
        
        # reported_on debe haberse llenado automáticamente
        self.assertIsNotNone(message.reported_on)
        # Debe ser igual a created_on (o muy cercano)
        time_diff = abs((message.reported_on - message.created_on).total_seconds())
        self.assertLess(time_diff, 1.0)  # Menos de 1 segundo de diferencia

    def test_manytomany_relationships_integrity(self):
        """
        TEST #5 - Verificar que las relaciones ManyToMany funcionan correctamente.
        Cubre la integridad de las relaciones complejas del sistema.
        """
        # Sector puede estar en múltiples UDNs
        shared_sector = Sector.objects.create(name='Sector Compartido')
        shared_sector.udn.add(self.udn1, self.udn2)
        
        self.assertEqual(shared_sector.udn.count(), 2)
        self.assertIn(self.udn1, shared_sector.udn.all())
        self.assertIn(self.udn2, shared_sector.udn.all())
        
        # IssueCategory puede estar en múltiples Sectores
        shared_category = IssueCategory.objects.create(name='Categoría Compartida')
        shared_category.sector.add(self.sector1, self.sector2)
        
        self.assertEqual(shared_category.sector.count(), 2)
        self.assertIn(self.sector1, shared_category.sector.all())
        self.assertIn(self.sector2, shared_category.sector.all())
        
        # Verificar relaciones inversas
        self.assertIn(shared_sector, self.udn1.sectors.all())
        self.assertIn(shared_category, self.sector1.issue_categories.all()) 