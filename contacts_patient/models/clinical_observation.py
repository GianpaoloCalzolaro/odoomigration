from odoo import models, fields


class ClinicalObservation(models.Model):
    _name = 'clinical.observation'
    _description = 'Clinical Observation'
    _order = 'date_created desc'

    clinical_sheet_id = fields.Many2one(
        'clinical.sheet',
        string='Clinical Sheet',
        required=True,
        ondelete='cascade'
    )
    observation_text = fields.Text(string='Observation', required=True)
    date_created = fields.Datetime(
        string='Date Created',
        default=fields.Datetime.now,
        readonly=True
    )
    author_id = fields.Many2one(
        'res.users',
        string='Author',
        default=lambda self: self.env.user,
        readonly=True
    )
