from odoo import api, fields, models


class SurveyUserInputHistory(models.Model):
    _name = 'survey.user_input.history'
    _description = 'Survey User Input History'
    _order = 'attempt_number'

    user_input_id = fields.Many2one('survey.user_input', ondelete='cascade', required=True, index=True)
    score_percentage = fields.Float()
    threshold_id = fields.Many2one('survey.certification.threshold')
    certification_name = fields.Char()
    completion_date = fields.Datetime()
    attempt_number = fields.Integer()

    @api.model
    def create_from_user_input(self, user_input):
        existing = self.search([('user_input_id', '=', user_input.id)])
        attempt = len(existing) + 1
        return self.create({
            'user_input_id': user_input.id,
            'score_percentage': user_input.scoring_percentage,
            'threshold_id': user_input.threshold_reached_id.id,
            'certification_name': user_input.current_certification_name,
            'completion_date': fields.Datetime.now(),
            'attempt_number': attempt,
        })
