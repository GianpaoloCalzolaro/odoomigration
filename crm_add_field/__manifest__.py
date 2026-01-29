# -*- coding: utf-8 -*-
{
    'name': "CRM Extended Classification",
    'summary': "Extends CRM with business classification fields",
    'description': """
        This module extends the CRM functionality by adding specific fields for business classification.
        It allows to categorize sales opportunities based on:
        - Company type
        - Company size
        - Geographical region
        - Business sector
        - Company structure information (annual volume and employee count)
        
        This categorization enables more detailed analysis and advanced segmentation of commercial opportunities.
    """,
    'author': "Gian Paolo Calzolaro",
    'website': "https://www.infologis.biz",
    'category': 'Sales/CRM',
    'version': '18.0.1.0.0',
    'depends': ['base', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'data/business_sector_data.xml',
        'views/crm_lead_views.xml',
        'views/business_sector_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'assets': {},
}