# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Portal for Calendar Meetings for Attendees",
    'version': '19.0.1.0.0',
    'license': 'Other proprietary',
    'price': 39.0,
    'currency': 'EUR',
    'summary':  """Calendar Meeting Show to Attendees Portal Users / Portal for Calendar Meetings for Attendees""",
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/image.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/calendar_meeting_portal/1018',#'https://youtu.be/kuh2AWBuT8U',
    'category': 'Productivity/Calendar',
    'depends': [
        'calendar',
        'portal',
        'hr',
        'website'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/calendar_event_security.xml',
        'data/calendar_event_outcome_data.xml',
        'views/calendar_event_outcome_views.xml',
        'views/calendar_event_views.xml',
        'views/customer_calendar_template.xml',
        'views/calendar_portal_templates.xml',
        'views/portal_meeting_create.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/calendar_meeting_portal/static/src/js/calendar_comment.js',
            '/calendar_meeting_portal/static/src/js/meeting_create_validation.js',
        ],
    },
}
