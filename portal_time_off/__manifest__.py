{
    'name': 'Employee Apply Leave (Time Off) as a Portal User',
    'version': '1.0',
    'summary': 'Manage and apply leaves via portal user',
    "description": """
       This module allows employees to apply for leave (Time Off) directly as a portal user.

       Features:
       - Portal users can submit time-off requests.
       - Admins can approve or reject requests.
       - Integrated with Odoo’s leave management system.
   """,
    'author': "Areterix Technologies",
    'price': '20.0',
    'currency': 'USD',
    'category': 'Human Resources',
    'depends': ['hr', 'portal', 'website', 'hr_holidays', 'l4l_timesheet_portal'],
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/employee_view.xml',
        'views/portal_time_off_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'portal_time_off/static/src/css/calendar_form.css',
            'portal_time_off/static/src/js/calendar_manager.js',
        ],
    },
    'live_test_url': 'https://youtu.be/vOElzQolu8o',  # Link to demo or test instance
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'images': ['static/description/banner.gif'],
}
