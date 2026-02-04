{
    'name': 'Employee Apply Leave (Time Off) as a Portal User',
    'version': '19.0.1.0.0',
    'summary': 'Manage and apply leaves via portal user',
    'author': "Areterix Technologies",
    'support': 'support@areterix.com',
    'price': '20.0',
    'currency': 'USD',
    'category': 'Human Resources',
    'depends': ['hr', 'portal', 'website', 'hr_holidays', 'l4l_timesheet_portal'],
    'data': [
        'security/ir.model.access.csv',
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
    'live_test_url': 'https://youtu.be/vOElzQolu8o',
    'license': 'LGPL-3',
    'images': ['static/description/banner.gif'],
}
