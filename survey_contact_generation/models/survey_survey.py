# Copyright 2023 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    generation_type = fields.Selection(
        selection=[("contact", "Contact"), ("applicant", "Applicant")],
        default="contact",
        string="Generation Type",
    )
    job_position_id = fields.Many2one(
        comodel_name="hr.job",
        string="Job Position",
    )
    generate_contact = fields.Boolean(
        help="Generate contacts for anonymous survey users",
    )
    create_parent_contact = fields.Boolean(
        help="Set the company_name in a question and a parent contact will be "
        "created to hold the generated one",
    )

    @api.onchange("generation_type")
    def _onchange_generation_type(self):
        if self.generation_type == "contact":
            self.job_position_id = False
        else:
            self.generate_contact = False
            self.create_parent_contact = False

    @api.constrains("generation_type", "job_position_id")
    def _check_job_position(self):
        for survey in self:
            if survey.generation_type == "applicant" and not survey.job_position_id:
                raise ValidationError("Job position is required for applicant generation.")
