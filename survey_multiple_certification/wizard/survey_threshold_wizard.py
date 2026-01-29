from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SurveyThresholdWizard(models.TransientModel):
    _name = 'survey.threshold.wizard'
    _description = 'Survey Threshold Wizard'

    survey_id = fields.Many2one('survey.survey', required=True)
    step = fields.Selection([
        ('select', 'Select'),
        ('config', 'Config')
    ], default='select')
    threshold_count = fields.Integer(default=2)
    threshold_line_ids = fields.One2many('survey.threshold.wizard.line', 'wizard_id')

    def action_next(self):
        if self.threshold_count < 2 or self.threshold_count > 15:
            raise ValidationError(_('Number of thresholds must be between 2 and 15'))
        if self.step == 'select':
            self.threshold_line_ids.unlink()
            for i in range(self.threshold_count):
                self.env['survey.threshold.wizard.line'].create({
                    'wizard_id': self.id,
                    'sequence': (i + 1) * 10,
                    'name': f'Level {i + 1}',  # Aggiungo un nome di default
                    'percentage_max': 100.0,
                })
            self.step = 'config'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'survey.threshold.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_apply(self):
        self.ensure_one()
        self.survey_id.threshold_ids.unlink()
        for line in self.threshold_line_ids:
            self.env['survey.certification.threshold'].create({
                'survey_id': self.survey_id.id,
                'sequence': line.sequence,
                'name': line.name,
                'description_html': line.description_html,
                'percentage_max': line.percentage_max,
                'badge_id': line.badge_id.id if line.badge_id else False,  # Gestisco il caso None
            })
        return {'type': 'ir.actions.act_window_close'}
