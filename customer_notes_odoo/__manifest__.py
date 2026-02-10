# -*- coding: utf-8 -*-
{
    'name': 'Customer Diario Portal',
    'summary': 'I clienti possono creare il proprio diario personale nel portale',

    'author': "Elite ERP",
    'website': "https://www.eliteerp.example.com",

    'category': 'portal customer website',

    'version': '19.0.1.6.0',

    'license': 'OPL-1',
    'depends': ['portal', 'website', 'contacts_patient'],

    'data': [
        'security/ir.model.access.csv',
        'security/portal_note_rules.xml',
        'views/views.xml',
        'views/portal_note_backend_views.xml',
        'views/res_partner_note_button.xml',
    ],
    'images': [
        'static/description/main_screenshot.gif',
    ],
}
