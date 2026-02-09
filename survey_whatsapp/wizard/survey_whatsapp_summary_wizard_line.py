from odoo import fields, models


class SurveyWhatsappSummaryWizardLine(models.TransientModel):
    _name = "survey.whatsapp.summary.wizard.line"
    _description = "Survey WhatsApp Summary Line"

    wizard_id = fields.Many2one(
        comodel_name="survey.whatsapp.summary.wizard",
        required=True,
        ondelete="cascade",
    )
    partner_name = fields.Char(
        string="Partner",
        readonly=True,
    )
    mobile = fields.Char(
        string="Mobile Number",
        readonly=True,
    )
    error_type = fields.Char(
        string="Error Type",
        readonly=True,
    )
    error_message = fields.Char(
        string="Error Message",
        readonly=True,
    )
