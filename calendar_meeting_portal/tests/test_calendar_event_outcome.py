# -*- coding: utf-8 -*-

from odoo.tests import common, tagged
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError


@tagged('post_install', '-at_install')
class TestCalendarEventOutcome(common.TransactionCase):
    """Test cases for calendar.event.outcome model"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.CalendarEventOutcome = cls.env['calendar.event.outcome']
        cls.CalendarEvent = cls.env['calendar.event']
        cls.AppointmentType = cls.env['appointment.type']
        
        # Create test appointment type
        cls.appointment_type = cls.AppointmentType.create({
            'name': 'Test Appointment Type',
        })

    def test_01_create_outcome_basic(self):
        """Test basic creation of calendar event outcome"""
        outcome = self.CalendarEventOutcome.create({
            'name': 'Completato',
            'code': 'completed',
            'description': 'Appuntamento completato con successo',
            'color': 10,
            'sequence': 10,
        })
        
        self.assertEqual(outcome.name, 'Completato')
        self.assertEqual(outcome.code, 'completed')
        self.assertEqual(outcome.description, 'Appuntamento completato con successo')
        self.assertEqual(outcome.color, 10)
        self.assertEqual(outcome.sequence, 10)
        self.assertTrue(outcome.active, 'New outcome should be active by default')

    def test_02_code_uniqueness_constraint(self):
        """Test that code field has uniqueness constraint"""
        self.CalendarEventOutcome.create({
            'name': 'Completato',
            'code': 'completed',
        })
        
        # Try to create another outcome with the same code
        with self.assertRaises(IntegrityError):
            with self.cr.savepoint():
                self.CalendarEventOutcome.create({
                    'name': 'Completato 2',
                    'code': 'completed',
                })

    def test_03_required_fields(self):
        """Test that name and code are required fields"""
        # Test missing name
        with self.assertRaises(ValidationError):
            self.CalendarEventOutcome.create({
                'code': 'test',
            })
        
        # Test missing code
        with self.assertRaises(ValidationError):
            self.CalendarEventOutcome.create({
                'name': 'Test',
            })

    def test_04_active_field_behavior(self):
        """Test active field allows archiving outcomes"""
        outcome = self.CalendarEventOutcome.create({
            'name': 'Annullato',
            'code': 'cancelled',
        })
        
        self.assertTrue(outcome.active)
        
        # Archive the outcome
        outcome.active = False
        self.assertFalse(outcome.active)
        
        # Should still exist but be filtered in default searches
        all_outcomes = self.CalendarEventOutcome.with_context(active_test=False).search([
            ('code', '=', 'cancelled')
        ])
        self.assertEqual(len(all_outcomes), 1)

    def test_05_ordering(self):
        """Test that outcomes are ordered by sequence and name"""
        outcome1 = self.CalendarEventOutcome.create({
            'name': 'Z Outcome',
            'code': 'z_outcome',
            'sequence': 20,
        })
        outcome2 = self.CalendarEventOutcome.create({
            'name': 'A Outcome',
            'code': 'a_outcome',
            'sequence': 10,
        })
        outcome3 = self.CalendarEventOutcome.create({
            'name': 'B Outcome',
            'code': 'b_outcome',
            'sequence': 10,
        })
        
        outcomes = self.CalendarEventOutcome.search([
            ('id', 'in', [outcome1.id, outcome2.id, outcome3.id])
        ])
        
        # Should be ordered by sequence first, then name
        self.assertEqual(outcomes[0].id, outcome2.id)  # sequence 10, name A
        self.assertEqual(outcomes[1].id, outcome3.id)  # sequence 10, name B
        self.assertEqual(outcomes[2].id, outcome1.id)  # sequence 20, name Z

    def test_06_calendar_event_esito_field(self):
        """Test that calendar.event has esito_evento_id field"""
        outcome = self.CalendarEventOutcome.create({
            'name': 'Completato',
            'code': 'completed',
        })
        
        event = self.CalendarEvent.create({
            'name': 'Test Meeting',
            'start': '2024-01-01 10:00:00',
            'stop': '2024-01-01 11:00:00',
            'appointment_type_id': self.appointment_type.id,
            'esito_evento_id': outcome.id,
        })
        
        self.assertEqual(event.esito_evento_id.id, outcome.id)
        self.assertEqual(event.esito_evento_id.name, 'Completato')

    def test_07_ondelete_restrict_behavior(self):
        """Test that outcomes with associated events cannot be deleted"""
        outcome = self.CalendarEventOutcome.create({
            'name': 'In Progress',
            'code': 'in_progress',
        })
        
        event = self.CalendarEvent.create({
            'name': 'Test Meeting',
            'start': '2024-01-01 10:00:00',
            'stop': '2024-01-01 11:00:00',
            'appointment_type_id': self.appointment_type.id,
            'esito_evento_id': outcome.id,
        })
        
        # Try to delete outcome that is linked to an event
        with self.assertRaises(IntegrityError):
            with self.cr.savepoint():
                outcome.unlink()
        
        # After removing the link, deletion should work
        event.esito_evento_id = False
        outcome.unlink()  # Should not raise error

    def test_08_domain_active_only(self):
        """Test that the domain on calendar.event shows only active outcomes"""
        active_outcome = self.CalendarEventOutcome.create({
            'name': 'Active',
            'code': 'active',
            'active': True,
        })
        
        archived_outcome = self.CalendarEventOutcome.create({
            'name': 'Archived',
            'code': 'archived',
            'active': False,
        })
        
        # The domain on the field is [('active', '=', True)]
        # We can verify this by checking the field definition
        field_info = self.CalendarEvent._fields['esito_evento_id']
        self.assertEqual(field_info.domain, "[('active', '=', True)]")

    def test_09_optional_fields(self):
        """Test that description and color are optional"""
        outcome = self.CalendarEventOutcome.create({
            'name': 'Minimal',
            'code': 'minimal',
        })
        
        self.assertFalse(outcome.description)
        self.assertFalse(outcome.color)

    def test_10_calendar_event_without_esito(self):
        """Test that calendar events can be created without an outcome"""
        event = self.CalendarEvent.create({
            'name': 'Test Meeting',
            'start': '2024-01-01 10:00:00',
            'stop': '2024-01-01 11:00:00',
            'appointment_type_id': self.appointment_type.id,
        })
        
        self.assertFalse(event.esito_evento_id)
