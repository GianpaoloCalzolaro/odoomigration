/** @odoo-module **/

/**
 * Calendar Manager - Frontend JavaScript per gestione dinamica slot orari
 * Modulo: portal_time_off
 * 
 * Funzionalità implementate:
 * - Gestione dinamica di slot (aggiungi/rimuovi) per ogni giorno attivo
 * - Dropdown timepicker step 30 minuti (formato float per backend, HH:MM per UI)
 * - Ricalcolo ore totale/anteprima live
 * - Validazione client: confronto hour_to > hour_from e sovrapposizioni, almeno un giorno attivo
 * - Messaggistica errore inline e scroll primo errore
 */

import publicWidget from "@web/legacy/js/public/public_widget";

/**
 * Constants for calendar configuration
 */
const FLOAT_PRECISION = 0.01;
const DAYS_IN_WEEK = 7;
const MAX_DAY_INDEX = DAYS_IN_WEEK - 1;

publicWidget.registry.portal_time_off_calendar_manager = publicWidget.Widget.extend({
    selector: '.calendar-manager-container, #inline_calendar_form, #calendar_create_form',
    events: {
        'click .add-slot-btn, #add_slot_btn, #add_slot_btn_mobile, #inline_add_slot_btn': '_onClickAddSlot',
        'click .remove-slot-btn': '_onClickRemoveSlot',
        'change .day-active-checkbox': '_onChangeDayActive',
        'change .slot-hour-from, .slot-day': '_onChangeSlotHour',
        'change .slot-hour-to': '_onChangeSlotHour',
        'submit': '_onSubmitCalendarForm',
    },

    /**
     * Mapping dei nomi dei giorni in italiano
     */
    DAY_NAMES: {
        0: 'Lunedì',
        1: 'Martedì',
        2: 'Mercoledì',
        3: 'Giovedì',
        4: 'Venerdì',
        5: 'Sabato',
        6: 'Domenica',
    },

    /**
     * Cache per le opzioni del timepicker
     */
    _cachedTimepickerOptions: null,

    /**
     * Inizializzazione del widget
     */
    start: function() {
        this._super.apply(this, arguments);
        this._initializeTimepickers();
        this._updateTotalHoursPreview();
    },

    // =========================================================================
    // GESTIONE TIMEPICKER
    // =========================================================================

    /**
     * Genera le opzioni del timepicker con step di 30 minuti
     * Utilizza caching per evitare rigenerazioni ripetute
     * @returns {string} HTML delle opzioni select
     */
    _generateTimepickerOptions: function(selectedValue) {
        let options = '';
        for (let hour = 0; hour <= 24; hour++) {
            for (let minute = 0; minute < 60; minute += 30) {
                // Skip 24:30 as it's not valid
                if (hour === 24 && minute > 0) continue;
                
                const floatValue = hour + (minute / 60);
                const displayValue = this._formatHourForUI(floatValue);
                const selected = (selectedValue !== undefined && Math.abs(floatValue - selectedValue) < FLOAT_PRECISION) ? ' selected' : '';
                options += `<option value="${floatValue}"${selected}>${displayValue}</option>`;
            }
        }
        return options;
    },

    /**
     * Converte un valore float in formato HH:MM per la UI
     * @param {number} floatHour - Orario in formato float (es. 9.5 = 09:30)
     * @returns {string} Orario formattato (es. "09:30")
     */
    _formatHourForUI: function(floatHour) {
        const hours = Math.floor(floatHour);
        const minutes = Math.round((floatHour - hours) * 60);
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
    },

    /**
     * Initializes existing timepickers on the page
     */
    _initializeTimepickers: function() {
        const self = this;
        this.$('.slot-hour-from, .slot-hour-to').each(function() {
            const $select = $(this);
            const currentValue = $select.data('value') || $select.val();
            if (!$select.find('option').length || $select.find('option').length < 10) {
                const options = self._generateTimepickerOptions(parseFloat(currentValue));
                $select.html(options);
            }
        });
    },

    // =========================================================================
    // DYNAMIC SLOT MANAGEMENT
    // =========================================================================

    /**
     * Adds a new slot
     * @param {Event} ev - Click event
     */
    _onClickAddSlot: function(ev) {
        ev.preventDefault();
        const $btn = $(ev.currentTarget);
        
        // Find the slots container based on context
        let $slotsContainer = this.$('#inline_slots_container');
        if (!$slotsContainer.length) {
            $slotsContainer = this.$('#slots_container');
        }
        
        if (!$slotsContainer.length) {
            console.warn('Container slot non trovato');
            return;
        }

        const slotIndex = $slotsContainer.find('.slot-row').length;
        const dayOptions = Object.entries(this.DAY_NAMES).map(([idx, name]) => 
            `<option value="${idx}">${name}</option>`
        ).join('');
        
        const slotHtml = `
            <div class="slot-row row mb-2 align-items-center" data-slot-index="${slotIndex}">
                <div class="col-sm-4 col-12 mb-1 mb-sm-0">
                    <select class="form-select form-select-sm slot-day" required>
                        ${dayOptions}
                    </select>
                </div>
                <div class="col-sm-3 col-5">
                    <select class="form-select form-select-sm slot-hour-from" required>
                        ${this._generateTimepickerOptions(9.0)}
                    </select>
                </div>
                <div class="col-sm-3 col-5">
                    <select class="form-select form-select-sm slot-hour-to" required>
                        ${this._generateTimepickerOptions(13.0)}
                    </select>
                </div>
                <div class="col-sm-2 col-2 text-end">
                    <button type="button" class="btn btn-outline-danger btn-sm remove-slot-btn" title="Rimuovi">
                        <i class="fa fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
        
        $slotsContainer.append(slotHtml);
        this._updateTotalHoursPreview();
        this._updateNoSlotsMessage();
    },

    /**
     * Removes a slot
     * @param {Event} ev - Click event
     */
    _onClickRemoveSlot: function(ev) {
        ev.preventDefault();
        const $btn = $(ev.currentTarget);
        const $slotRow = $btn.closest('.slot-row');
        
        $slotRow.remove();
        this._reindexSlots();
        this._updateTotalHoursPreview();
        this._updateNoSlotsMessage();
    },

    /**
     * Reindexes slots after removal
     */
    _reindexSlots: function() {
        let $slotsContainer = this.$('#inline_slots_container');
        if (!$slotsContainer.length) {
            $slotsContainer = this.$('#slots_container');
        }
        
        $slotsContainer.find('.slot-row').each(function(index) {
            $(this).attr('data-slot-index', index);
        });
    },

    /**
     * Updates the visibility of "no slots" message
     */
    _updateNoSlotsMessage: function() {
        const slots = this._collectAllSlots();
        
        // For inline form
        const $inlineMessage = this.$('#inline_no_slots_message');
        if ($inlineMessage.length) {
            $inlineMessage.css('display', slots.length === 0 ? 'block' : 'none');
        }
        
        // For full page form
        const $pageMessage = this.$('#no_slots_message');
        if ($pageMessage.length) {
            $pageMessage.css('display', slots.length === 0 ? 'block' : 'none');
        }
    },

    /**
     * Handles day active/inactive state change
     * @param {Event} ev - Change event
     */
    _onChangeDayActive: function(ev) {
        const $checkbox = $(ev.currentTarget);
        const dayofweek = $checkbox.data('dayofweek');
        const isActive = $checkbox.is(':checked');
        const $dayContent = this.$(`#day-${dayofweek}-content`);
        
        if (isActive) {
            $dayContent.removeClass('d-none');
        } else {
            $dayContent.addClass('d-none');
            this.$(`#day-${dayofweek}-slots`).empty();
        }
        
        this._updateTotalHoursPreview();
    },

    /**
     * Handles slot time change
     * @param {Event} ev - Change event
     */
    _onChangeSlotHour: function(ev) {
        this._updateTotalHoursPreview();
    },

    // =========================================================================
    // TOTAL HOURS CALCULATION AND PREVIEW
    // =========================================================================

    /**
     * Updates the total hours preview
     */
    _updateTotalHoursPreview: function() {
        const slots = this._collectAllSlots();
        let totalHours = 0;
        const hoursByDay = {};
        const activeDays = new Set();

        // Initialize hours for each day
        for (let i = 0; i <= MAX_DAY_INDEX; i++) {
            hoursByDay[i] = 0;
        }

        // Calculate hours for each slot
        slots.forEach(slot => {
            const slotHours = slot.hour_to - slot.hour_from;
            if (slotHours > 0) {
                totalHours += slotHours;
                hoursByDay[slot.dayofweek] += slotHours;
                activeDays.add(slot.dayofweek);
            }
        });

        // Update total hours display - inline form
        const $inlineTotalHours = this.$('#inline_total_hours');
        if ($inlineTotalHours.length) {
            $inlineTotalHours.text(totalHours.toFixed(1));
        }
        
        const $inlineDaysWorked = this.$('#inline_days_worked');
        if ($inlineDaysWorked.length) {
            $inlineDaysWorked.text(activeDays.size);
        }
        
        const $inlineAvgHours = this.$('#inline_avg_hours');
        if ($inlineAvgHours.length) {
            const avgHours = activeDays.size > 0 ? (totalHours / activeDays.size) : 0;
            $inlineAvgHours.text(avgHours.toFixed(1));
        }

        // Aggiorna display totale ore - full page form
        const $totalHours = this.$('#total_hours');
        if ($totalHours.length) {
            $totalHours.text(totalHours.toFixed(1));
        }
        
        const $daysWorked = this.$('#days_worked');
        if ($daysWorked.length) {
            $daysWorked.text(activeDays.size);
        }
        
        const $avgHours = this.$('#avg_hours');
        if ($avgHours.length) {
            const avgHours = activeDays.size > 0 ? (totalHours / activeDays.size) : 0;
            $avgHours.text(avgHours.toFixed(1));
        }

        // Aggiorna il campo hidden per il form
        const $inlineSlotConfig = this.$('#inline_slot_config_json');
        if ($inlineSlotConfig.length) {
            $inlineSlotConfig.val(JSON.stringify(slots));
        }
        
        const $slotConfig = this.$('#slot_config_json');
        if ($slotConfig.length) {
            $slotConfig.val(JSON.stringify(slots));
        }

        // Update preview
        this._updatePreview(slots);
    },

    /**
     * Updates the configuration preview
     * @param {Array} slots - Array of configured slots
     */
    _updatePreview: function(slots) {
        const $inlinePreview = this.$('#inline_preview_container');
        const $preview = this.$('#preview_container');
        const $container = $inlinePreview.length ? $inlinePreview : $preview;
        
        if (!$container.length) return;

        if (slots.length === 0) {
            $container.html('<p class="text-muted mb-0">Aggiungi slot per vedere l\'anteprima.</p>');
            return;
        }

        // Group slots by day
        const byDay = {};
        slots.forEach(s => {
            if (!byDay[s.dayofweek]) byDay[s.dayofweek] = [];
            byDay[s.dayofweek].push(s);
        });

        const dayShort = ['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom'];
        let html = '<ul class="list-unstyled mb-0">';
        for (let d = 0; d < DAYS_IN_WEEK; d++) {
            if (byDay[d]) {
                const daySlots = byDay[d].sort((a, b) => a.hour_from - b.hour_from);
                const slotsStr = daySlots.map(s => 
                    `${this._formatHourForUI(s.hour_from)}-${this._formatHourForUI(s.hour_to)}`
                ).join(', ');
                html += `<li><strong>${dayShort[d]}:</strong> ${slotsStr}</li>`;
            }
        }
        html += '</ul>';
        $container.html(html);
    },

    /**
     * Collects all configured slots
     * @returns {Array} List of slots with dayofweek, hour_from, hour_to
     */
    _collectAllSlots: function() {
        const slots = [];
        
        this.$('.slot-row').each((index, row) => {
            const $row = $(row);
            const $daySelect = $row.find('.slot-day');
            const $hourFrom = $row.find('.slot-hour-from');
            const $hourTo = $row.find('.slot-hour-to');
            
            const dayofweek = parseInt($daySelect.val(), 10);
            const hourFrom = parseFloat($hourFrom.val());
            const hourTo = parseFloat($hourTo.val());
            
            // Include only slots with valid times
            if (!isNaN(dayofweek) && !isNaN(hourFrom) && !isNaN(hourTo)) {
                slots.push({
                    dayofweek: dayofweek,
                    hour_from: hourFrom,
                    hour_to: hourTo
                });
            }
        });
        
        return slots;
    },

    // =========================================================================
    // CLIENT-SIDE VALIDATION
    // =========================================================================

    /**
     * Validates that at least one slot is configured
     * @returns {Object} Validation result {valid: boolean, message: string}
     */
    _validateAtLeastOneSlot: function() {
        const slots = this._collectAllSlots();
        
        if (slots.length === 0) {
            return {
                valid: false,
                message: 'Aggiungi almeno uno slot orario prima di salvare.'
            };
        }

        // Verify that each slot has hour_to > hour_from
        for (const slot of slots) {
            if (slot.hour_to <= slot.hour_from) {
                return {
                    valid: false,
                    message: `L'orario di fine deve essere successivo all'orario di inizio per ${this.DAY_NAMES[slot.dayofweek]}.`
                };
            }
        }

        return { valid: true, message: '' };
    },

    /**
     * Shows an error message using Bootstrap alert
     * @param {string} message - Error message to display
     */
    _showErrorMessage: function(message) {
        // Remove any existing error alert
        this.$('.pto-validation-error').remove();
        
        // Create Bootstrap alert
        const alertHtml = `
            <div class="alert alert-danger alert-dismissible fade show pto-validation-error" role="alert">
                <i class="fa fa-exclamation-triangle me-2"></i>
                ${this._escapeHtml(message)}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        // Insert at the top of the form
        this.$el.prepend(alertHtml);
        
        // Scroll to the alert
        const alertElement = this.$('.pto-validation-error')[0];
        if (alertElement) {
            alertElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    },

    /**
     * Escapes HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    _escapeHtml: function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    // =========================================================================
    // FORM SUBMISSION
    // =========================================================================

    /**
     * Handles calendar form submission
     * @param {Event} ev - Submit event
     */
    _onSubmitCalendarForm: function(ev) {
        // Update slot configuration before validation
        this._updateTotalHoursPreview();
        
        // Remove any existing error alerts
        this.$('.pto-validation-error').remove();
        
        // Run validations
        const validation = this._validateAtLeastOneSlot();
        
        if (!validation.valid) {
            ev.preventDefault();
            ev.stopPropagation();
            
            this._showErrorMessage(validation.message);
            return false;
        }
        
        // Form can proceed with submission
        return true;
    },
});

export default publicWidget.registry.portal_time_off_calendar_manager;
