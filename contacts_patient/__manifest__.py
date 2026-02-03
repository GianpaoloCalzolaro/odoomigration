# -*- coding: utf-8 -*-
{
    'name': 'Contacts Patient',
    'version': '19.0.1.0.0',
    'category': 'Contacts',
    'summary': 'Extend contacts with patient information',
    'description': """
        This module extends the contacts app with clinical information for patients.
        It adds medical information, diagnosis, and treatment fields.
    """,
    'author': 'Gian Paolo Calzolaro',
    'website': 'www.infologis.biz',
    'depends': ['contacts', 'hr', 'website', 'portal', 'survey'],
    'data': [
        'security/contacts_patient_security.xml',
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
        'views/clinical_observation_views.xml',
        'views/clinical_sheet_view.xml',
        'views/clinical_sheet_portal.xml',
        'views/clinical_observation_portal.xml',
        'views/res_partner_views.xml',
        'views/contacts_portal_templates.xml',
        'views/contact_detail_view.xml',
        'views/survey_responses_portal.xml',
        'views/contact_edit_form.xml',
        'views/portal_equipe_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'contacts_patient/static/src/js/clinical_portal.js',
            'contacts_patient/static/src/css/clinical_portal.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}