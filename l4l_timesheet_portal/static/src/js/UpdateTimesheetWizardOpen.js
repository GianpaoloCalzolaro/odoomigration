/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { useService } from "@web/core/utils/hooks";

publicWidget.registry.update_hr_timesheet = publicWidget.Widget.extend({
    selector: '.timesheet_wizard',
    events: {
        'click .open_update_timesheet_wizard': '_onClickOpenTimesheetWizard',
        'click .close_timesheet_wizard': '_onClickCloseTimesheetWizard',
        'change #leap_project_id': '_onChangeProjectId',
        'click .submit_timesheet_wizard': '_onClickUpdateTimesheet',
    },

    init() {
        this._super(...arguments);
        this.orm = this.bindService("orm");
    },

    _onChangeProjectId: function(ev) {
        var ProjectId = $(ev.target).val();
        this.orm.call('account.analytic.line', 'onchange_project_id', [ProjectId]).then(function(result) {
           if (result) {
               var $select_task = $('select[name="leap_task_id"]');
               $select_task.empty().append('<option value="">-- Select Task --</option>');

               if (Array.isArray(result) && result.length > 0) {
                   result.forEach((TaskData) => {
                       var task_id = TaskData.task_id;
                       var task_name = TaskData.task_name;

                       if (task_id && task_name) {
                           var option = $('<option></option>').attr('value', task_id).text(task_name);
                           $select_task.append(option);
                       } else {
                           console.warn("Task data is missing id or name:", TaskData);
                       }
                   });
               } else {
                   $select_task.empty().append('<option value="">-- No Task --</option>');
               }
           } else {
                console.log("Please Select Valid Project...")
           }
        }).catch(function(error) {
            console.error('Error:', error);
        });
    },

    _onClickOpenTimesheetWizard: async function(ev) {
        var button = $(ev.currentTarget);
        var timesheetIdFromData = button.data('timesheet-id');
        var wizard = $('#update_timesheet_wizard_show');
        wizard.modal('show');

        var timesheet_rec_id = $('#timesheet_rec_id').val();

        this.orm.call('account.analytic.line', 'get_timesheet', [timesheetIdFromData]).then((result) => {
            var timesheet = result[0];

            $('#timesheet_rec_id').val(timesheet.id);
            $('#leap_name').val(timesheet.name);
            $('#leap_employee_id').val(timesheet.employee_id);
            $('#leap_date').val(timesheet.date);
            $('#leap_project_id').val(timesheet.project_id);

            var unitAmountInHours = timesheet.unit_amount;
            var hours = Math.floor(unitAmountInHours);
            var minutes = Math.round((unitAmountInHours - hours) * 60);
            var timeString = pad(hours) + ":" + pad(minutes);

            $('#leap_unit_amount').val(timeString);

            function pad(num) {
                return num < 10 ? '0' + num : num;
            }

            var projectId = timesheet.project_id;

            this.orm.call('account.analytic.line', 'onchange_project_id', [projectId]).then((tasks) => {
                var $select_task = $('select[name="leap_task_id"]');
                $select_task.empty().append('<option value="">-- Select Task --</option>');

                if (Array.isArray(tasks) && tasks.length > 0) {
                    tasks.forEach(function(TaskData) {
                        var task_id = TaskData.task_id;
                        var task_name = TaskData.task_name;

                        if (task_id && task_name) {
                            var option = $('<option></option>').attr('value', task_id).text(task_name);
                            $select_task.append(option);
                        } else {
                            console.warn("Task data is missing id or name:", TaskData);
                        }
                    });
                } else {
                    $select_task.empty().append('<option value="">-- No Task --</option>');
                }

                if (timesheet.task_id) {
                    $select_task.val(timesheet.task_id);
                } else {
                    console.warn('No task_id found in timesheet:', timesheet);
                }
            }).catch((error) => {
                console.error('Error fetching tasks:', error);
            });
        }).catch((error) => {
            console.error('Error fetching timesheet:', error);
        });
    },



    _onClickCloseTimesheetWizard: async function(ev){
        var wizard_close = $('#update_timesheet_wizard_show');
        wizard_close.modal('hide');
    },

    _onClickUpdateTimesheet: async function (ev) {
        var self = this;

        var timesheet_rec_id = $('#timesheet_rec_id').val();
        var timesheet_name = $('#leap_name').val();
        var employee_id = parseInt($("#leap_employee_id").val());
        var project_id = parseInt($("#leap_project_id").val());
        var task_id = parseInt($("#leap_task_id").val());
        var date = $('#leap_date').val();
        var unit_amount = $("#leap_unit_amount").val();

        var requiredFields = [
            { field: '#name', errorMessage: 'Please enter the Description.' },
            { field: '#leap_employee_id', errorMessage: 'Please select an employee.' },
            { field: '#leap_project_id', errorMessage: 'Please select the Project.' },
            { field: '#leap_task_id', errorMessage: 'Please select the Task.' },
            { field: '#leap_date', errorMessage: 'Please select the date.' },
        ];

        var valid = true;

        if (!valid) {
            return false;
        }

        var timesheet_details = {
            "id": timesheet_rec_id,
            "name": timesheet_name,
            "employee_id": employee_id,
            "project_id": project_id,
            "task_id": task_id,
            "date": date,
            "unit_amount": unit_amount,
        };
        try {
            var result = this.orm.call('account.analytic.line', 'update_emp_timesheet', [timesheet_details]);
            if (result) {
                alert("Timesheet updated successfully!");
            } else {
                alert("Oops... Timesheet not updated.");
            }
        } catch (error) {
            alert("You Cannot update This Timesheet.");
        }
        setTimeout(function () {document.location.reload(true)}, 1000);
    },
});
