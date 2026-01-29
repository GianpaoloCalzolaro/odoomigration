# Copyright 2023 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Survey contacts generation",
    "summary": "Generate new contacts or applicants from surveys",
    "version": "18.0.4.0.0",
    "development_status": "Beta",
    "category": "Marketing/Survey",
    "website": "https://github.com/OCA/survey",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["pilarvargas-tecnativa"],
    "license": "AGPL-3",
    "depends": ["survey", "hr_recruitment", "website"],
    "data": [
        "views/survey_question_views.xml",
        "views/survey_survey_views.xml",
        "views/survey_layout_inherit.xml",
    ],
    "demo": [
        "demo/survey_contact_generation_demo.xml",
    ],
    "assets": {
        "web.assets_tests": [
            "/survey_contact_generation/static/tests/survey_contact_generation_tour.esm.js",
        ],
    },
}
