from odoo import api, fields, models


class SurveyWhatsappSummaryWizard(models.TransientModel):
    _name = "survey.whatsapp.summary.wizard"
    _description = "Survey WhatsApp Send Summary"

    sent_count = fields.Integer(
        string="Sent Successfully",
        readonly=True,
    )
    error_count = fields.Integer(
        string="Failed",
        readonly=True,
    )
    total_count = fields.Integer(
        string="Total",
        compute="_compute_total_count",
    )
    summary_line_ids = fields.One2many(
        comodel_name="survey.whatsapp.summary.wizard.line",
        inverse_name="wizard_id",
        string="Error Details",
    )

    @api.depends("sent_count", "error_count")
    def _compute_total_count(self):
        for wizard in self:
            wizard.total_count = wizard.sent_count + wizard.error_count
