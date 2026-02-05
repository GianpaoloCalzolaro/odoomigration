{
    'name': 'Survey Multiple Certification',
    'version': '19.0.1.0.0',  # Migrazione a Odoo 19
    'category': 'Marketing/Surveys',
    'summary': 'Add multiple certification thresholds to surveys',
    'author': 'Gian Paolo Calzolaro',
    'website': 'https://www.infologis.biz',
    'maintainer': 'Gian Paolo Calzolaro',
    'support': 'info@infologis.biz',
    'depends': ['survey', 'gamification', 'web', 'website'],
    'data': [
        'security/survey_multiple_certification_security.xml',
        'security/ir.model.access.csv',
        'views/survey_certification_threshold_views.xml',
        'views/survey_survey_views.xml',
        'views/survey_user_input_views.xml',
        'views/survey_templates.xml',
        'wizard/survey_threshold_wizard_views.xml',
    ],
    'license': 'LGPL-3',
    'application': True,
}
