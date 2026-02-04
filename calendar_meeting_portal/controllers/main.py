# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class WebsiteCustomerCalendarComment(http.Controller):
        
    @http.route(['/custom_calendar/comment'], type='http', auth="user", website=True)
    def customer_meeting_comment(self, **kw):
        custom_calendar_comment = kw.get('custom_calendar_comment')
        custom_calendar_id = kw.get('custom_calendar_comment_id')
        redirect_url = request.httprequest.referrer
        if custom_calendar_comment and custom_calendar_id:
            record_id = request.env['calendar.event'].sudo().browse(int(custom_calendar_id))
            group_msg = custom_calendar_comment
            record_id.message_post(body=group_msg, message_type='comment')
            try:
                record_id.message_post(
                    body=group_msg,
                    message_type='email',
                    partner_ids=record_id.partner_ids.ids,
                )
            except Exception as e:
                _logger.warning("Failed to send message to partners: %s", e)
        return request.redirect(redirect_url or '/')