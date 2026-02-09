from odoo import fields, models


class SurveyWhatsappWizardLine(models.TransientModel):
    _name = "survey.whatsapp.wizard.line"
    _description = "Survey WhatsApp Wizard Preview Line"

    wizard_id = fields.Many2one(
        comodel_name="survey.whatsapp.wizard",
        required=True,
        ondelete="cascade",
    )
    user_input_id = fields.Many2one(
        comodel_name="survey.user_input",
        string="Participant",
        readonly=True,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        readonly=True,
    )
    mobile = fields.Char(
        string="Mobile Number",
        readonly=True,
    )
    is_valid = fields.Boolean(
        string="Valid",
        readonly=True,
    )
    error_message = fields.Char(
        string="Error",
        readonly=True,
    )
