# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from odoo import models

_logger = logging.getLogger(__name__)


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    def _prepare_applicant(self):
        self.ensure_one()
        elegible_inputs = self.user_input_line_ids.filtered(
            lambda x: x.question_id.hr_applicant_field and not x.skipped
        )
        basic_inputs = elegible_inputs.filtered(
            lambda x: x.answer_type not in {"suggestion", "upload_file"}
            and x.question_id.hr_applicant_field.name not in {"comment"}
        )
        vals = {
            line.question_id.hr_applicant_field.name: line[f"value_{line.answer_type}"]
            for line in basic_inputs
        }
        for line in elegible_inputs - basic_inputs:
            field_name = line.question_id.hr_applicant_field.name
            if line.question_id.hr_applicant_field.ttype == "many2one":
                resource_ref = line.suggested_answer_id.hr_applicant_field_resource_ref
                if resource_ref:
                    vals[field_name] = resource_ref.id
            elif line.question_id.hr_applicant_field.ttype == "many2many":
                vals.setdefault(field_name, [])
                resource_ref = line.suggested_answer_id.hr_applicant_field_resource_ref
                if resource_ref:
                    vals[field_name] += [
                        (4, resource_ref.id)
                    ]
            # Gestione speciale per campi binary (file upload)
            elif (
                line.question_id.hr_applicant_field.ttype == "binary"
                and line.answer_type == "upload_file"
            ):
                # Debug: preferisci i dati dal suggested answer, ma fai fallback
                # sul valore diretto della linea se presente. Logga entrambe le
                # possibilità per facilitare il debug in produzione.
                try:
                    file_from_suggested = getattr(line.suggested_answer_id, "file_upload_data", False)
                except Exception:
                    file_from_suggested = False
                try:
                    file_from_line = line[f"value_{line.answer_type}"]
                except Exception:
                    file_from_line = False
                # Fallback: alcuni survey salvano i binary in una relazione user_binary_line
                try:
                    file_from_user_binary = False
                    if getattr(line, "user_binary_line", False):
                        ub = line.user_binary_line[:1]
                        if ub:
                            ub = ub[0]
                            # prefer explicit binary_data field from survey.binary
                            file_from_user_binary = (
                                getattr(ub, "binary_data", False)
                                or getattr(ub, "file_upload_data", False)
                                or getattr(ub, "file", False)
                                or getattr(ub, "datas", False)
                                or getattr(ub, "binary", False)
                                or getattr(ub, "value", False)
                            )
                            # optional: filename available as binary_filename
                            file_from_user_binary_filename = getattr(ub, "binary_filename", False)
                except Exception:
                    file_from_user_binary = False
                _logger.info(
                    "Binary mapping (_prepare_applicant) debug: question=%s field=%s answer_type=%s has_suggested=%s has_line_value=%s has_user_binary=%s",
                    line.question_id.id,
                    field_name,
                    line.answer_type,
                    bool(file_from_suggested),
                    bool(file_from_line),
                    bool(file_from_user_binary),
                )
                vals[field_name] = file_from_suggested or file_from_line or file_from_user_binary
            # Gestione speciale per campi selection
            elif (
                line.question_id.hr_applicant_field.ttype == "selection"
                and line.answer_type == "suggestion"
            ):
                vals[field_name] = (
                    line.suggested_answer_id.selection_value
                    or line.suggested_answer_id.value
                )
            elif field_name == "comment":
                vals.setdefault("comment", "")
                value = (
                    line.suggested_answer_id.value
                    if line.answer_type == "suggestion"
                    else line[f"value_{line.answer_type}"]
                )
                vals["comment"] += f"\n{line.question_id.title}: {value}"
            else:
                if line.question_id.question_type == "multiple_choice":
                    vals[field_name] = vals.get(field_name, "") + line.suggested_answer_id.value
                else:
                    vals[field_name] = line.suggested_answer_id.value
        vals["generating_survey_user_input_id"] = self.id
        job = self.survey_id.job_position_id
        if job:
            vals.setdefault("job_id", job.id)
            stage = self._get_initial_stage(job)
            if stage:
                vals.setdefault("stage_id", stage.id)
            vals.setdefault("user_id", job.user_id.id)
        return vals

    def _get_existing_applicant(self, email, limit=1):
        return self.env["hr.applicant"].search([
            ("email_from", "=ilike", email),
            "|",
            ("generating_survey_user_input_id", "=", False),
            ("generating_survey_user_input_id", "=", self.id)
        ], limit=limit)

    def _create_applicant_post_process(self, applicant):
        applicant.message_post_with_source(
            "mail.message_origin_link",
            render_values={"self": applicant, "origin": self.survey_id},
            subtype_xmlid="mail.mt_note",
        )

    def _get_initial_stage(self, job):
        return job._get_first_stage()

    def _prepare_partner(self):
        """Extract partner values from the answers"""
        self.ensure_one()
        elegible_inputs = self.user_input_line_ids.filtered(
            lambda x: x.question_id.res_partner_field and not x.skipped
        )
        basic_inputs = elegible_inputs.filtered(
            lambda x: x.answer_type not in {"suggestion", "upload_file"}
            and x.question_id.res_partner_field.name not in {"comment", "company_name"}
        )
        vals = {
            line.question_id.res_partner_field.name: line[f"value_{line.answer_type}"]
            for line in basic_inputs
        }
        for line in elegible_inputs - basic_inputs:
            field_name = line.question_id.res_partner_field.name
            if line.question_id.res_partner_field.ttype == "many2one":
                vals[
                    field_name
                ] = line.suggested_answer_id.res_partner_field_resource_ref.id
            elif line.question_id.res_partner_field.ttype == "many2many":
                vals.setdefault(field_name, [])
                vals[field_name] += [
                    (4, line.suggested_answer_id.res_partner_field_resource_ref.id)
                ]
            # Gestione speciale per campi binary (file upload)
            elif (
                line.question_id.res_partner_field.ttype == "binary"
                and line.answer_type == "upload_file"
            ):
                try:
                    file_from_suggested = getattr(line.suggested_answer_id, "file_upload_data", False)
                except Exception:
                    file_from_suggested = False
                try:
                    file_from_line = line[f"value_{line.answer_type}"]
                except Exception:
                    file_from_line = False
                try:
                    file_from_user_binary = False
                    if getattr(line, "user_binary_line", False):
                        ub = line.user_binary_line[:1]
                        if ub:
                            ub = ub[0]
                            file_from_user_binary = (
                                getattr(ub, "binary_data", False)
                                or getattr(ub, "file_upload_data", False)
                                or getattr(ub, "file", False)
                                or getattr(ub, "datas", False)
                                or getattr(ub, "binary", False)
                                or getattr(ub, "value", False)
                            )
                            file_from_user_binary_filename = getattr(ub, "binary_filename", False)
                except Exception:
                    file_from_user_binary = False
                _logger.info(
                    "Binary mapping (_prepare_partner) debug: question=%s field=%s answer_type=%s has_suggested=%s has_line_value=%s has_user_binary=%s",
                    line.question_id.id,
                    field_name,
                    line.answer_type,
                    bool(file_from_suggested),
                    bool(file_from_line),
                    bool(file_from_user_binary),
                )
                vals[field_name] = file_from_suggested or file_from_line or file_from_user_binary
            # Gestione speciale per campi selection
            elif (
                line.question_id.res_partner_field.ttype == "selection"
                and line.answer_type == "suggestion"
            ):
                vals[field_name] = (
                    line.suggested_answer_id.selection_value
                    or line.suggested_answer_id.value
                )
            # We'll use the comment field to add any other infos
            elif field_name == "comment":
                vals.setdefault("comment", "")
                value = (
                    line.suggested_answer_id.value
                    if line.answer_type == "suggestion"
                    else line[f"value_{line.answer_type}"]
                )
                vals["comment"] += f"\n{line.question_id.title}: {value}"
            # Create the parent company
            elif field_name == "company_name" and self.survey_id.create_parent_contact:
                if line[f"value_{line.answer_type}"]:
                    vals["parent_id"] = (
                        self.env["res.partner"]
                        .create(
                            {
                                "name": line[f"value_{line.answer_type}"],
                                "company_type": "company",
                            }
                        )
                        .id
                    )
            else:
                if line.question_id.question_type == "multiple_choice":
                    if not vals.get(field_name):
                        vals[field_name] = line.suggested_answer_id.value
                    else:
                        vals[field_name] += line.suggested_answer_id.value
                else:
                    vals[field_name] = line.suggested_answer_id.value
        vals["generating_survey_user_input_id"] = self.id
        return vals

    def _create_contact_post_process(self, partner):
        """After creating the lead send an internal message with the input link"""
        partner.message_post_with_source(
            "mail.message_origin_link",
            render_values={"self": partner, "origin": self.survey_id},
            subtype_xmlid="mail.mt_note",
        )

    def _get_existing_partner(self, email, limit=1):
        """Hook method that can be used to change the behavior of contact generation"""
        return self.env["res.partner"].search([
            ("email", "=ilike", email),
            "|",
            ("generating_survey_user_input_id", "=", False),
            ("generating_survey_user_input_id", "=", self.id)
        ], limit=limit)

    def _mark_done(self):
        """Generate partner or applicant based on survey configuration"""
        result = super()._mark_done()
        for user_input in self.filtered(
            lambda r: r.survey_id.generation_type == "contact" and not r.partner_id
        ):
            vals = user_input._prepare_partner()
            partner = False
            email = vals.get("email")
            if email:
                partner = self._get_existing_partner(email)
            if not partner:
                partner = self.env["res.partner"].create(vals)
                self._create_contact_post_process(partner)
            user_input.update({"partner_id": partner.id, "email": partner.email})

        for user_input in self.filtered(lambda r: r.survey_id.generation_type == "applicant"):
            # Verifica se esiste già un applicant per questo user_input
            existing_applicant = self.env["hr.applicant"].search([
                ("generating_survey_user_input_id", "=", user_input.id)
            ], limit=1)
            if existing_applicant:
                user_input.update({
                    "partner_id": existing_applicant.partner_id.id,
                    "email": existing_applicant.email_from,
                    "applicant_id": existing_applicant.id,
                })
                continue

            # Prepara i valori dall'applicant field mapping
            vals = user_input._prepare_applicant()

            # Prepara i valori extra dal candidate field mapping
            # (ora puntano a hr.applicant) e fondili
            extra_vals = user_input._prepare_candidate_as_applicant()
            if extra_vals:
                extra_vals.pop("generating_survey_user_input_id", None)
                for key, value in extra_vals.items():
                    if key not in vals or not vals[key]:
                        vals[key] = value

            # Cerca applicant esistente per email
            applicant = False
            email = vals.get("email_from")
            if email:
                applicant = user_input._get_existing_applicant(email)
                if applicant:
                    applicant.write(vals)
                    user_input.update({
                        "partner_id": applicant.partner_id.id,
                        "email": applicant.email_from,
                        "applicant_id": applicant.id,
                    })
                    continue

            # Crea nuovo applicant
            applicant = self.env["hr.applicant"].create(vals)
            self._create_applicant_post_process(applicant)
            user_input.update({
                "partner_id": applicant.partner_id.id,
                "email": applicant.email_from,
                "applicant_id": applicant.id,
            })

        return result

    def _prepare_candidate_as_applicant(self):
        """Extract extra applicant values from candidate-mapped questions"""
        self.ensure_one()
        elegible_inputs = self.user_input_line_ids.filtered(
            lambda x: x.question_id.hr_candidate_field and not x.skipped
        )
        basic_inputs = elegible_inputs.filtered(
            lambda x: x.answer_type not in {"suggestion", "upload_file"}
            and x.question_id.hr_candidate_field.name not in {"comment"}
        )
        vals = {
            line.question_id.hr_candidate_field.name: line[f"value_{line.answer_type}"]
            for line in basic_inputs
        }
        for line in elegible_inputs - basic_inputs:
            field_name = line.question_id.hr_candidate_field.name
            if line.question_id.hr_candidate_field.ttype == "many2one":
                vals[field_name] = line.suggested_answer_id.hr_candidate_field_resource_ref.id
            elif line.question_id.hr_candidate_field.ttype == "many2many":
                vals.setdefault(field_name, [])
                vals[field_name] += [
                    (4, line.suggested_answer_id.hr_candidate_field_resource_ref.id)
                ]
            # Gestione speciale per campi binary (file upload)
            elif (
                line.question_id.hr_candidate_field.ttype == "binary"
                and line.answer_type == "upload_file"
            ):
                try:
                    file_from_suggested = getattr(line.suggested_answer_id, "file_upload_data", False)
                except Exception:
                    file_from_suggested = False
                try:
                    file_from_line = line[f"value_{line.answer_type}"]
                except Exception:
                    file_from_line = False
                try:
                    file_from_user_binary = False
                    if getattr(line, "user_binary_line", False):
                        ub = line.user_binary_line[:1]
                        if ub:
                            ub = ub[0]
                            file_from_user_binary = (
                                getattr(ub, "binary_data", False)
                                or getattr(ub, "file_upload_data", False)
                                or getattr(ub, "file", False)
                                or getattr(ub, "datas", False)
                                or getattr(ub, "binary", False)
                                or getattr(ub, "value", False)
                            )
                            file_from_user_binary_filename = getattr(ub, "binary_filename", False)
                except Exception:
                    file_from_user_binary = False
                _logger.info(
                    "Binary mapping (_prepare_candidate) debug: question=%s field=%s answer_type=%s has_suggested=%s has_line_value=%s has_user_binary=%s",
                    line.question_id.id,
                    field_name,
                    line.answer_type,
                    bool(file_from_suggested),
                    bool(file_from_line),
                    bool(file_from_user_binary),
                )
                vals[field_name] = file_from_suggested or file_from_line or file_from_user_binary
            # Gestione speciale per campi selection
            elif (
                line.question_id.hr_candidate_field.ttype == "selection"
                and line.answer_type == "suggestion"
            ):
                vals[field_name] = (
                    line.suggested_answer_id.selection_value
                    or line.suggested_answer_id.value
                )
            elif field_name == "comment":
                vals.setdefault("comment", "")
                value = (
                    line.suggested_answer_id.value
                    if line.answer_type == "suggestion"
                    else line[f"value_{line.answer_type}"]
                )
                vals["comment"] += f"\n{line.question_id.title}: {value}"
            else:
                if line.question_id.question_type == "multiple_choice":
                    vals[field_name] = vals.get(field_name, "") + line.suggested_answer_id.value
                else:
                    vals[field_name] = line.suggested_answer_id.value
        
        # Solo aggiungere il survey user input ID se ci sono altri valori
        if vals:
            vals["generating_survey_user_input_id"] = self.id
            
        # Aggiunge company_id se configurato
        if vals and self.survey_id.job_position_id.company_id:
            vals.setdefault(
                "company_id", self.survey_id.job_position_id.company_id.id
            )
        return vals
