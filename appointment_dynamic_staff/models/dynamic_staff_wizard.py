# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AppointmentDynamicStaffWizard(models.TransientModel):
    _name = 'appointment.dynamic.staff.wizard'
    _description = 'Appointment Dynamic Staff Wizard'

    appointment_type_id = fields.Many2one(
        comodel_name='appointment.type',
        required=True,
        ondelete='cascade',
    )

    staff_user_domain = fields.Char(
        string='Regola Dinamica Staff',
        default='[]',
        required=True,
    )

    preview_count = fields.Integer(
        string='Totale trovati',
        readonly=True,
    )

    preview_user_ids = fields.Many2many(
        comodel_name='res.users',
        relation='appointment_dynamic_staff_wizard_preview_user_rel',
        column1='wizard_id',
        column2='user_id',
        string='Primi 10 utenti',
        readonly=True,
    )

    preview_limit = fields.Integer(
        string='Limite anteprima',
        default=10,
        readonly=True,
    )

    def _compute_preview(self):
        self.ensure_one()

        try:
            domain = self.appointment_type_id._get_dynamic_staff_domain(self.staff_user_domain)
        except Exception as e:
            _logger.warning('Invalid dynamic staff domain in wizard: %s', str(e))
            return {
                'ok': False,
                'message': (
                    'Regola non valida. Verifica la sintassi del dominio.\n\n'
                    f'Dettaglio: {e}'
                ),
            }

        User = self.env['res.users']
        total = User.search_count(domain)
        users = User.search(domain, limit=self.preview_limit)

        self.preview_count = total
        self.preview_user_ids = [(6, 0, users.ids)]
        return {'ok': True}

    def action_preview(self):
        self.ensure_one()
        res = self._compute_preview()
        if not res.get('ok'):
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Dominio non valido',
                    'message': res.get('message'),
                    'type': 'warning',
                    'sticky': True,
                },
            }
        view = self.env.ref('appointment_dynamic_staff.view_appointment_dynamic_staff_wizard_form')
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'target': 'new',
        }

    def action_apply(self):
        self.ensure_one()

        apt = self.appointment_type_id
        apt.write({'staff_user_domain': self.staff_user_domain or '[]'})
        apt.action_recompute_dynamic_staff()
        return {'type': 'ir.actions.act_window_close'}
