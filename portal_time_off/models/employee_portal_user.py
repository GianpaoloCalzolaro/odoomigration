from odoo import models, fields, api , _
from odoo.exceptions import UserError



class EmployeePortalUser(models.Model):
    _inherit = 'hr.employee'

    def action_create_portal_user(self):
        self.ensure_one()
        if not self.work_email and not self.private_email:
            raise UserError(
                _("Please set either a work email or a private email address before creating a portal user."))
        for record in self:
            if not record.user_id:
                user_vals = {
                    'name': record.name,
                    'login': record.work_email,
                    'email': record.work_email,
                    'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
                }
                user = self.env['res.users'].create(user_vals)
                record.user_id = user
