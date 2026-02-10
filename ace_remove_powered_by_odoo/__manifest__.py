# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Remove Powered By Odoo',
    'version': '19.0.0.1.0',
    'summary': """ 
        Remove powered by odoo, Remove powered by odoo from login page, remove powered by from signup page, remove powered by odoo login screen,
        Hide powered by odoo, odoo powered by hide, odoo powered by remove, disable powered by odoo login screen
    """,
    'sequence': 10,
    'category': 'Extra Tools',
    'author': 'A Cloud ERP',
    'website': 'https://www.aclouderp.com',
    'images': ['static/description/powered_by_odoo.png'],
    'depends': ['base'],
    'data': [
        'views/web_login.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
}
