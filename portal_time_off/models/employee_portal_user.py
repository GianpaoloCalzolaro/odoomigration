from odoo import models, api
from odoo.exceptions import UserError



class EmployeePortalUser(models.Model):
    _inherit = 'hr.employee'

    def action_create_portal_user(self):
        self.ensure_one()
        if not self.work_email and not self.private_email:
            raise UserError(
                self.env._("Please set either a work email or a private email address before creating a portal user."))

        if not self.user_id:
            user_vals = {
                'name': self.name,
                'login': self.work_email or self.private_email,
                'email': self.work_email or self.private_email,
                'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
                'company_id': self.company_id.id,
                'company_ids': [(6, 0, self.company_id.ids)],
            }
            user = self.env['res.users'].sudo().create(user_vals)
            self.user_id = user
