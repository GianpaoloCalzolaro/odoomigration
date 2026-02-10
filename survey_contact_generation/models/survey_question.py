# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SurveyQuestion(models.Model):
    _inherit = "survey.question"

    allowed_field_domain = fields.Char(
        compute="_compute_allowed_field_domain",
    )
    allowed_applicant_field_domain = fields.Char(
        compute="_compute_allowed_applicant_field_domain",
    )
    allowed_candidate_field_domain = fields.Char(
        compute="_compute_allowed_candidate_field_domain",
    )
    res_partner_field = fields.Many2one(
        string="Contact field",
        comodel_name="ir.model.fields",
    )
    hr_applicant_field = fields.Many2one(
        string="Applicant field",
        comodel_name="ir.model.fields",
    )
    hr_candidate_field = fields.Many2one(
        string="Candidate field",
        comodel_name="ir.model.fields",
    )

    @api.depends("question_type", "survey_id.generation_type")
    def _compute_allowed_field_domain(self):
        type_mapping = {
            "char_box": ["char", "text"],
            "text_box": ["html"],
            "numerical_box": ["integer", "float", "html", "char"],
            "date": ["date", "text", "char"],
            "datetime": ["datetime", "html", "char"],
            "simple_choice": ["many2one", "html", "char", "selection"],
            "multiple_choice": ["many2many", "html", "char"],
            "upload_file": ["binary"],
        }
        for record in self:
            allowed_types = type_mapping.get(record.question_type, [])
            domain = [
                ("model", "=", "res.partner"),
                ("ttype", "in", allowed_types),
                ("store", "=", True),
                ("readonly", "=", False),
            ]
            record.allowed_field_domain = str(domain)

    @api.depends("question_type")
    def _compute_allowed_applicant_field_domain(self):
        type_mapping = {
            "char_box": ["char", "text"],
            "text_box": ["html"],
            "numerical_box": ["integer", "float", "html", "char"],
            "date": ["date", "text", "char"],
            "datetime": ["datetime", "html", "char"],
            "simple_choice": ["many2one", "html", "char", "selection"],
            "multiple_choice": ["many2many", "html", "char"],
            "upload_file": ["binary"],
        }
        for record in self:
            allowed_types = type_mapping.get(record.question_type, [])
            domain = [
                ("model", "=", "hr.applicant"),
                ("ttype", "in", allowed_types),
                ("store", "=", True),
                ("readonly", "=", False),
            ]
            record.allowed_applicant_field_domain = str(domain)

    @api.depends("question_type")
    def _compute_allowed_candidate_field_domain(self):
        type_mapping = {
            "char_box": ["char", "text"],
            "text_box": ["html"],
            "numerical_box": ["integer", "float", "html", "char"],
            "date": ["date", "text", "char"],
            "datetime": ["datetime", "html", "char"],
            "simple_choice": ["many2one", "html", "char", "selection"],
            "multiple_choice": ["many2many", "html", "char"],
            "upload_file": ["binary"],
        }
        for record in self:
            allowed_types = type_mapping.get(record.question_type, [])
            domain = [
                ("model", "=", "hr.applicant"),
                ("ttype", "in", allowed_types),
                ("store", "=", True),
                ("readonly", "=", False),
            ]
            record.allowed_candidate_field_domain = str(domain)

    def _get_selection_values(self, field):
        """Extract selection values from an ir.model.fields record"""
        if not field or field.ttype != "selection":
            return []

        # Metodo 1: selection_ids (alcuni campi custom)
        if getattr(field, "selection_ids", False):
            return [(sel.value, sel.name) for sel in field.selection_ids]
        
        # Metodo 2: field.selection (stringa)
        elif field.selection:
            try:
                import ast
                selection_list = ast.literal_eval(field.selection)
                if isinstance(selection_list, list):
                    return selection_list
            except Exception:
                pass

        # Metodo 3: campo dal modello python
        try:
            model_obj = self.env[field.model]
            field_obj = model_obj._fields.get(field.name)
            if field_obj and hasattr(field_obj, "selection"):
                if callable(field_obj.selection):
                    selection_values = field_obj.selection(model_obj)
                else:
                    selection_values = field_obj.selection
                
                # Assicurati che sia una lista di tuple
                if isinstance(selection_values, (list, tuple)):
                    return list(selection_values)
        except Exception:
            pass

        return []

    @api.onchange("res_partner_field")
    def _onchange_res_partner_field_selection(self):
        """Quando viene selezionato un campo selection, aggiorna automaticamente le scelte"""
        if (
            self.res_partner_field
            and self.res_partner_field.ttype == "selection"
            and self.question_type == "simple_choice"
        ):
            selection_values = self._get_selection_values(self.res_partner_field)
            if selection_values:
                self.suggested_answer_ids = [(5, 0, 0)]
                new_answers = []
                for sequence, (value, label) in enumerate(selection_values, 1):
                    _logger.info("Selection value: %s, label: %s", value, label)
                    
                    new_answers.append(
                        (
                            0,
                            0,
                            {
                                "sequence": sequence,
                                "value": label,
                                "selection_value": value,
                            },
                        )
                    )
                self.suggested_answer_ids = new_answers

    @api.onchange("hr_applicant_field")
    def _onchange_hr_applicant_field(self):
        """Reset candidate field when applicant field is set and handle selection fields"""
        if self.hr_applicant_field:
            self.hr_candidate_field = False
            
        if (
            self.hr_applicant_field
            and self.hr_applicant_field.ttype == "selection"
            and self.question_type == "simple_choice"
        ):
            selection_values = self._get_selection_values(self.hr_applicant_field)
            if selection_values:
                self.suggested_answer_ids = [(5, 0, 0)]
                new_answers = []
                for sequence, (value, label) in enumerate(selection_values, 1):
                    _logger.info("Selection value: %s, label: %s", value, label)
                    
                    new_answers.append(
                        (
                            0,
                            0,
                            {
                                "sequence": sequence,
                                "value": label,
                                "selection_value": value,
                            },
                        )
                    )
                self.suggested_answer_ids = new_answers

    @api.onchange("hr_candidate_field")
    def _onchange_hr_candidate_field(self):
        """Reset applicant field when candidate field is set and handle selection fields"""
        if self.hr_candidate_field:
            self.hr_applicant_field = False
            
        if (
            self.hr_candidate_field
            and self.hr_candidate_field.ttype == "selection"
            and self.question_type == "simple_choice"
        ):
            selection_values = self._get_selection_values(self.hr_candidate_field)
            if selection_values:
                self.suggested_answer_ids = [(5, 0, 0)]
                new_answers = []
                for sequence, (value, label) in enumerate(selection_values, 1):
                    _logger.info("Selection value: %s, label: %s", value, label)
                    
                    new_answers.append(
                        (
                            0,
                            0,
                            {
                                "sequence": sequence,
                                "value": label,
                                "selection_value": value,
                            },
                        )
                    )
                self.suggested_answer_ids = new_answers

    @api.constrains("hr_applicant_field", "hr_candidate_field")
    def _check_unique_field_mapping(self):
        """Verifica che lo stesso campo survey non sia mappato su entrambi i modelli"""
        for record in self:
            if record.hr_applicant_field and record.hr_candidate_field:
                raise ValidationError(
                    _("Non è possibile mappare la stessa domanda su entrambi i campi Applicant e Candidate. "
                      "Scegliere solo uno dei due campi.")
                )

    @api.constrains("hr_candidate_field")
    def _check_candidate_name_required(self):
        """Assicura che il nome del candidato sia obbligatorio per la generazione di applicant"""
        for record in self:
            if (record.survey_id.generation_type == "applicant" and 
                record.hr_candidate_field and 
                not record.survey_id.question_ids.filtered(
                    lambda q: q.hr_candidate_field and q.hr_candidate_field.name == "partner_name"
                )):
                # Controllo se almeno una domanda mappa il campo partner_name del candidato
                has_name_mapping = any(
                    q.hr_candidate_field and q.hr_candidate_field.name == "partner_name"
                    for q in record.survey_id.question_ids
                )
                if not has_name_mapping:
                    pass  # Solo un warning, non bloccare la validazione

    def action_regenerate_selection_values(self):
        """Rigenera i valori di selection per le risposte suggerite"""
        for record in self:
            if record.question_type == "simple_choice":
                field_to_check = None
                if record.hr_applicant_field and record.hr_applicant_field.ttype == "selection":
                    field_to_check = record.hr_applicant_field
                elif record.hr_candidate_field and record.hr_candidate_field.ttype == "selection":
                    field_to_check = record.hr_candidate_field
                elif record.res_partner_field and record.res_partner_field.ttype == "selection":
                    field_to_check = record.res_partner_field
                
                if field_to_check:
                    selection_values = record._get_selection_values(field_to_check)
                    if selection_values:
                        # Aggiorna le risposte esistenti senza selection_value
                        answers_to_update = record.suggested_answer_ids.filtered(
                            lambda x: not x.selection_value
                        )
                        for answer in answers_to_update:
                            # Trova il valore tecnico corrispondente alla label
                            for value, label in selection_values:
                                if answer.value == label:
                                    answer.selection_value = value
                                    break


