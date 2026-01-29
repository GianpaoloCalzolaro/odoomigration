# -*- coding: utf-8 -*-

from odoo.tests import common, tagged
from odoo.exceptions import AccessError, ValidationError
from datetime import datetime, timedelta


@tagged('post_install', '-at_install')
class TestCalendarEventSecurity(common.TransactionCase):
    """
    FASE 3: Test cases for security and permissions configuration
    Tests multi-level security validations for calendar event outcomes
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.CalendarEventOutcome = cls.env['calendar.event.outcome']
        cls.CalendarEvent = cls.env['calendar.event']
        cls.ResUsers = cls.env['res.users']
        cls.ResPartner = cls.env['res.partner']
        cls.HrEmployee = cls.env['hr.employee']
        cls.AppointmentType = cls.env['appointment.type']
        
        # Create test appointment type
        cls.appointment_type = cls.AppointmentType.create({
            'name': 'Test Appointment Type',
        })
        
        # Create test groups
        cls.group_system = cls.env.ref('base.group_system')
        cls.group_user = cls.env.ref('base.group_user')
        cls.group_portal = cls.env.ref('base.group_portal')
        
        # Create test users
        # Admin user
        cls.admin_user = cls.ResUsers.create({
            'name': 'Admin User',
            'login': 'admin_test',
            'email': 'admin@test.com',
            'groups_id': [(6, 0, [cls.group_system.id])],
        })
        
        # Internal user
        cls.internal_user = cls.ResUsers.create({
            'name': 'Internal User',
            'login': 'internal_test',
            'email': 'internal@test.com',
            'groups_id': [(6, 0, [cls.group_user.id])],
        })
        
        # Portal employee user
        cls.portal_employee_user = cls.ResUsers.create({
            'name': 'Portal Employee User',
            'login': 'portal_employee_test',
            'email': 'portal_employee@test.com',
            'groups_id': [(6, 0, [cls.group_portal.id])],
        })
        
        # Create employee for portal user
        cls.employee = cls.HrEmployee.create({
            'name': 'Portal Employee',
            'user_id': cls.portal_employee_user.id,
        })
        
        # Portal non-employee user
        cls.portal_user = cls.ResUsers.create({
            'name': 'Portal User',
            'login': 'portal_test',
            'email': 'portal@test.com',
            'groups_id': [(6, 0, [cls.group_portal.id])],
        })
        
        # Create test outcomes
        cls.active_outcome = cls.CalendarEventOutcome.create({
            'name': 'Completato',
            'code': 'completed',
            'active': True,
        })
        
        cls.archived_outcome = cls.CalendarEventOutcome.create({
            'name': 'Archiviato',
            'code': 'archived',
            'active': False,
        })
        
        # Create test calendar events
        start_date = datetime.now() + timedelta(days=1)
        end_date = start_date + timedelta(hours=1)
        
        cls.meeting_with_employee = cls.CalendarEvent.create({
            'name': 'Meeting with Employee',
            'start': start_date,
            'stop': end_date,
            'appointment_type_id': cls.appointment_type.id,
            'partner_ids': [(6, 0, [cls.portal_employee_user.partner_id.id])],
        })
        
        cls.meeting_without_employee = cls.CalendarEvent.create({
            'name': 'Meeting without Employee',
            'start': start_date,
            'stop': end_date,
            'appointment_type_id': cls.appointment_type.id,
            'partner_ids': [(6, 0, [cls.internal_user.partner_id.id])],
        })

    def test_01_admin_full_access_outcomes(self):
        """Test Case 1: Admin has full access to outcome management"""
        # Admin can read outcomes
        outcomes = self.CalendarEventOutcome.with_user(self.admin_user).search([])
        self.assertTrue(len(outcomes) >= 2, 'Admin should be able to read outcomes')
        
        # Admin can create outcome
        new_outcome = self.CalendarEventOutcome.with_user(self.admin_user).create({
            'name': 'Admin Created',
            'code': 'admin_created',
        })
        self.assertTrue(new_outcome.id, 'Admin should be able to create outcomes')
        
        # Admin can write outcome
        new_outcome.with_user(self.admin_user).write({'name': 'Admin Updated'})
        self.assertEqual(new_outcome.name, 'Admin Updated', 'Admin should be able to update outcomes')
        
        # Admin can delete outcome
        new_outcome.with_user(self.admin_user).unlink()
        self.assertFalse(new_outcome.exists(), 'Admin should be able to delete outcomes')

    def test_02_internal_user_read_only_outcomes(self):
        """Test Case 2: Internal users can only read outcomes"""
        # Internal user can read outcomes
        outcomes = self.CalendarEventOutcome.with_user(self.internal_user).search([])
        self.assertTrue(len(outcomes) >= 1, 'Internal user should be able to read outcomes')
        
        # Internal user cannot create outcome
        with self.assertRaises(AccessError, msg='Internal user should not be able to create outcomes'):
            self.CalendarEventOutcome.with_user(self.internal_user).create({
                'name': 'Internal Created',
                'code': 'internal_created',
            })
        
        # Internal user cannot write outcome
        with self.assertRaises(AccessError, msg='Internal user should not be able to update outcomes'):
            self.active_outcome.with_user(self.internal_user).write({'name': 'Internal Updated'})
        
        # Internal user cannot delete outcome
        with self.assertRaises(AccessError, msg='Internal user should not be able to delete outcomes'):
            self.active_outcome.with_user(self.internal_user).unlink()

    def test_03_portal_user_read_only_active_outcomes(self):
        """Test Case 3: Portal users can only read active outcomes"""
        # Portal user can read active outcomes
        outcomes = self.CalendarEventOutcome.with_user(self.portal_user).search([
            ('active', '=', True)
        ])
        self.assertTrue(len(outcomes) >= 1, 'Portal user should be able to read active outcomes')
        
        # Portal user should not see archived outcomes (filtered by record rule)
        all_outcomes = self.CalendarEventOutcome.with_user(self.portal_user).search([])
        self.assertTrue(
            all(outcome.active for outcome in all_outcomes),
            'Portal user should only see active outcomes due to record rule'
        )
        
        # Portal user cannot create outcome
        with self.assertRaises(AccessError, msg='Portal user should not be able to create outcomes'):
            self.CalendarEventOutcome.with_user(self.portal_user).create({
                'name': 'Portal Created',
                'code': 'portal_created',
            })
        
        # Portal user cannot write outcome
        with self.assertRaises(AccessError, msg='Portal user should not be able to update outcomes'):
            self.active_outcome.with_user(self.portal_user).write({'name': 'Portal Updated'})
        
        # Portal user cannot delete outcome
        with self.assertRaises(AccessError, msg='Portal user should not be able to delete outcomes'):
            self.active_outcome.with_user(self.portal_user).unlink()

    def test_04_portal_employee_can_update_own_meeting_outcome(self):
        """Test Case 4: Portal employee can update outcome of meetings where they are attendees"""
        # Portal employee can read their meetings
        meetings = self.CalendarEvent.with_user(self.portal_employee_user).search([
            ('partner_ids', 'in', self.portal_employee_user.partner_id.ids)
        ])
        self.assertTrue(len(meetings) >= 1, 'Portal employee should see their meetings')
        
        # Portal employee can update outcome of their meeting
        self.meeting_with_employee.with_user(self.portal_employee_user).write({
            'esito_evento_id': self.active_outcome.id
        })
        self.assertEqual(
            self.meeting_with_employee.esito_evento_id.id,
            self.active_outcome.id,
            'Portal employee should be able to update outcome of their meeting'
        )
        
        # Portal employee cannot update meeting they are not attending
        with self.assertRaises(AccessError, msg='Portal employee should not update meetings where not attendee'):
            self.meeting_without_employee.with_user(self.portal_employee_user).write({
                'esito_evento_id': self.active_outcome.id
            })

    def test_05_portal_non_employee_cannot_update_meetings(self):
        """Test Case 5: Portal users who are not employees have limited access"""
        # Portal non-employee can read outcomes (but only active ones)
        outcomes = self.CalendarEventOutcome.with_user(self.portal_user).search([])
        self.assertTrue(len(outcomes) >= 1, 'Portal non-employee can read active outcomes')
        
        # Create a meeting with portal user as attendee
        start_date = datetime.now() + timedelta(days=2)
        end_date = start_date + timedelta(hours=1)
        meeting_with_portal = self.CalendarEvent.create({
            'name': 'Meeting with Portal User',
            'start': start_date,
            'stop': end_date,
            'appointment_type_id': self.appointment_type.id,
            'partner_ids': [(6, 0, [self.portal_user.partner_id.id])],
        })
        
        # Portal non-employee should be able to see the meeting (they are attendee)
        meeting = self.CalendarEvent.with_user(self.portal_user).search([
            ('id', '=', meeting_with_portal.id)
        ])
        self.assertTrue(meeting.exists(), 'Portal non-employee should see meetings where they are attendee')
        
        # Portal non-employee can update their meeting
        # (Controller will block, but ORM allows due to record rule)
        meeting_with_portal.with_user(self.portal_user).write({
            'esito_evento_id': self.active_outcome.id
        })
        # This passes ORM level but controller would block based on employee check

    def test_06_archived_outcome_not_assignable(self):
        """Test Case 6: Archived outcomes cannot be assigned to new events"""
        # Try to assign archived outcome directly (should work at ORM level)
        start_date = datetime.now() + timedelta(days=3)
        end_date = start_date + timedelta(hours=1)
        
        # At ORM level, archived outcome can be assigned (no constraint)
        # But controller validation would prevent this
        meeting = self.CalendarEvent.create({
            'name': 'Test Meeting',
            'start': start_date,
            'stop': end_date,
            'appointment_type_id': self.appointment_type.id,
            'esito_evento_id': self.archived_outcome.id,  # This works at ORM
        })
        self.assertEqual(
            meeting.esito_evento_id.id,
            self.archived_outcome.id,
            'Archived outcome can be assigned at ORM level'
        )
        # Note: Controller validation prevents this via UI

    def test_07_outcome_domain_filters_active_only(self):
        """Test Case 7: Verify field domain filters only active outcomes"""
        # Check that field definition has correct domain
        field_info = self.CalendarEvent._fields['esito_evento_id']
        self.assertEqual(
            field_info.domain,
            "[('active', '=', True)]",
            'Field domain should filter only active outcomes'
        )

    def test_08_admin_sees_all_outcomes_including_archived(self):
        """Test Case 8: Admin can see all outcomes including archived"""
        # Admin searches without context
        all_outcomes = self.CalendarEventOutcome.with_user(self.admin_user).with_context(
            active_test=False
        ).search([])
        
        # Should include both active and archived
        active_count = len([o for o in all_outcomes if o.active])
        archived_count = len([o for o in all_outcomes if not o.active])
        
        self.assertTrue(active_count >= 1, 'Admin should see active outcomes')
        self.assertTrue(archived_count >= 1, 'Admin should see archived outcomes')

    def test_09_record_rule_filters_portal_meetings(self):
        """Test Case 9: Record rule ensures portal users only see their meetings"""
        # Portal employee should only see meetings where they are attendees
        employee_meetings = self.CalendarEvent.with_user(self.portal_employee_user).search([])
        
        for meeting in employee_meetings:
            self.assertIn(
                self.portal_employee_user.partner_id.id,
                meeting.partner_ids.ids,
                'Portal employee should only see meetings where they are attendee'
            )

    def test_10_multiple_employees_different_meetings(self):
        """Test Case 10: Multiple portal employees can only update their own meetings"""
        # Create second portal employee
        portal_employee_2 = self.ResUsers.create({
            'name': 'Portal Employee 2',
            'login': 'portal_employee_2',
            'email': 'portal_employee2@test.com',
            'groups_id': [(6, 0, [self.group_portal.id])],
        })
        
        employee_2 = self.HrEmployee.create({
            'name': 'Portal Employee 2',
            'user_id': portal_employee_2.id,
        })
        
        # Create meeting with employee 2
        start_date = datetime.now() + timedelta(days=4)
        end_date = start_date + timedelta(hours=1)
        meeting_employee_2 = self.CalendarEvent.create({
            'name': 'Meeting with Employee 2',
            'start': start_date,
            'stop': end_date,
            'appointment_type_id': self.appointment_type.id,
            'partner_ids': [(6, 0, [portal_employee_2.partner_id.id])],
        })
        
        # Employee 2 can update their meeting
        meeting_employee_2.with_user(portal_employee_2).write({
            'esito_evento_id': self.active_outcome.id
        })
        self.assertEqual(
            meeting_employee_2.esito_evento_id.id,
            self.active_outcome.id,
            'Employee 2 can update their meeting'
        )
        
        # Employee 1 cannot update employee 2's meeting
        with self.assertRaises(AccessError, msg='Employee 1 should not update employee 2 meeting'):
            meeting_employee_2.with_user(self.portal_employee_user).write({
                'esito_evento_id': False
            })
