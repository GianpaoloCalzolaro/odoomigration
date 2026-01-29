# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2023 Leap4Logic Solutions PVT LTD
#    Email: sales@leap4logic.com
#################################################

import json
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.http import request


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def prepare_task_values(self, tasks):
        return {
            'task_id': tasks.ids,
            'task_name': tasks.mapped('display_name'),
        }

    def time_to_float(self, time_str):
        try:
            time_obj = datetime.strptime(time_str, '%H:%M')
            return time_obj.hour + time_obj.minute / 60.0
        except ValueError:
            return 0.0

    @api.model
    def create_timesheet(self, timesheet_details):
        if not isinstance(timesheet_details, dict):
            raise ValidationError("Invalid data format. Expected a dictionary.")

        value = {
            "name": timesheet_details.get('name'),
            "employee_id": timesheet_details.get('employee_id'),
            "project_id": timesheet_details.get('project_id'),
            "task_id": timesheet_details.get('task_id'),
            "date": timesheet_details.get('date'),
            "unit_amount": self.time_to_float(timesheet_details.get('unit_amount')),
        }
        if 'employee_ids' in value and value['employee_ids']:
            employee = self.env['hr.employee'].sudo().browse(value['employee_ids'][0][2])
            if employee:
                value['department_id'] = employee.department_id.id

        try:
            account_analytic_line = self.sudo().create(value)

            if account_analytic_line:
                return {
                    'success': True,
                    'message': "Employee's Timesheet created successfully!"
                }
        except Exception as e:
            raise ValidationError(f"Failed to create timesheet: {e}")

    @api.model
    def onchange_project_id(self, ProjectId):
        task_vals = []
        if ProjectId:
            project = request.env['project.project'].sudo().search([('id', '=', ProjectId)])
            tasks = request.env['project.task'].sudo().search([('project_id', '=?', project.id), ("is_closed", "=", False), ('display_in_project', '=', True)])
            if tasks:
                for task in tasks:
                    task_vals.append(self.prepare_task_values(task))
                return task_vals
            else:
                return []

    @api.model
    def get_timesheet(self, record):
        record_id = self.sudo().search([('id', '=', record)])
        timesheets = []
        for record in record_id:
            timesheets.append({"id": record.id,
                               "name": record.name,
                               "employee_id": record.employee_id.id,
                               "project_id": record.project_id.id,
                               "task_id": record.task_id.id,
                               "task_name": record.task_id.name,
                               "date": record.date,
                               "unit_amount": record.unit_amount,
                           })
        return timesheets

    @api.model
    def update_emp_timesheet(self, timesheet_id):
        record_id = self.sudo().search([('id', '=', timesheet_id.get('id'))])
        value = {
            "name": timesheet_id.get('name'),
            "employee_id": timesheet_id.get('employee_id'),
            "project_id": timesheet_id.get('project_id'),
            "task_id": timesheet_id.get('task_id'),
            "date": timesheet_id.get('date'),
            "unit_amount": self.time_to_float(timesheet_id.get('unit_amount')),
        }
        if 'employee_ids' in value and value['employee_ids']:
            employee = self.env['hr.employee'].sudo().browse(value['employee_ids'][0][2])
            if employee:
                value['department_id'] = employee.department_id.id

        try:
            account_analytic_line = record_id.sudo().write(value)

            if account_analytic_line:
                return {
                    'success': True,
                    'message': "Employee's Timesheet created successfully!"
                }
        except Exception as e:
            raise ValidationError(f"Failed to create timesheet: {e}")

    @api.model
    def delete_emp_timesheet(self, timesheet_id):
        record_id = self.sudo().search([('id', '=', timesheet_id)])
        return record_id.sudo().unlink()


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    leap_own_portal_user = fields.Boolean(string="Can view own timesheet in portal", help="Allow user to view their own timesheet in the portal.")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
