from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SurveyCertificationThreshold(models.Model):
    """Store thresholds for multi certification surveys."""

    _name = 'survey.certification.threshold'
    _description = 'Survey Certification Threshold'
    _order = 'sequence, id'

    survey_id = fields.Many2one('survey.survey', ondelete='cascade', required=True, index=True)
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    description_html = fields.Html()
    percentage_min = fields.Float(compute='_compute_percentage_min', store=True)
    percentage_max = fields.Float(required=True)
    badge_id = fields.Many2one('gamification.badge')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('percent_range', 'CHECK(percentage_max>=0 and percentage_max<=100)',
         'Percentage must be between 0 and 100.'),
        ('percent_min_lt_max', 'CHECK(percentage_min < percentage_max)',
         'Min percentage must be lower than max percentage.'),
    ]

    @api.depends('survey_id', 'percentage_max')
    def _compute_percentage_min(self):
        for threshold in self:
            previous = self.search([
                ('survey_id', '=', threshold.survey_id.id),
                ('sequence', '<', threshold.sequence)
            ], order='sequence desc', limit=1)
            if previous:
                threshold.percentage_min = previous.percentage_max
            else:
                threshold.percentage_min = 0.0

    @api.constrains('percentage_max')
    def _check_survey_state(self):
        for threshold in self:
            if threshold.survey_id and threshold.survey_id.user_input_ids:
                raise ValidationError(_('Cannot modify threshold once the survey has answers.'))

    def create_challenge(self):
        if self.badge_id:
            self.env['gamification.challenge'].sudo().create({
                'name': _('Badge for %s') % self.name,
                'reward_id': self.badge_id.id,
            })

    @api.model
    def create(self, vals):
        threshold = super().create(vals)
        threshold.create_challenge()
        return threshold

    def write(self, vals):
        res = super().write(vals)
        if 'badge_id' in vals:
            for record in self:
                record.create_challenge()
        return res
