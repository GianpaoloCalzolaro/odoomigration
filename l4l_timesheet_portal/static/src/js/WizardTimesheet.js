/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { useService } from "@web/core/utils/hooks";

publicWidget.registry.wizard_timesheet = publicWidget.Widget.extend({
    selector: '.timesheet-container',
    events: {
        'click .close_timesheet_wizard': '_onClickCloseTimesheetWizard',
        'change #project_id': '_onChangeProjectId',
        'click .submit_timesheet_wizard': '_onClickTimesheetSubmit',
    },

    init() {
        this.orm = this.bindService("orm");
    },

    start: function() {
        this._super.apply(this, arguments);
        var ProjectId = $('select[name="project_id"]').val();
        this.orm.call('account.analytic.line', 'onchange_project_id', [ProjectId]).then(function(result) {
           if (result) {
               var $select = $('select[name="task_id"]');
               $select.empty().append('<option value="">-- Select Task --</option>');

               if (Array.isArray(result) && result.length > 0) {
                   result.forEach((TaskData) => {
                       var task_id = TaskData.task_id;
                       var task_name = TaskData.task_name;

                       if (task_id && task_name) {
                           var option = $('<option></option>').attr('value', task_id).text(task_name);
                           $select.append(option);
                       } else {
                           console.warn("Task data is missing id or name:", TaskData);
                       }
                   });
               } else {
                   $select.empty().append('<option value="">-- No Task --</option>');
               }
           } else {
                console.log("Please Select Valid Project...")
           }
        }).catch(function(error) {
            console.error('Error:', error);
        });
    },

    _onChangeProjectId: function(ev) {
        var ProjectId = $(ev.target).val();
        this.orm.call('account.analytic.line', 'onchange_project_id', [ProjectId]).then(function(result) {
           if (result) {
               var $select = $('select[name="task_id"]');
               $select.empty().append('<option value="">-- Select Task --</option>');
               if (Array.isArray(result) && result.length > 0) {
                   result.forEach((TaskData) => {
                       var task_id = TaskData.task_id;
                       var task_name = TaskData.task_name;

                       if (task_id && task_name) {
                           var option = $('<option></option>').attr('value', task_id).text(task_name);
                           $select.append(option);
                       } else {
                           console.warn("Task data is missing id or name:", TaskData);
                       }
                   });
               } else {
                   $select.empty().append('<option value="">-- No Task --</option>');
               }
           } else {
                console.log("Please Select Valid Project...")
           }
        }).catch(function(error) {
            console.error('Error:', error);
        });
    },

    _onClickCloseTimesheetWizard: async function(ev){
        var wizard_close = $('#timesheet_wizard_show');
        wizard_close.modal('hide');
    },

    _onClickTimesheetSubmit: async function(ev) {
        var self = this;

        var name = $('#name').val();
        var employee_id = parseInt($("#employee_id").val());
        var project_id = parseInt($("#project_id").val());
        var task_id = parseInt($("#task_id").val());
        var date = $('#date').val();
        var unit_amount = $("#l4l_unit_amount").val();

        var requiredFields = [
            { field: '#name', errorMessage: 'Please enter the Description.' },
            { field: '#employee_id', errorMessage: 'Please select an employee.' },
            { field: '#project_id', errorMessage: 'Please select the Project.' },
            { field: '#task_id', errorMessage: 'Please select the Task.' },
            { field: '#date', errorMessage: 'Please select the date.' },
        ];

        var valid = true;

        if (!valid) {
            return false;
        }

        var timesheet_details = {
            "name": name,
            "employee_id": employee_id,
            "project_id": project_id,
            "task_id": task_id,
            "date": date,
            "unit_amount": unit_amount,
        };

        var result = this.orm.call('account.analytic.line', 'create_timesheet', [timesheet_details]);

        setTimeout(function () {document.location.reload(true)}, 1000);
    },
});
