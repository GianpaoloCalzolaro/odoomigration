# -*- coding: utf-8 -*-
import base64
from odoo import api, fields, models


class SurveySurvey(models.Model):
    _inherit = "survey.survey"


    attachment_count = fields.Integer('Number of Attachments', compute='_compute_attachment_number')

    website_url = fields.Char(string='Website URL', compute='_compute_website_url', readonly=True)

    def _compute_website_url(self):
        for survey in self:
            # Prova a generare l'URL pubblico del sondaggio se il modulo website è installato
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if hasattr(survey, 'id') and base_url:
                survey.website_url = f"{base_url}/survey/fill/{survey.access_token}"
            else:
                survey.website_url = ''

    def _compute_attachment_number(self):
        for survey in self:
            survey.attachment_count = self.env['survey.binary'].search_count([
                ('user_input_line_id.survey_id', '=', survey.id),
                ('user_input_line_id.user_input_id.test_entry', '=', False)
            ])

    def action_survey_user_input_attachment(self):
        self.ensure_one()
        return {
            'name': self.env._('Documents'),
            'domain': [('user_input_line_id.survey_id', '=', self.id), ('user_input_line_id.user_input_id.test_entry', '=', False)],
            'res_model': 'survey.binary',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
        }

class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    attachment_count = fields.Integer('Number of Attachments', compute='_compute_attachment_number')

    def _save_lines(self, question, answer, comment=None, overwrite_existing=True):
        if question.question_type == 'upload_file':
            old_answers = self.env['survey.user_input.line'].search([
                ('user_input_id', '=', self.id),
                ('question_id', '=', question.id)
            ])
            return self._save_line_upload_files(question, old_answers, answer, comment)
        return super()._save_lines(question, answer, comment, overwrite_existing)

    def _compute_attachment_number(self):
        for user_input in self:
            user_input.attachment_count = self.env['survey.binary'].search_count([
                ('user_input_line_id.user_input_id', '=', user_input.id),
                ('user_input_line_id.user_input_id.test_entry', '=', False),
            ])

    def action_survey_user_input_attachment(self):
        self.ensure_one()
        return {
            'name': self.env._('Documents'),
            'domain': [('user_input_line_id.user_input_id', '=', self.id), ('user_input_line_id.user_input_id.test_entry', '=', False)],
            'res_model': 'survey.binary',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
        }

    def _save_line_upload_files(self, question, old_answers, answers, comment):
        vals = {
            'user_input_id': self.id,
            'question_id': question.id,
            'skipped': False,
            'answer_type': question.question_type,
        }
        if answers and answers.get('values') and answers.get('is_answer_update'):
            user_binary_lines = [
                    (0, 0, {'binary_data': answer.get('data'), 'binary_filename': answer.get('file_name')})
                    for answer in answers.get('values')
                ]
            vals.update({'user_binary_line': user_binary_lines})
            if old_answers:
                old_answers.unlink()
            old_answers.create(vals)
        else:
            vals.update({'answer_type': None, 'skipped': True})

        return old_answers

class SurveyBinary(models.Model):
    _name = 'survey.binary'
    _description = "Survey Input Binary Files"
    _rec_name = 'binary_filename'

    user_input_line_id = fields.Many2one('survey.user_input.line', string="Answers")
    binary_filename = fields.Char(string="Upload File Name")
    binary_data = fields.Binary(string="Upload File Data")
    partner_id = fields.Many2one('res.partner', string='Partner', related='user_input_line_id.user_input_id.partner_id', readonly=True)


class SurveyUserInputLine(models.Model):
    _inherit = "survey.user_input.line"

    user_binary_line = fields.One2many('survey.binary', 'user_input_line_id', string='Binary Files')
    answer_type = fields.Selection(selection_add=[('upload_file', 'Upload File')])
    value_upload_file = fields.Char('Upload Multiple File')

    @api.constrains('skipped', 'answer_type')
    def _check_answer_type_skipped(self):
        for line in self:
            if line.answer_type != 'upload_file':
                return super(SurveyUserInputLine, line)._check_answer_type_skipped()

    @api.depends(
        'answer_type', 'value_text_box', 'value_numerical_box',
        'value_char_box', 'value_date', 'value_datetime',
        'suggested_answer_id.value', 'matrix_row_id.value',
    )
    def _compute_display_name(self):
        super()._compute_display_name()
        for line in self:
            if line.answer_type == 'upload_file' and len(line.user_binary_line) > 0:
                line.display_name = 'File Upload ('+ str(len(line.user_binary_line)) + ')'

