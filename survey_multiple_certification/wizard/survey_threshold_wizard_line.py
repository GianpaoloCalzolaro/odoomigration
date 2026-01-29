from odoo import fields, models


class SurveyThresholdWizardLine(models.TransientModel):
    _name = 'survey.threshold.wizard.line'
    _description = 'Survey Threshold Wizard Line'

    wizard_id = fields.Many2one('survey.threshold.wizard')
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    description_html = fields.Html()
    percentage_max = fields.Float()
    badge_id = fields.Many2one('gamification.badge')
