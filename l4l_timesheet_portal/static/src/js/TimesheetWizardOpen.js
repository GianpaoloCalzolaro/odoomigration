/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { useService } from "@web/core/utils/hooks";

publicWidget.registry.hr_timesheet = publicWidget.Widget.extend({
    selector: '.search-bar',
    events: {
        'click .open_timesheet_wizard': '_onClickOpenTimesheetWizard',
    },

    _onClickOpenTimesheetWizard: async function(ev){
        ev.preventDefault();
        var wizard = $('#timesheet_wizard_show');
        wizard.modal('show');
    },
});
