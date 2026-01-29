# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2023 Leap4Logic Solutions PVT LTD
#    Email : sales@leap4logic.com
#################################################

{
    'name': "Timesheet Portal",
    'category': 'Human Resources/Time Off',
    'version': '18.0.1.0',
    'sequence': 1,
    'summary': """Timesheet Portal, Hr Timesheet Portal, Employee Timesheet Portal, Employee Timesheet, Short By, Search By, Filter By, Search Functionality, Website, Sale Order, Order, Purchase, Invoice, Bill, Receipt, Vendor, Partner, Contact, Transfer, Inventory, Shipment, Picking Portal, Picking, Portal, Create timesheet from portal, portal create timesheet, portal user create timesheet, Delivery""",
    'description': """This module offers users a streamlined and intuitive method for managing their timesheet records. It provides a complete range of features that simplify tasks such as viewing, filtering, adding, updating, and deleting timesheet data.""",
    'author': 'Leap4Logic Solutions Private Limited',
    'website': 'https://leap4logic.com/',
    'depends': ['mail', 'website', 'hr_timesheet'],
    'data': [
        'security/ir.model.access.csv',
        'security/resource_calendar_rules.xml',
        'views/timesheet_portal_template_views.xml',
        'views/leap_hr_employee_views_extended.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            "l4l_timesheet_portal/static/src/css/calendar_form.css",
            "l4l_timesheet_portal/static/src/js/TimesheetWizardOpen.js",
            "l4l_timesheet_portal/static/src/js/UpdateTimesheetWizardOpen.js",
            "l4l_timesheet_portal/static/src/js/WizardTimesheet.js",
            "l4l_timesheet_portal/static/src/js/DeleteTimesheetWizardOpen.js",
            "l4l_timesheet_portal/static/src/js/calendar_manager.js",
        ],
    },
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'images': ['static/description/banner.gif'],
    'price': '20.99',
    'currency': 'USD',
    'live_test_url': 'https://youtu.be/8ezTgKNtLhE',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
