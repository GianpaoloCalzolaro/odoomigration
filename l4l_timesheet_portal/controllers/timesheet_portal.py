# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2023 Leap4Logic Solutions PVT LTD
#    Email : sales@leap4logic.com
#################################################

from odoo import http, _, SUPERUSER_ID, models, fields
from dateutil.relativedelta import relativedelta
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.osv.expression import AND, FALSE_DOMAIN
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import content_disposition, Controller, request, route
from odoo.osv import expression
from operator import itemgetter
from odoo.addons.hr_timesheet.controllers.portal import TimesheetCustomerPortal


class TimesheetPortal(TimesheetCustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        employee_ids = partner.employee_ids
        if employee_ids:
            timesheet_count = 1
        else:
            timesheet_count = 0
        values['timesheet_count'] = int(timesheet_count)
        return values

    def _domain_project_id(self):
        domain = [('allow_timesheets', '=', True)]
        if not request.env.user.has_group('hr_timesheet.group_timesheet_manager'):
            return expression.AND([domain,
                ['|', ('privacy_visibility', '!=', 'followers'), ('message_partner_ids', 'in', [request.env.user.partner_id.id])]
            ])
        return domain

    def _get_searchbar_sortings(self):
        return super()._get_searchbar_sortings() | {
            'id desc': {'label': request.env._('Newest')},
            'date desc': {'label': request.env._('Date')},
        }

    @http.route(['/my/timesheets', '/my/timesheets/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_timesheets(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='none',
                             **kw):
        Timesheet = request.env['account.analytic.line']
        domain = []
        Timesheet_sudo = Timesheet.sudo()

        values = self._prepare_portal_layout_values()
        _items_per_page = 100

        searchbar_sortings = self._get_searchbar_sortings()

        searchbar_inputs = dict(sorted(self._get_searchbar_inputs().items(), key=lambda item: item[1]['sequence']))

        searchbar_groupby = dict(sorted(self._get_searchbar_groupby().items(), key=lambda item: item[1]['sequence']))

        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_quarter_date = date_utils.subtract(quarter_start, weeks=1)
        last_quarter_start, last_quarter_end = date_utils.get_quarter(last_quarter_date)
        last_week = today + relativedelta(weeks=-1)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)

        employees = request.env['hr.employee'].sudo().search([('id', 'in', request.env.user.partner_id.employee_ids.ids)])

        searchbar_filters = {
            'all': {'label': request.env._('All'), 'domain': []},
            'employee': {'label': request.env._('Employee'), 'domain': [('employee_id', '=', employees.id)]},
            'last_year': {'label': request.env._('Last Year'), 'domain': [('date', '>=', date_utils.start_of(last_year, 'year')),
                                                              ('date', '<=', date_utils.end_of(last_year, 'year'))]},
            'last_quarter': {'label': request.env._('Last Quarter'),
                             'domain': [('date', '>=', last_quarter_start), ('date', '<=', last_quarter_end)]},
            'last_month': {'label': request.env._('Last Month'),
                           'domain': [('date', '>=', date_utils.start_of(last_month, 'month')),
                                      ('date', '<=', date_utils.end_of(last_month, 'month'))]},
            'last_week': {'label': request.env._('Last Week'), 'domain': [('date', '>=', date_utils.start_of(last_week, "week")),
                                                              ('date', '<=', date_utils.end_of(last_week, 'week'))]},
            'today': {'label': request.env._('Today'), 'domain': [("date", "=", today)]},
            'week': {'label': request.env._('This Week'), 'domain': [('date', '>=', date_utils.start_of(today, "week")),
                                                         ('date', '<=', date_utils.end_of(today, 'week'))]},
            'month': {'label': request.env._('This Month'), 'domain': [('date', '>=', date_utils.start_of(today, 'month')),
                                                           ('date', '<=', date_utils.end_of(today, 'month'))]},
            'quarter': {'label': request.env._('This Quarter'),
                        'domain': [('date', '>=', quarter_start), ('date', '<=', quarter_end)]},
            'year': {'label': request.env._('This Year'), 'domain': [('date', '>=', date_utils.start_of(today, 'year')),
                                                         ('date', '<=', date_utils.end_of(today, 'year'))]},
        }
        # default sort by value
        if not sortby:
            sortby = 'id desc'
        # default filter by value
        if not filterby:
            filterby = 'employee'
        domain = AND([domain, searchbar_filters[filterby]['domain']])

        if search and search_in:
            domain = AND([domain, self._get_search_domain(search_in, search)])

        if parent_task_id := kw.get('parent_task_id'):
            domain = AND([domain, [('parent_task_id', '=', int(parent_task_id))]])

        projects = request.env['project.project'].sudo().search([])
        tasks = request.env['project.task'].sudo().search([('allow_timesheets', '=', True), ('project_id', 'in', projects.ids)])

        if employees.leap_own_portal_user:
            domain = AND([domain, [('employee_id', 'in', request.env.user.partner_id.employee_ids.ids)]])

        timesheet_count = Timesheet_sudo.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/timesheets",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'filterby': filterby,
                      'groupby': groupby},
            total=timesheet_count,
            page=page,
            step=_items_per_page
        )

        def get_timesheets():
            field = None if groupby == 'none' else groupby
            orderby = '%s, %s' % (field, sortby) if field else sortby
            timesheets = Timesheet_sudo.search(domain, order=orderby, limit=_items_per_page, offset=pager['offset'])

            if field:
                if groupby == 'date':
                    raw_timesheets_group = Timesheet_sudo._read_group(
                        domain, ['date:day'], ['unit_amount:sum', 'id:recordset'], order='date:day desc'
                    )
                    grouped_timesheets = [(records, unit_amount) for __, unit_amount, records in raw_timesheets_group]

                else:
                    time_data = Timesheet_sudo._read_group(domain, [field], ['unit_amount:sum'])
                    mapped_time = {field.id: unit_amount for field, unit_amount in time_data}
                    grouped_timesheets = [(Timesheet_sudo.concat(*g), mapped_time[k.id]) for k, g in groupbyelem(timesheets, itemgetter(field))]
                return timesheets, grouped_timesheets

            grouped_timesheets = [(
                timesheets,
                Timesheet_sudo._read_group(domain, aggregates=['unit_amount:sum'])[0][0]
            )] if timesheets else []
            return timesheets, grouped_timesheets

        timesheets, grouped_timesheets = get_timesheets()

        values.update({
            'timesheets': timesheets,
            'employees': employees,
            'projects': projects,
            'tasks': tasks,
            'grouped_timesheets': grouped_timesheets,
            'page_name': 'timesheet',
            'default_url': '/my/timesheets',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_filters': searchbar_filters,
            'filterby': filterby,
            'is_uom_day': request.env['account.analytic.line']._is_timesheet_encode_uom_day(),
        })
        return request.render("hr_timesheet.portal_my_timesheets", values)



