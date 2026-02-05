# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from markupsafe import Markup

from odoo import fields, models
from odoo.tools import format_date, format_datetime

_logger = logging.getLogger(__name__)


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    opportunity_id = fields.Many2one(comodel_name="crm.lead")

    def _prepare_opportunity(self):
        vals = {
            "name": self.survey_id.title,
            "tag_ids": [(6, 0, self.survey_id.crm_tag_ids.ids)],
            "partner_id": self.partner_id.id,
            "user_id": self.survey_id.crm_team_id.user_id.id,
            "team_id": self.survey_id.crm_team_id.id,
            "company_id": self.env.company.id,
            "survey_user_input_id": self.id,
            "description": self._prepare_lead_description(),
        }
        if not self.partner_id:
            # Solo aggiungere se i valori sono presenti e validi
            if self.email:
                vals["email_from"] = self.email
            if self.nickname:
                vals["contact_name"] = self.nickname
        # Fill sale.order fields from answers
        elegible_inputs = self.user_input_line_ids.filtered(
            lambda x: x.question_id.crm_lead_field and not x.skipped
        )
        basic_inputs = elegible_inputs.filtered(
            lambda x: x.answer_type not in {"suggestion"}
        )
        # Ottenere lista campi validi di crm.lead
        valid_fields = self.env["crm.lead"]._fields.keys()
        # Filtrare solo campi che esistono
        for line in basic_inputs:
            field_name = line.question_id.crm_lead_field.name
            if field_name in valid_fields:
                vals[field_name] = line[f"value_{line.answer_type}"]
            else:
                _logger.warning(
                    "Campo %s non esiste in crm.lead, ignorato "
                    "(survey: %s, question: %s)",
                    field_name,
                    self.survey_id.title,
                    line.question_id.title,
                )
        for line in elegible_inputs - basic_inputs:
            field_name = line.question_id.crm_lead_field.name
            if field_name in valid_fields:
                value = (
                    line.suggested_answer_id.value
                    if line.answer_type == "suggestion"
                    else line[f"value_{line.answer_type}"]
                )
                vals[field_name] = value
            else:
                _logger.warning(
                    "Campo %s non esiste in crm.lead, ignorato "
                    "(survey: %s, question: %s)",
                    field_name,
                    self.survey_id.title,
                    line.question_id.title,
                )
        return vals

    def _build_answers_html(self, given_answers=False):
        """Basic html formatted answers. Can be used in mail communications and other
        html fields without worring about styles

        Copied from survey_result_mail v17.0 to remove unavailable dependency in 19.0
        Source: https://github.com/OCA/survey/blob/17.0/survey_result_mail/models/survey_user_input.py
        """

        def _answer_element(title, value):
            return f"<li><em>{title}</em>: <b>{value}</b></li>"

        given_answers = (given_answers or self.user_input_line_ids).filtered(
            lambda x: not x.skipped
        )
        questions_dict = {}
        for answer in given_answers.filtered(lambda x: x.answer_type != "suggestion"):
            if answer.answer_type == "date":
                value = format_date(self.env, answer.value_date)
            elif answer.answer_type == "datetime":
                value = format_datetime(self.env, answer.value_datetime)
            else:
                value = answer[f"value_{answer.answer_type}"]
            questions_dict[answer.question_id] = _answer_element(
                answer.question_id.title, value
            )
        for answer in given_answers.filtered(
            lambda x: x.question_id.question_type == "simple_choice"
        ):
            questions_dict[answer.question_id] = _answer_element(
                answer.question_id.title,
                answer.suggested_answer_id.value or answer.value_char_box,
            )
        multiple_choice_dict = {}
        for answer in given_answers.filtered(
            lambda x: x.question_id.question_type == "multiple_choice"
        ):
            multiple_choice_dict.setdefault(answer.question_id, [])
            multiple_choice_dict[answer.question_id].append(
                answer.suggested_answer_id.value or answer.value_char_box
            )
        for question, answers in multiple_choice_dict.items():
            questions_dict[question] = _answer_element(
                question.title, " / ".join([x for x in answers if x])
            )
        matrix_dict = {}
        for answer in given_answers.filtered(
            lambda x: x.question_id.question_type == "matrix"
        ):
            matrix_dict.setdefault(answer.question_id, {})
            matrix_dict[answer.question_id].setdefault(answer.matrix_row_id, [])
            matrix_dict[answer.question_id][answer.matrix_row_id].append(
                answer.suggested_answer_id.value or answer.value_char_box
            )
        for question, rows in matrix_dict.items():
            questions_dict[question] = f"<li><em>{question.title}:</em><ul>"
            for row, answers in rows.items():
                questions_dict[question] += _answer_element(
                    row.value, " / ".join([x for x in answers if x])
                )
            questions_dict[question] += "</ul></li>"
        answers_html = "".join([questions_dict[q] for q in given_answers.question_id])
        return Markup(answers_html)

    def _prepare_lead_description(self):
        """We can have surveys without partner. It's handy to have some relevant info
        in the description although the answers are linked themselves.

        :return str: description for the lead
        """
        return self._build_answers_html(
            self.user_input_line_ids.filtered("question_id.show_in_lead_description")
        )

    def _create_opportunity_post_process(self):
        """After creating the lead send an internal message with the input link"""
        self.opportunity_id.message_post_with_source(
            "mail.message_origin_link",
            render_values={"self": self.opportunity_id, "origin": self.survey_id},
            subtype_xmlid="mail.mt_note",
        )

    def _mark_done(self):
        """Generate the opportunity when the survey is submitted"""
        res = super()._mark_done()
        if not self.survey_id.generate_leads:
            return res
        vals = self._prepare_opportunity()
        self.opportunity_id = self.env["crm.lead"].sudo().create(vals)
        self._create_opportunity_post_process()
        return res
