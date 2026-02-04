from odoo import api, models, fields

import uuid


class CalendarEvent(models.Model):
    """
    Extension of calendar.event to add outcome field for completed appointments.
    """
    _inherit = 'calendar.event'

    esito_evento_id = fields.Many2one(
        'calendar.event.outcome',
        string='Esito Evento',
        tracking=True,
        ondelete='restrict',
        domain="[('active', '=', True)]",
        help='Tipologia di esito dell\'appuntamento o evento'
    )

    @api.model_create_multi
    def create(self, vals_list):
        events = super().create(vals_list)
        for event in events:
            event._ensure_videocall_setup()
        return events

    def _ensure_videocall_setup(self):
        self.ensure_one()

        updates = {}
        from_portal = bool(self.env.context.get('from_portal'))

        if from_portal:
            if self.videocall_source != 'discuss':
                updates['videocall_source'] = 'discuss'
        else:
            if not self.videocall_source:
                updates['videocall_source'] = 'discuss'

        if not self.access_token:
            updates['access_token'] = str(uuid.uuid4())

        if from_portal and not self.videocall_location:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            token = updates.get('access_token') or self.access_token
            if base_url and token:
                updates['videocall_location'] = f"{base_url}/calendar/join_videocall/{token}"

        if updates:
            self.write(updates)

        return True
