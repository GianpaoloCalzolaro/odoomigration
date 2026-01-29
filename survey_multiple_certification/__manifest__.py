{
    'name': 'Survey Multiple Certification',
    'version': '18.0.1.0.2',  # Versione compatibile con Odoo 18 - Fix can_retake
    'category': 'Marketing/Surveys',
    'summary': 'Add multiple certification thresholds to surveys',
    'description': """
        Questo modulo permette di aggiungere più soglie di certificazione ai sondaggi Odoo.
        Ideale per gestire livelli diversi di certificazione in base ai punteggi ottenuti dagli utenti.
    """,
    'author': 'Gian Paolo Calzolaro',
    'website': 'www.infologis.biz',
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
    'installable': True,
    'auto_install': False,
}