class SurveyQuestionAnswer(models.Model):
    _inherit = "survey.question.answer"

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)
        if (
            not result.get("res_partner_field")
            or "res_partner_field_resource_ref" not in fields
        ):
            return result
        partner_field = self.env["ir.model.fields"].browse(result["res_partner_field"])
        # Otherwise we'll just use the value (char, text)
        if partner_field.ttype not in {"many2one", "many2many"}:
            return result
        res = self.env[partner_field.relation].search([], limit=1)
        if res:
            result[
                "res_partner_field_resource_ref"
            ] = f"{partner_field.relation},{res.id}"
        return result

    @api.model
    def _selection_res_partner_field_resource_ref(self):
        return [(model.model, model.name) for model in self.env["ir.model"].search([])]

    @api.model
    def _selection_hr_candidate_field_resource_ref(self):
        return [(model.model, model.name) for model in self.env["ir.model"].search([])]

    @api.model
    def _selection_hr_applicant_field_resource_ref(self):
        return [(model.model, model.name) for model in self.env["ir.model"].search([])]

    res_partner_field = fields.Many2one(related="question_id.res_partner_field")
    res_partner_field_resource_ref = fields.Reference(
        string="Contact field value",
        selection="_selection_res_partner_field_resource_ref",
    )
    hr_applicant_field = fields.Many2one(related="question_id.hr_applicant_field")
    hr_applicant_field_resource_ref = fields.Reference(
        string="Applicant field value",
        selection="_selection_hr_applicant_field_resource_ref",
    )
    hr_candidate_field = fields.Many2one(related="question_id.hr_candidate_field")
    hr_candidate_field_resource_ref = fields.Reference(
        string="Candidate field value",
        selection="_selection_hr_candidate_field_resource_ref",
    )
    selection_value = fields.Char(
        help="Technical value for selection fields",
    )
    file_upload_data = fields.Binary(
        string="File Data",
        help="Binary data for uploaded files",
    )
    file_upload_filename = fields.Char(
        string="File Name",
        help="Original filename for uploaded files",
    )

    @api.onchange("res_partner_field_resource_ref")
    def _onchange_res_partner_field_resource_ref(self):
        """Set the default value as the product name, although we can change it"""
        if (
            self.res_partner_field
            and self.res_partner_field.ttype == "selection"
        ):
            return
        if self.res_partner_field_resource_ref:
            self.value = self.res_partner_field_resource_ref.display_name or ""

    @api.onchange("hr_applicant_field_resource_ref")
    def _onchange_hr_applicant_field_resource_ref(self):
        if self.hr_applicant_field_resource_ref:
            self.value = self.hr_applicant_field_resource_ref.display_name or ""

    @api.onchange("hr_candidate_field_resource_ref")
    def _onchange_hr_candidate_field_resource_ref(self):
        if self.hr_candidate_field_resource_ref:
            self.value = self.hr_candidate_field_resource_ref.display_name or ""

    @api.onchange("res_partner_field")
    def _onchange_res_partner_field(self):
        if self.res_partner_field:
            self.hr_applicant_field = False
            self.hr_candidate_field = False
            self.hr_applicant_field_resource_ref = False
            self.hr_candidate_field_resource_ref = False

    @api.onchange("hr_applicant_field")
    def _onchange_hr_applicant_field(self):
        if self.hr_applicant_field:
            self.res_partner_field = False
            self.hr_candidate_field = False
            self.res_partner_field_resource_ref = False
            self.hr_candidate_field_resource_ref = False

    @api.onchange("hr_candidate_field")
    def _onchange_hr_candidate_field(self):
        if self.hr_candidate_field:
            self.res_partner_field = False
            self.hr_applicant_field = False
            self.res_partner_field_resource_ref = False
            self.hr_applicant_field_resource_ref = False

    @api.onchange("file_upload_data")
    def _onchange_file_upload_data(self):
        """Handle file upload for binary fields"""
        if self.file_upload_data and self.question_id.question_type == "upload_file":
            # Set a default filename if not provided
            if not self.file_upload_filename:
                self.file_upload_filename = "uploaded_file"

    @api.model
    def create(self, vals):
        """Override create to ensure selection_value is set for selection fields"""
        answer = super().create(vals)
        answer._ensure_selection_value()
        return answer

    def write(self, vals):
        """Override write to ensure selection_value is set for selection fields"""
        result = super().write(vals)
        if 'value' in vals:
            self._ensure_selection_value()
        return result

    def _ensure_selection_value(self):
        """Ensure that selection_value is set for selection fields"""
        for answer in self:
            if answer.question_id and answer.value and not answer.selection_value:
                field_to_check = None
                if answer.hr_applicant_field and answer.hr_applicant_field.ttype == "selection":
                    field_to_check = answer.hr_applicant_field
                elif answer.hr_candidate_field and answer.hr_candidate_field.ttype == "selection":
                    field_to_check = answer.hr_candidate_field
                elif answer.res_partner_field and answer.res_partner_field.ttype == "selection":
                    field_to_check = answer.res_partner_field
                
                if field_to_check:
                    selection_values = answer.question_id._get_selection_values(field_to_check)
                    for value, label in selection_values:
                        if answer.value == label:
                            answer.selection_value = value
                            break

