from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from .models import UDN, Sector, IssueCategory, Issue, Roles, Ticket, Message

User = get_user_model()


class DeskModelsTest(TestCase):

    def setUp(self):
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
        Roles.objects.create(user=self.regular_user, udn=self.udn1, sector=self.sector1,
                            issue_category=self.category1, can_read=True)
        
        with self.assertRaises(IntegrityError):
            Roles.objects.create(user=self.regular_user, udn=self.udn1, sector=self.sector1,
                                issue_category=self.category1, can_comment=True)

    def test_ticket_properties_calculation(self):
        ticket = Ticket.objects.create(udn=self.udn1, sector=self.sector1,
                                     issue_category=self.category1, issue=self.issue1)
        
        self.assertIsNone(ticket.created_by)
        self.assertIsNone(ticket.status)
        
        message1 = Message.objects.create(ticket=ticket, user=self.regular_user, 
                                        status='open', body='Primer mensaje')
        
        self.assertEqual(ticket.created_by, self.regular_user)
        self.assertEqual(ticket.status, 'open')
        
        message2 = Message.objects.create(ticket=ticket, user=self.other_user,
                                        status='solved', body='Resuelto')
        
        self.assertEqual(ticket.created_by, self.regular_user)
        self.assertEqual(ticket.status, 'solved')

    def test_message_save_auto_fill_reported_on(self):
        ticket = Ticket.objects.create(udn=self.udn1, sector=self.sector1,
                                     issue_category=self.category1, issue=self.issue1)
        
        message = Message.objects.create(ticket=ticket, user=self.regular_user,
                                       body='Test mensaje', reported_on=None)
        
        self.assertIsNotNone(message.reported_on)
        time_diff = abs((message.reported_on - message.created_on).total_seconds())
        self.assertLess(time_diff, 1.0)

    def test_manytomany_relationships_integrity(self):
        shared_sector = Sector.objects.create(name='Sector Compartido')
        shared_sector.udn.add(self.udn1, self.udn2)
        
        self.assertEqual(shared_sector.udn.count(), 2)
        self.assertIn(self.udn1, shared_sector.udn.all())
        self.assertIn(self.udn2, shared_sector.udn.all())
        
        shared_category = IssueCategory.objects.create(name='Categoría Compartida')
        shared_category.sector.add(self.sector1, self.sector2)
        
        self.assertEqual(shared_category.sector.count(), 2)
        self.assertIn(self.sector1, shared_category.sector.all())
        self.assertIn(self.sector2, shared_category.sector.all())
        
        self.assertIn(shared_sector, self.udn1.sectors.all())
        self.assertIn(shared_category, self.sector1.issue_categories.all()) 