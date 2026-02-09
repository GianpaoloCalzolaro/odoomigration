{
    "name": "Survey WhatsApp Integration",
    "summary": "Send WhatsApp template messages to survey participants.",
    "description": """
Integrate Odoo Survey with WhatsApp Enterprise to send approved template messages to survey participants.
""",
    "version": "18.0.1.0.0",
    "category": "Marketing/Surveys",
    "website": "wwww.infologis.biz",
    "author": "infologis",
    "depends": [
        "survey",
        "whatsapp",
    ],
    "data": [
        "security/survey_whatsapp_security.xml",
        "security/ir.model.access.csv",
        "views/survey_user_input_views.xml",
        "views/survey_whatsapp_wizard_views.xml",
        "views/survey_whatsapp_summary_wizard_views.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}
