# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import tagged
from odoo.addons.appointment.tests.common import AppointmentCommon


@tagged('post_install', '-at_install', 'appointment_dynamic_staff')
class TestAppointmentDynamicStaff(AppointmentCommon):
    """Test dynamic staff selection using domains."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Create additional test users with specific attributes for domain filtering
        from odoo.addons.mail.tests.common import mail_new_test_user
        
        cls.staff_user_dept_it = mail_new_test_user(
            cls.env,
            company_id=cls.company_admin.id,
            email='it_staff@test.example.com',
            groups='base.group_user',
            name='IT Staff Member',
            notification_type='email',
            login='staff_it',
            tz='Europe/Brussels'
        )
        
        cls.staff_user_dept_sales = mail_new_test_user(
            cls.env,
            company_id=cls.company_admin.id,
            email='sales_staff@test.example.com',
            groups='base.group_user',
            name='Sales Staff Member',
            notification_type='email',
            login='staff_sales',
            tz='Europe/Brussels'
        )

    def test_basic_domain_application(self):
        """Test that a basic domain correctly selects users."""
        # Create appointment type with empty staff initially
        apt_type = self.env['appointment.type'].create({
            'name': 'Test Dynamic Staff',
            'appointment_tz': 'Europe/Brussels',
            'schedule_based_on': 'users',
            'staff_user_ids': False,
        })
        
        # Verify no staff initially
        self.assertFalse(apt_type.staff_user_ids, "Should have no staff initially")
        
        # Set domain to select users by login pattern
        apt_type.write({
            'staff_user_domain': "[('login', 'in', ['staff_it', 'staff_sales'])]"
        })

        # Recompute dynamic staff
        apt_type.action_recompute_dynamic_staff()

        # Verify users were added to dynamic list
        self.assertIn(
            self.staff_user_dept_it,
            apt_type.dynamic_staff_user_ids,
            "IT staff should be in dynamic_staff_user_ids"
        )
        self.assertIn(
            self.staff_user_dept_sales,
            apt_type.dynamic_staff_user_ids,
            "Sales staff should be in dynamic_staff_user_ids"
        )
        self.assertIn(
            self.staff_user_dept_it,
            apt_type.staff_user_ids,
            "IT staff should be used in staff_user_ids"
        )

    def test_hybrid_manual_dynamic_selection(self):
        """Test that manual and dynamic selections are combined."""
        # Create appointment type with one manual user
        apt_type = self.env['appointment.type'].create({
            'name': 'Test Hybrid Staff',
            'appointment_tz': 'Europe/Brussels',
            'schedule_based_on': 'users',
            'staff_user_ids': [(4, self.staff_user_bxls.id)],
        })
        
        # Verify manual user is present
        self.assertIn(
            self.staff_user_bxls,
            apt_type.staff_user_ids,
            "Manual user should be present"
        )
        
        # Add domain to select IT staff
        apt_type.write({
            'staff_user_domain': "[('login', '=', 'staff_it')]"
        })

        # Recompute dynamic staff
        apt_type.action_recompute_dynamic_staff()

        # Verify manual still present
        self.assertIn(
            self.staff_user_bxls,
            apt_type.staff_user_ids,
            "Manual user should still be present"
        )

        # Verify dynamic user is present in dynamic list
        self.assertIn(
            self.staff_user_dept_it,
            apt_type.dynamic_staff_user_ids,
            "Dynamic IT user should be added to dynamic_staff_user_ids"
        )

        # Verify total merges both
        self.assertEqual(
            len(apt_type.staff_user_ids), 2,
            "Should have exactly 2 users total (1 manual + 1 dynamic)"
        )

    def test_domain_enforcement_on_recalculation(self):
        """Test that dynamic list is recomputed when domain changes."""
        # Create appointment type with domain
        apt_type = self.env['appointment.type'].create({
            'name': 'Test Domain Enforcement',
            'appointment_tz': 'Europe/Brussels',
            'schedule_based_on': 'users',
            'staff_user_domain': "[('login', '=', 'staff_it')]",
        })

        # Compute dynamic
        apt_type.action_recompute_dynamic_staff()

        # Verify IT staff is present in dynamic list
        self.assertIn(
            self.staff_user_dept_it,
            apt_type.dynamic_staff_user_ids,
            "IT staff should be present from domain"
        )

        # Change domain away and back
        apt_type.write({'staff_user_domain': "[('login', '=', 'staff_sales')]"})
        apt_type.action_recompute_dynamic_staff()
        self.assertNotIn(
            self.staff_user_dept_it,
            apt_type.dynamic_staff_user_ids,
            "IT staff should not match the new domain"
        )
        apt_type.write({'staff_user_domain': "[('login', '=', 'staff_it')]"})
        apt_type.action_recompute_dynamic_staff()
        self.assertIn(
            self.staff_user_dept_it,
            apt_type.dynamic_staff_user_ids,
            "IT staff should be back after recompute"
        )

    def test_malformed_domain_handling(self):
        """Test that malformed domains don't break the system."""
        # Create appointment type
        apt_type = self.env['appointment.type'].create({
            'name': 'Test Malformed Domain',
            'appointment_tz': 'Europe/Brussels',
            'schedule_based_on': 'users',
            'staff_user_ids': [(4, self.staff_user_bxls.id)],
        })
        
        # Set malformed domain (invalid Python syntax)
        apt_type.write({
            'staff_user_domain': "[('login', '=', 'test']"  # Missing closing parenthesis
        })
        
        # Force recompute - should not raise exception
        try:
            apt_type.action_recompute_dynamic_staff()
        except Exception as e:
            self.fail(f"Malformed domain should not raise exception: {e}")
        
        # Verify manual user is still present (fallback to existing)
        self.assertIn(
            self.staff_user_bxls,
            apt_type.staff_user_ids,
            "Manual user should still be present despite malformed domain"
        )

        # Malformed domain should not add dynamic users
        self.assertFalse(
            apt_type.dynamic_staff_user_ids,
            "Dynamic users should be empty with malformed domain"
        )

    def test_invalid_domain_type_handling(self):
        """Test that non-list domains are handled gracefully."""
        # Create appointment type
        apt_type = self.env['appointment.type'].create({
            'name': 'Test Invalid Domain Type',
            'appointment_tz': 'Europe/Brussels',
            'schedule_based_on': 'users',
            'staff_user_ids': [(4, self.staff_user_bxls.id)],
        })
        
        # Set invalid domain (not a list)
        apt_type.write({
            'staff_user_domain': "{'login': 'test'}"  # Dict instead of list
        })
        
        # Force recompute - should not raise exception
        try:
            apt_type.action_recompute_dynamic_staff()
        except Exception as e:
            self.fail(f"Invalid domain type should not raise exception: {e}")
        
        # Verify manual user is still present
        self.assertIn(
            self.staff_user_bxls,
            apt_type.staff_user_ids,
            "Manual user should still be present despite invalid domain"
        )

        self.assertFalse(
            apt_type.dynamic_staff_user_ids,
            "Dynamic users should be empty with invalid domain type"
        )

    def test_empty_domain_handling(self):
        """Test that empty domains are handled correctly."""
        # Create appointment type with manual user
        apt_type = self.env['appointment.type'].create({
            'name': 'Test Empty Domain',
            'appointment_tz': 'Europe/Brussels',
            'schedule_based_on': 'users',
            'staff_user_ids': [(4, self.staff_user_bxls.id)],
        })
        
        # Set empty domain
        apt_type.write({
            'staff_user_domain': '[]'
        })
        
        # Force recompute
        apt_type.action_recompute_dynamic_staff()
        
        # Verify manual user is still present (empty domain adds no users)
        self.assertIn(
            self.staff_user_bxls,
            apt_type.staff_user_ids,
            "Manual user should be present"
        )

        self.assertFalse(
            apt_type.dynamic_staff_user_ids,
            "Dynamic users should be empty when domain is empty"
        )

    def test_resources_mode_ignores_domain(self):
        """Test that domain is not applied when in resources mode."""
        # Create appointment type in resources mode
        apt_type = self.env['appointment.type'].create({
            'name': 'Test Resources Mode',
            'appointment_tz': 'Europe/Brussels',
            'schedule_based_on': 'resources',
            'staff_user_domain': "[('login', '=', 'staff_it')]",
        })
        
        # Force recompute
        apt_type.action_recompute_dynamic_staff()
        
        # Verify no staff users are added (resources mode clears staff)
        self.assertFalse(
            apt_type.dynamic_staff_user_ids,
            "Dynamic staff users should be empty in resources mode"
        )

    def test_domain_with_share_users_excluded(self):
        """Test that share users are excluded only if the domain says so."""
        # Create appointment type with domain excluding share users
        apt_type = self.env['appointment.type'].create({
            'name': 'Test No Share Users',
            'appointment_tz': 'Europe/Brussels',
            'schedule_based_on': 'users',
            'staff_user_domain': "[('share', '=', False), ('login', 'in', ['staff_it', 'staff_sales'])]",
        })
        
        # Force recompute
        apt_type.action_recompute_dynamic_staff()
        
        # Verify only internal users are selected
        for user in apt_type.dynamic_staff_user_ids:
            self.assertFalse(
                user.share,
                f"User {user.name} should not be a portal/share user"
            )
