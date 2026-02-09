from odoo import models


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    def _whatsapp_get_recipient_info(self):
        self.ensure_one()
        partner = self.partner_id
        if not partner:
            return False, "", False, "Partner mancante"
        mobile = partner.mobile or ""
        if not mobile:
            return partner, "", False, "Numero mobile mancante"
        return partner, mobile, True, False

    def _whatsapp_is_valid_recipient(self):
        self.ensure_one()
        _partner, _mobile, is_valid, _error = self._whatsapp_get_recipient_info()
        return is_valid

    def _whatsapp_get_formatted_number(self):
        self.ensure_one()
        partner = self.partner_id
        if not partner or not partner.mobile:
            return False
        formatted = self._whatsapp_phone_format(
            fpath="partner_id.mobile",
            raise_on_format_error=False,
        )
        return formatted or False
