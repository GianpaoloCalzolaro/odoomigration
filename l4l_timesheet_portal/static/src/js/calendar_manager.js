/** @odoo-module **/

/**
 * Calendar Manager - Frontend JavaScript per gestione dinamica slot orari
 * 
 * Funzionalità implementate:
 * - Gestione dinamica di slot (aggiungi/rimuovi) per ogni giorno attivo
 * - Dropdown timepicker step 30 minuti (formato float per backend, HH:MM per UI)
 * - Ricalcolo ore totale/anteprima live
 * - Validazione client: confronto hour_to > hour_from e sovrapposizioni, almeno un giorno attivo
 * - Messaggistica errore inline e scroll primo errore
 */

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.calendar_manager = publicWidget.Widget.extend({
    selector: '.calendar-manager-container',
    events: {
        'click .add-slot-btn': '_onClickAddSlot',
        'click .remove-slot-btn': '_onClickRemoveSlot',
        'change .day-active-checkbox': '_onChangeDayActive',
        'change .slot-hour-from': '_onChangeSlotHour',
        'change .slot-hour-to': '_onChangeSlotHour',
        'submit .calendar-form': '_onSubmitCalendarForm',
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
    _generateTimepickerOptions: function() {
        // Ritorna le opzioni dalla cache se già generate
        if (this._cachedTimepickerOptions) {
            return this._cachedTimepickerOptions;
        }
        
        let options = '<option value="">-- Seleziona --</option>';
        for (let hour = 0; hour <= 24; hour++) {
            for (let minute = 0; minute < 60; minute += 30) {
                // Salta 24:30 perché non valido
                if (hour === 24 && minute > 0) continue;
                
                const floatValue = hour + (minute / 60);
                const displayValue = this._formatHourForUI(floatValue);
                options += `<option value="${floatValue}">${displayValue}</option>`;
            }
        }
        
        // Salva nella cache
        this._cachedTimepickerOptions = options;
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
     * Converte un valore HH:MM in formato float per il backend
     * @param {string} timeString - Orario in formato HH:MM
     * @returns {number} Orario in formato float
     */
    _parseHourFromUI: function(timeString) {
        if (!timeString) return null;
        const parts = timeString.split(':');
        if (parts.length !== 2) return null;
        const hours = parseInt(parts[0], 10);
        const minutes = parseInt(parts[1], 10);
        if (isNaN(hours) || isNaN(minutes)) return null;
        return hours + (minutes / 60);
    },

    /**
     * Inizializza i timepicker esistenti nella pagina
     */
    _initializeTimepickers: function() {
        const options = this._generateTimepickerOptions();
        this.$('.slot-hour-from, .slot-hour-to').each(function() {
            const $select = $(this);
            const currentValue = $select.data('value');
            $select.html(options);
            if (currentValue !== undefined && currentValue !== '') {
                $select.val(currentValue);
            }
        });
    },

    // =========================================================================
    // GESTIONE SLOT DINAMICI
    // =========================================================================

    /**
     * Aggiunge un nuovo slot a un giorno
     * @param {Event} ev - Evento click
     */
    _onClickAddSlot: function(ev) {
        ev.preventDefault();
        const $btn = $(ev.currentTarget);
        const dayofweek = $btn.data('dayofweek');
        const $dayContainer = this.$(`#day-${dayofweek}-slots`);
        
        if (!$dayContainer.length) {
            console.warn('Container slot non trovato per giorno:', dayofweek);
            return;
        }

        const slotIndex = $dayContainer.find('.slot-row').length;
        const options = this._generateTimepickerOptions();
        
        const slotHtml = `
            <div class="slot-row row mb-2" data-dayofweek="${dayofweek}" data-slot-index="${slotIndex}">
                <div class="col-5">
                    <select class="form-control slot-hour-from" 
                            name="slot_${dayofweek}_${slotIndex}_from"
                            data-dayofweek="${dayofweek}"
                            data-slot-index="${slotIndex}">
                        ${options}
                    </select>
                    <div class="invalid-feedback slot-error-from"></div>
                </div>
                <div class="col-5">
                    <select class="form-control slot-hour-to" 
                            name="slot_${dayofweek}_${slotIndex}_to"
                            data-dayofweek="${dayofweek}"
                            data-slot-index="${slotIndex}">
                        ${options}
                    </select>
                    <div class="invalid-feedback slot-error-to"></div>
                </div>
                <div class="col-2">
                    <button type="button" class="btn btn-danger remove-slot-btn" 
                            data-dayofweek="${dayofweek}"
                            data-slot-index="${slotIndex}"
                            title="Rimuovi slot">
                        <i class="fa fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
        
        $dayContainer.append(slotHtml);
        this._updateTotalHoursPreview();
        this._clearDayErrors(dayofweek);
    },

    /**
     * Rimuove uno slot
     * @param {Event} ev - Evento click
     */
    _onClickRemoveSlot: function(ev) {
        ev.preventDefault();
        const $btn = $(ev.currentTarget);
        const $slotRow = $btn.closest('.slot-row');
        const dayofweek = $btn.data('dayofweek');
        
        $slotRow.remove();
        this._reindexSlots(dayofweek);
        this._updateTotalHoursPreview();
        this._clearDayErrors(dayofweek);
    },

    /**
     * Reindicizza gli slot di un giorno dopo una rimozione
     * @param {number} dayofweek - Indice del giorno (0-6)
     */
    _reindexSlots: function(dayofweek) {
        const $dayContainer = this.$(`#day-${dayofweek}-slots`);
        $dayContainer.find('.slot-row').each(function(index) {
            const $row = $(this);
            $row.attr('data-slot-index', index);
            $row.find('.slot-hour-from')
                .attr('name', `slot_${dayofweek}_${index}_from`)
                .attr('data-slot-index', index);
            $row.find('.slot-hour-to')
                .attr('name', `slot_${dayofweek}_${index}_to`)
                .attr('data-slot-index', index);
            $row.find('.remove-slot-btn').attr('data-slot-index', index);
        });
    },

    /**
     * Gestisce il cambio di stato attivo/inattivo di un giorno
     * @param {Event} ev - Evento change
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
            // Pulisce gli slot quando il giorno viene disattivato
            this.$(`#day-${dayofweek}-slots`).empty();
        }
        
        this._updateTotalHoursPreview();
        this._clearDayErrors(dayofweek);
    },

    /**
     * Gestisce il cambio di orario in uno slot
     * @param {Event} ev - Evento change
     */
    _onChangeSlotHour: function(ev) {
        const $select = $(ev.currentTarget);
        const dayofweek = $select.data('dayofweek');
        const slotIndex = $select.data('slot-index');
        
        // Validazione immediata dello slot
        this._validateSlot(dayofweek, slotIndex);
        this._updateTotalHoursPreview();
    },

    // =========================================================================
    // CALCOLO ORE TOTALI E ANTEPRIMA
    // =========================================================================

    /**
     * Aggiorna l'anteprima delle ore totali
     */
    _updateTotalHoursPreview: function() {
        const slots = this._collectAllSlots();
        let totalHours = 0;
        const hoursByDay = {};
        const activeDays = new Set();

        // Inizializza le ore per ogni giorno
        for (let i = 0; i <= 6; i++) {
            hoursByDay[i] = 0;
        }

        // Calcola le ore per ogni slot
        slots.forEach(slot => {
            const slotHours = slot.hour_to - slot.hour_from;
            if (slotHours > 0) {
                totalHours += slotHours;
                hoursByDay[slot.dayofweek] += slotHours;
                activeDays.add(slot.dayofweek);
            }
        });

        // Aggiorna il display totale
        const $totalDisplay = this.$('.total-hours-display');
        if ($totalDisplay.length) {
            $totalDisplay.text(this._formatHoursDisplay(totalHours));
        }

        // Aggiorna il display per giorno
        for (let day = 0; day <= 6; day++) {
            const $dayHours = this.$(`#day-${day}-hours`);
            if ($dayHours.length) {
                $dayHours.text(this._formatHoursDisplay(hoursByDay[day]));
            }
        }

        // Aggiorna conteggio giorni lavorativi
        const $daysCount = this.$('.working-days-count');
        if ($daysCount.length) {
            $daysCount.text(activeDays.size);
        }

        // Aggiorna media ore giornaliera
        const $avgHours = this.$('.average-hours-display');
        if ($avgHours.length) {
            const avgHours = activeDays.size > 0 ? totalHours / activeDays.size : 0;
            $avgHours.text(this._formatHoursDisplay(avgHours));
        }

        // Aggiorna il campo hidden per il form
        const $slotConfigInput = this.$('input[name="slot_config_json"]');
        if ($slotConfigInput.length) {
            $slotConfigInput.val(JSON.stringify(slots));
        }
    },

    /**
     * Formatta le ore per la visualizzazione
     * @param {number} hours - Ore in formato float
     * @returns {string} Ore formattate (es. "8.5 ore" o "8h 30m")
     */
    _formatHoursDisplay: function(hours) {
        const wholeHours = Math.floor(hours);
        const minutes = Math.round((hours - wholeHours) * 60);
        
        if (minutes === 0) {
            return `${wholeHours}h`;
        }
        return `${wholeHours}h ${minutes}m`;
    },

    /**
     * Raccoglie tutti gli slot configurati
     * @returns {Array} Lista di slot con dayofweek, hour_from, hour_to
     */
    _collectAllSlots: function() {
        const slots = [];
        
        this.$('.slot-row').each((index, row) => {
            const $row = $(row);
            const dayofweek = parseInt($row.data('dayofweek'), 10);
            const $hourFrom = $row.find('.slot-hour-from');
            const $hourTo = $row.find('.slot-hour-to');
            
            const hourFrom = parseFloat($hourFrom.val());
            const hourTo = parseFloat($hourTo.val());
            
            // Include solo slot con orari validi
            if (!isNaN(hourFrom) && !isNaN(hourTo)) {
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
    // VALIDAZIONE CLIENT-SIDE
    // =========================================================================

    /**
     * Valida un singolo slot (hour_to > hour_from)
     * @param {number} dayofweek - Indice del giorno
     * @param {number} slotIndex - Indice dello slot
     * @returns {boolean} True se valido
     */
    _validateSlot: function(dayofweek, slotIndex) {
        const $row = this.$(`.slot-row[data-dayofweek="${dayofweek}"][data-slot-index="${slotIndex}"]`);
        if (!$row.length) return true;

        const $hourFrom = $row.find('.slot-hour-from');
        const $hourTo = $row.find('.slot-hour-to');
        const $errorFrom = $row.find('.slot-error-from');
        const $errorTo = $row.find('.slot-error-to');

        const hourFrom = parseFloat($hourFrom.val());
        const hourTo = parseFloat($hourTo.val());

        // Reset errori
        $hourFrom.removeClass('is-invalid');
        $hourTo.removeClass('is-invalid');
        $errorFrom.text('').hide();
        $errorTo.text('').hide();

        // Se uno dei due non è selezionato, non validare ancora
        if (isNaN(hourFrom) || isNaN(hourTo)) {
            return true;
        }

        // Validazione: hour_to deve essere maggiore di hour_from
        if (hourTo <= hourFrom) {
            $hourTo.addClass('is-invalid');
            $errorTo.text("L'orario di fine deve essere successivo all'orario di inizio").show();
            return false;
        }

        return true;
    },

    /**
     * Valida tutti gli slot di un giorno per sovrapposizioni
     * @param {number} dayofweek - Indice del giorno
     * @returns {Object} Risultato validazione {valid: boolean, errors: Array}
     */
    _validateDayOverlaps: function(dayofweek) {
        const slots = [];
        const $daySlots = this.$(`#day-${dayofweek}-slots .slot-row`);
        
        $daySlots.each((index, row) => {
            const $row = $(row);
            const $hourFrom = $row.find('.slot-hour-from');
            const $hourTo = $row.find('.slot-hour-to');
            
            const hourFrom = parseFloat($hourFrom.val());
            const hourTo = parseFloat($hourTo.val());
            
            if (!isNaN(hourFrom) && !isNaN(hourTo)) {
                slots.push({
                    index: index,
                    hour_from: hourFrom,
                    hour_to: hourTo,
                    $row: $row
                });
            }
        });

        // Ordina per orario di inizio
        slots.sort((a, b) => a.hour_from - b.hour_from);

        const errors = [];
        
        // Controlla sovrapposizioni
        for (let i = 0; i < slots.length - 1; i++) {
            const current = slots[i];
            const next = slots[i + 1];
            
            if (current.hour_to > next.hour_from) {
                errors.push({
                    slot1: current,
                    slot2: next,
                    message: `Sovrapposizione: ${this._formatHourForUI(current.hour_from)}-${this._formatHourForUI(current.hour_to)} si sovrappone con ${this._formatHourForUI(next.hour_from)}-${this._formatHourForUI(next.hour_to)}`
                });
                
                // Evidenzia gli slot sovrapposti
                current.$row.find('.slot-hour-to').addClass('is-invalid');
                next.$row.find('.slot-hour-from').addClass('is-invalid');
            }
        }

        return {
            valid: errors.length === 0,
            errors: errors
        };
    },

    /**
     * Valida che ci sia almeno un giorno attivo con slot
     * @returns {Object} Risultato validazione {valid: boolean, message: string}
     */
    _validateAtLeastOneActiveDay: function() {
        const slots = this._collectAllSlots();
        const activeDays = new Set();
        
        slots.forEach(slot => {
            if (slot.hour_to > slot.hour_from) {
                activeDays.add(slot.dayofweek);
            }
        });

        if (activeDays.size === 0) {
            return {
                valid: false,
                message: 'Devi configurare almeno un giorno lavorativo con uno slot orario valido.'
            };
        }

        return { valid: true, message: '' };
    },

    /**
     * Esegue tutte le validazioni del form
     * @returns {Object} Risultato validazione {valid: boolean, errors: Array}
     */
    _validateForm: function() {
        const errors = [];
        let firstErrorElement = null;

        // 1. Validazione: almeno un giorno attivo
        const activeDayValidation = this._validateAtLeastOneActiveDay();
        if (!activeDayValidation.valid) {
            errors.push({
                type: 'general',
                message: activeDayValidation.message
            });
        }

        // 2. Validazione: hour_to > hour_from per ogni slot
        this.$('.slot-row').each((index, row) => {
            const $row = $(row);
            const dayofweek = parseInt($row.data('dayofweek'), 10);
            const slotIndex = parseInt($row.data('slot-index'), 10);
            
            if (!this._validateSlot(dayofweek, slotIndex)) {
                if (!firstErrorElement) {
                    firstErrorElement = $row.find('.is-invalid').first();
                }
                errors.push({
                    type: 'slot',
                    dayofweek: dayofweek,
                    slotIndex: slotIndex,
                    message: `${this.DAY_NAMES[dayofweek]}: l'orario di fine deve essere successivo all'orario di inizio`
                });
            }
        });

        // 3. Validazione: nessuna sovrapposizione
        for (let day = 0; day <= 6; day++) {
            const overlapValidation = this._validateDayOverlaps(day);
            if (!overlapValidation.valid) {
                overlapValidation.errors.forEach(err => {
                    if (!firstErrorElement) {
                        firstErrorElement = err.slot1.$row.find('.is-invalid').first();
                    }
                    errors.push({
                        type: 'overlap',
                        dayofweek: day,
                        message: `${this.DAY_NAMES[day]}: ${err.message}`
                    });
                });
            }
        }

        // 4. Validazione nome calendario (se presente)
        const $customName = this.$('input[name="custom_name"]');
        if ($customName.length && !$customName.val().trim()) {
            $customName.addClass('is-invalid');
            if (!firstErrorElement) {
                firstErrorElement = $customName;
            }
            errors.push({
                type: 'field',
                field: 'custom_name',
                message: 'Il nome del calendario è obbligatorio.'
            });
        }

        return {
            valid: errors.length === 0,
            errors: errors,
            firstErrorElement: firstErrorElement
        };
    },

    /**
     * Mostra gli errori inline
     * @param {Array} errors - Lista errori
     */
    _showErrors: function(errors) {
        // Mostra errori generali
        const $generalErrors = this.$('.calendar-general-errors');
        if ($generalErrors.length) {
            $generalErrors.empty();
            
            const generalErrors = errors.filter(e => e.type === 'general');
            if (generalErrors.length > 0) {
                generalErrors.forEach(err => {
                    $generalErrors.append(`
                        <div class="alert alert-danger alert-dismissible fade show" role="alert">
                            <i class="fa fa-exclamation-triangle me-2"></i>
                            ${this._escapeHtml(err.message)}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Chiudi"></button>
                        </div>
                    `);
                });
                $generalErrors.show();
            }
        }

        // Mostra errori per giorno
        const overlapErrors = errors.filter(e => e.type === 'overlap');
        overlapErrors.forEach(err => {
            const $dayErrors = this.$(`#day-${err.dayofweek}-errors`);
            if ($dayErrors.length) {
                $dayErrors.append(`
                    <div class="alert alert-warning alert-sm py-1 mb-1">
                        <small><i class="fa fa-exclamation-circle me-1"></i>${this._escapeHtml(err.message)}</small>
                    </div>
                `);
                $dayErrors.show();
            }
        });
    },

    /**
     * Pulisce gli errori di un giorno specifico
     * @param {number} dayofweek - Indice del giorno
     */
    _clearDayErrors: function(dayofweek) {
        this.$(`#day-${dayofweek}-slots .slot-row`).each((index, row) => {
            const $row = $(row);
            $row.find('.slot-hour-from, .slot-hour-to').removeClass('is-invalid');
            $row.find('.slot-error-from, .slot-error-to').text('').hide();
        });
        
        const $dayErrors = this.$(`#day-${dayofweek}-errors`);
        if ($dayErrors.length) {
            $dayErrors.empty().hide();
        }
    },

    /**
     * Pulisce tutti gli errori
     */
    _clearAllErrors: function() {
        this.$('.is-invalid').removeClass('is-invalid');
        this.$('.invalid-feedback').text('').hide();
        this.$('.calendar-general-errors').empty().hide();
        this.$('[id$="-errors"]').empty().hide();
    },

    /**
     * Scrolla al primo errore
     * Utilizza scrollIntoView nativo per migliori performance
     * @param {jQuery} $element - Elemento con errore
     */
    _scrollToFirstError: function($element) {
        if ($element && $element.length) {
            const element = $element[0];
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
            // Imposta il focus dopo lo scroll
            setTimeout(() => {
                element.focus();
            }, 300);
        }
    },

    /**
     * Escape HTML per prevenire XSS
     * @param {string} text - Testo da escapare
     * @returns {string} Testo escapato
     */
    _escapeHtml: function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    // =========================================================================
    // GESTIONE SUBMIT FORM
    // =========================================================================

    /**
     * Gestisce il submit del form calendario
     * @param {Event} ev - Evento submit
     */
    _onSubmitCalendarForm: function(ev) {
        // Pulisce errori precedenti
        this._clearAllErrors();
        
        // Esegue validazioni
        const validation = this._validateForm();
        
        if (!validation.valid) {
            ev.preventDefault();
            ev.stopPropagation();
            
            // Mostra errori
            this._showErrors(validation.errors);
            
            // Scrolla al primo errore
            this._scrollToFirstError(validation.firstErrorElement);
            
            return false;
        }
        
        // Aggiorna il campo JSON prima del submit
        this._updateTotalHoursPreview();
        
        // Il form può procedere con il submit
        return true;
    },
});

export default publicWidget.registry.calendar_manager;
