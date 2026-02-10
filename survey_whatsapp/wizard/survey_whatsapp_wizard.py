import logging
import time

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.osv.expression import OR

_logger = logging.getLogger(__name__)


class SurveyWhatsappWizard(models.TransientModel):
    _name = "survey.whatsapp.wizard"
    _description = "Survey WhatsApp Send Wizard"

    whatsapp_template_id = fields.Many2one(
        comodel_name="whatsapp.template",
        string="WhatsApp Template",
        required=True,
        domain="[('model', '=', 'survey.user_input'), ('status', '=', 'approved'), ('quality', '!=', 'red'), ('wa_account_id', '!=', False), ('wa_account_id.active', '=', True)]",
    )
    user_input_ids = fields.Many2many(
        comodel_name="survey.user_input",
        string="Selected Participants",
        readonly=True,
    )
    preview_line_ids = fields.One2many(
        comodel_name="survey.whatsapp.wizard.line",
        inverse_name="wizard_id",
        string="Preview",
        readonly=True,
    )
    valid_count = fields.Integer(
        string="Valid Recipients",
        compute="_compute_counts",
    )
    invalid_count = fields.Integer(
        string="Invalid Recipients",
        compute="_compute_counts",
    )
    can_send = fields.Boolean(
        compute="_compute_can_send",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get("active_ids")
        if active_ids:
            user_inputs = self.env["survey.user_input"].browse(active_ids)
            res.setdefault("user_input_ids", [])
            res["user_input_ids"].append((6, 0, user_inputs.ids))
            res["preview_line_ids"] = self._prepare_preview_line_commands(user_inputs)
        self._check_whatsapp_configuration()
        return res

    def _check_whatsapp_configuration(self):
        active_account = self.env["whatsapp.account"].search([("active", "=", True)], limit=1)
        if not active_account:
            raise UserError(
                self.env._("Nessun account WhatsApp attivo configurato. Configura un account nelle impostazioni di WhatsApp.")
            )
        template_domain = self._compute_template_domain()
        if not self.env["whatsapp.template"].search(template_domain, limit=1):
            raise UserError(
                self.env._(
                    "Nessun template WhatsApp approvato disponibile per i partecipanti del sondaggio. "
                    "Crea o approva un template per il modello Survey Responses."
                )
            )

    def _compute_template_domain(self):
        return [
            ("model", "=", "survey.user_input"),
            ("status", "=", "approved"),
            ("quality", "!=", "red"),
            ("wa_account_id", "!=", False),
            ("wa_account_id.active", "=", True),
            "|",
            ("allowed_user_ids", "=", False),
            ("allowed_user_ids", "in", self.env.user.id),
        ]

    def _prepare_preview_line_commands(self, user_inputs):
        commands = [(5, 0, 0)]
        for user_input in user_inputs:
            partner, mobile, is_valid, error = user_input._whatsapp_get_recipient_info()
            commands.append(
                (
                    0,
                    0,
                    {
                        "user_input_id": user_input.id,
                        "partner_id": partner.id if partner else False,
                        "mobile": mobile,
                        "is_valid": is_valid,
                        "error_message": error or False,
                    },
                )
            )
        return commands

    @api.onchange("user_input_ids")
    def _validate_recipients(self):
        domain = {"whatsapp_template_id": self._compute_template_domain()}
        if self.user_input_ids:
            self.preview_line_ids = self._prepare_preview_line_commands(self.user_input_ids)
        else:
            self.preview_line_ids = [(5, 0, 0)]
        return {"domain": domain}

    @api.depends("preview_line_ids.is_valid")
    def _compute_counts(self):
        for wizard in self:
            valid_lines = wizard.preview_line_ids.filtered("is_valid")
            wizard.valid_count = len(valid_lines)
            wizard.invalid_count = len(wizard.preview_line_ids) - len(valid_lines)

    @api.depends("valid_count")
    def _compute_can_send(self):
        for wizard in self:
            wizard.can_send = wizard.valid_count > 0

    def action_send_whatsapp(self):
        self.ensure_one()
        try:
            if not self.whatsapp_template_id:
                raise UserError(self.env._("Seleziona un template WhatsApp approvato."))
            valid_lines = self.preview_line_ids.filtered("is_valid")
            if not valid_lines:
                raise UserError(self.env._("Nessun destinatario valido disponibile per l'invio."))
            message_vals = self._prepare_message_vals(valid_lines)
            if not message_vals:
                raise UserError(self.env._("Nessun messaggio valido da inviare."))
            messages = self.env["whatsapp.message"].create(message_vals)
            messages._send(force_send_by_cron=True)
            return self._show_summary(messages)
        except (UserError, AccessError):
            raise
        except Exception as exc:
            _logger.exception("Unexpected error while sending WhatsApp messages from survey wizard", exc_info=exc)
            raise UserError(
                self.env._(
                    "Si è verificato un errore inatteso durante l'invio dei messaggi WhatsApp. "
                    "Controlla i log di sistema e riprova."
                )
            ) from exc

    def _prepare_message_vals(self, valid_lines):
        self.ensure_one()
        template = self.whatsapp_template_id
        message_vals = []
        for line in valid_lines:
            user_input = line.user_input_id
            formatted_number = user_input._whatsapp_get_formatted_number()
            if not formatted_number:
                continue
            mail_message = self._create_mail_message(user_input)
            message_vals.append(
                {
                    "wa_template_id": template.id,
                    "wa_account_id": template.wa_account_id.id,
                    "mobile_number": line.mobile,
                    "mobile_number_formatted": formatted_number,
                    "state": "outgoing",
                    "mail_message_id": mail_message.id,
                }
            )
        return message_vals

    def _create_mail_message(self, user_input):
        template = self.whatsapp_template_id
        variable_values = template.variable_ids._get_variables_value(user_input)
        body = template._get_formatted_body(variable_values=variable_values)
        partner_ids = user_input.partner_id.ids
        message_vals = {
            "model": "survey.user_input",
            "res_id": user_input.id,
            "message_type": "whatsapp_message",
            "body": body,
            "subtype_id": self.env.ref("mail.mt_note").id,
            "author_id": self.env.user.partner_id.id,
        }
        if partner_ids:
            message_vals["partner_ids"] = [(6, 0, partner_ids)]
        return self.env["mail.message"].create(message_vals)

    def _show_summary(self, sent_messages):
        self.ensure_one()
        time.sleep(2)
        sent_messages.invalidate_recordset()
        sent_messages.read(["state", "failure_type", "failure_reason", "mobile_number", "mobile_number_formatted"])
        success_states = {"sent", "delivered"}
        sent_count = len(sent_messages.filtered(lambda msg: msg.state in success_states))
        error_messages = sent_messages.filtered(lambda msg: msg.state in {"error", "bounced"})
        failure_labels = {
            "account": self.env._("Errore configurazione account WhatsApp"),
            "blacklisted": self.env._("Numero in blacklist"),
            "network": self.env._("Errore di rete"),
            "phone_invalid": self.env._("Formato numero non valido"),
            "template": self.env._("Template non utilizzabile"),
            "unknown": self.env._("Errore sconosciuto"),
            "whatsapp_recoverable": self.env._("Errore temporaneo WhatsApp"),
            "whatsapp_unrecoverable": self.env._("Errore WhatsApp non recuperabile"),
            "outdated_channel": self.env._("Canale non più valido"),
        }
        summary_lines = []
        Partner = self.env["res.partner"]
        for message in error_messages:
            numbers = {num for num in (message.mobile_number, message.mobile_number_formatted) if num}
            domain = []
            for number in numbers:
                domain = OR(domain, [("mobile", "=", number)]) if domain else [("mobile", "=", number)]
            for number in numbers:
                domain = OR(domain, [("phone", "=", number)]) if domain else [("phone", "=", number)]
            partner = Partner.search(domain, limit=1) if domain else Partner.browse()
            partner_name = partner.name if partner else (
                message.mail_message_id.partner_ids[:1].name if message.mail_message_id.partner_ids else ""
            )
            failure_type = message.failure_type or "unknown"
            summary_lines.append(
                (
                    0,
                    0,
                    {
                        "partner_name": partner_name,
                        "mobile": message.mobile_number or message.mobile_number_formatted,
                        "error_type": failure_labels.get(failure_type, failure_type),
                        "error_message": message.failure_reason or "",
                    },
                )
            )
        summary_wizard = self.env["survey.whatsapp.summary.wizard"].create(
            {
                "sent_count": sent_count,
                "error_count": len(error_messages),
                "summary_line_ids": summary_lines,
            }
        )
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("WhatsApp Send Summary"),
            "res_model": "survey.whatsapp.summary.wizard",
            "view_mode": "form",
            "view_id": self.env.ref("survey_whatsapp.view_survey_whatsapp_summary_wizard_form").id,
            "target": "new",
            "res_id": summary_wizard.id,
        }
