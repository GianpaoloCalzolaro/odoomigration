from odoo import fields, models


class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    generating_survey_user_input_id = fields.Many2one(
        comodel_name="survey.user_input", copy=False, readonly=True
    )
