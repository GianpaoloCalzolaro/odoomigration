from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    note_count = fields.Integer(string='Diario Note Count', compute='_compute_note_count')

    def _compute_note_count(self):
        Note = self.env['portal.note']
        for partner in self:
            partner.note_count = Note.search_count([('user_id.partner_id', '=', partner.id)])

    def action_view_notes(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('customer_notes_odoo.action_portal_notes')
        action['domain'] = [('user_id.partner_id', '=', self.id)]
        return action
