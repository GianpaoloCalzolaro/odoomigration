# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class AppointmentType(models.Model):
    _inherit = 'appointment.type'

    staff_user_domain = fields.Char(
        string="Regola Dinamica Staff",
        help="Definisci una regola per selezionare automaticamente gli utenti (es. per dipartimento o tag).",
        default='[]',
        copy=True,
    )

    manual_staff_user_ids = fields.Many2many(
        comodel_name='res.users',
        relation='appointment_type_manual_staff_user_rel',
        column1='appointment_type_id',
        column2='user_id',
        string="Staff Manuale",
        help="Utenti selezionati manualmente (separati da quelli dinamici).",
        copy=False,
    )

    dynamic_staff_user_ids = fields.Many2many(
        comodel_name='res.users',
        relation='appointment_type_dynamic_staff_user_rel',
        column1='appointment_type_id',
        column2='user_id',
        string="Staff Dinamico",
        help="Utenti aggiunti automaticamente in base alla regola (domain).",
        compute='_compute_dynamic_staff_user_ids',
        store=True,
        copy=False,
        readonly=True,
    )

    dynamic_staff_count = fields.Integer(
        string="N. Utenti Dinamici",
        compute='_compute_dynamic_staff_count',
        store=False,
    )

    manual_staff_count = fields.Integer(
        string="N. Utenti Manuali",
        compute='_compute_manual_staff_count',
        store=False,
    )

    dynamic_staff_last_update = fields.Datetime(
        string="Ultimo Aggiornamento Staff Dinamico",
        copy=False,
        readonly=True,
    )

    @api.depends('staff_user_domain', 'schedule_based_on')
    def _compute_dynamic_staff_user_ids(self):
        for record in self:
            if record.schedule_based_on != 'users':
                record.dynamic_staff_user_ids = [(5, 0, 0)]
                continue

            domain_str = (record.staff_user_domain or '').strip()
            if not domain_str or domain_str in ('[]', ''):
                record.dynamic_staff_user_ids = [(5, 0, 0)]
                continue

            try:
                domain = record._get_dynamic_staff_domain(domain_str)
                users = self.env['res.users'].search(domain)
                record.dynamic_staff_user_ids = [(6, 0, users.ids)]
            except Exception as e:
                _logger.warning(
                    "Error computing dynamic staff for appointment.type (id: %s): %s",
                    record.id, str(e)
                )
                record.dynamic_staff_user_ids = [(5, 0, 0)]

    @api.depends('schedule_based_on', 'resource_ids', 'manual_staff_user_ids', 'dynamic_staff_user_ids')
    def _compute_staff_user_ids(self):
        resource_records = self.filtered(lambda r: r.schedule_based_on == 'resources')
        if resource_records:
            super(AppointmentType, resource_records.with_context(skip_manual_staff_sync=True))._compute_staff_user_ids()

        user_records = self.filtered(lambda r: r.schedule_based_on == 'users')
        for record in user_records:
            staff = record.manual_staff_user_ids | record.dynamic_staff_user_ids
            if not staff:
                staff = record.env.user
            record.with_context(skip_manual_staff_sync=True).staff_user_ids = staff

    def _get_dynamic_staff_domain(self, domain_str):
        """Return a safe domain list to search users for dynamic staff."""
        if not domain_str or not domain_str.strip():
            return [('id', '=', False)]

        domain = safe_eval(domain_str, {'uid': self.env.uid, 'user': self.env.user})
        if not isinstance(domain, list):
            raise ValueError("Domain deve essere una lista")

        secure_domain = []
        if not any(isinstance(t, (list, tuple)) and len(t) >= 1 and t[0] == 'active' for t in domain):
            secure_domain.append(('active', '=', True))
        return secure_domain + domain

    def action_recompute_dynamic_staff(self):
        self._compute_dynamic_staff_user_ids()
        self._compute_staff_user_ids()
        self.dynamic_staff_last_update = fields.Datetime.now()
        return True

    def action_open_dynamic_staff_wizard(self):
        self.ensure_one()
        view = self.env.ref('appointment_dynamic_staff.view_appointment_dynamic_staff_wizard_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Configura regola dinamica',
            'res_model': 'appointment.dynamic.staff.wizard',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'target': 'new',
            'context': {
                'default_appointment_type_id': self.id,
                'default_staff_user_domain': self.staff_user_domain or '[]',
            },
        }

    @api.depends('dynamic_staff_user_ids')
    def _compute_dynamic_staff_count(self):
        for record in self:
            record.dynamic_staff_count = len(record.dynamic_staff_user_ids)

    @api.depends('manual_staff_user_ids')
    def _compute_manual_staff_count(self):
        for record in self:
            record.manual_staff_count = len(record.manual_staff_user_ids)

    def write(self, vals):
        if self.env.context.get('skip_manual_staff_sync'):
            return super().write(vals)

        if 'staff_user_ids' in vals and 'manual_staff_user_ids' not in vals:
            if len(self) == 1 and isinstance(vals.get('staff_user_ids'), list):
                commands = list(vals['staff_user_ids'])
                filtered_commands = []
                for cmd in commands:
                    if isinstance(cmd, (list, tuple)) and len(cmd) >= 3 and cmd[0] == 6:
                        ids = set(cmd[2] or [])
                        ids -= set(self.dynamic_staff_user_ids.ids)
                        filtered_commands.append((6, 0, list(ids)))
                    else:
                        filtered_commands.append(cmd)
                vals['manual_staff_user_ids'] = filtered_commands
            else:
                vals['manual_staff_user_ids'] = vals['staff_user_ids']

        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get('skip_manual_staff_sync'):
            for vals in vals_list:
                if 'staff_user_ids' in vals and 'manual_staff_user_ids' not in vals:
                    vals['manual_staff_user_ids'] = vals['staff_user_ids']
        return super().create(vals_list)
