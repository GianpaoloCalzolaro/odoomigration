/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { useService } from "@web/core/utils/hooks";

publicWidget.registry.delete_timesheet = publicWidget.Widget.extend({
    selector: '.timesheet_delete_wizard',
    events: {
        'click .delete_timesheet': '_onClickDelete',
    },

    init() {
        this.orm = this.bindService("orm");
    },

    _onClickDelete: async function (ev) {
        var button = $(ev.currentTarget);
        var timesheetIdFromData = button.data('timesheet-id');
        try {
            var result = this.orm.call('account.analytic.line', 'delete_emp_timesheet', [timesheetIdFromData]);
            if (result) {
                alert("Timesheet deleted successfully!");
            } else {
                alert("Oops... Timesheet not deleted.");
            }
        } catch (error) {
            alert("You Cannot deleted This Timesheet.");
        }
        setTimeout(function () {document.location.reload(true)}, 1000);
    },
});
