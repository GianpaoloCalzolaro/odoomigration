# -*- coding: utf-8 -*-
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2023 Leap4Logic Solutions PVT LTD
#    Email : sales@leap4logic.com
#################################################

import json
import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResourceCalendar(models.Model):
    """
    Estensione del modello resource.calendar per la gestione di calendari personalizzati
    creati dagli utenti portal dipendente.

    Funzionalità implementate:
    - Generazione automatica del nome: "Calendario di [Nome Dipendente] - [Nome Personalizzato]"
    - Assegnazione automatica di company_id dalla company del dipendente
    - Assegnazione automatica del timezone (tz) dal dipendente
    - Campo flexible_hours impostato sempre a False
    - Campo active impostato a True di default
    - Visibilità privata: ogni dipendente vede e gestisce solo i propri calendari
    - Creazione dinamica degli slot orari (attendance) dalla UI

    Modalità d'uso:
    - Questo modello viene utilizzato dagli utenti portal dipendente per creare
      calendari di lavoro personalizzati attraverso il portale.
    - Alla creazione, fornire solo il campo 'custom_name' (nome personalizzato);
      gli altri attributi vengono calcolati automaticamente in base al dipendente collegato.
    - L'accesso ai calendari è limitato: ogni dipendente può visualizzare e modificare
      solo i calendari da lui creati tramite il campo 'employee_creator_id'.
    - Gli slot orari vengono creati automaticamente a partire da slot_config_ids.
    """

    _inherit = 'resource.calendar'

    custom_name = fields.Char(
        string='Nome Personalizzato',
        help='Nome personalizzato del calendario. '
             'Verrà utilizzato per generare il nome completo del calendario.'
    )
    employee_creator_id = fields.Many2one(
        'hr.employee',
        string='Dipendente Creatore',
        help='Dipendente che ha creato questo calendario. '
             'Utilizzato per la visibilità privata dei calendari.'
    )
    slot_config_json = fields.Text(
        string='Configurazione Slot JSON',
        help='Configurazione degli slot orari in formato JSON. '
             'Formato: [{"dayofweek": 0, "hour_from": 9.0, "hour_to": 13.0}, ...]'
    )

    # =========================================================================
    # CAMPI CALCOLATI PER ORE SETTIMANALI E MEDIA GIORNALIERA
    # =========================================================================

    total_weekly_hours = fields.Float(
        string='Ore Settimanali Totali',
        compute='_compute_weekly_hours_stats',
        store=True,
        readonly=True,
        help='Somma delle ore di lavoro settimanali calcolate dagli slot del calendario.'
    )
    days_worked = fields.Integer(
        string='Giorni Lavorativi',
        compute='_compute_weekly_hours_stats',
        store=True,
        readonly=True,
        help='Numero di giorni lavorativi settimanali (giorni distinti con almeno uno slot).'
    )
    hours_per_day = fields.Float(
        string='Media Ore Giornaliera',
        compute='_compute_weekly_hours_stats',
        store=True,
        readonly=True,
        help='Media ore giornaliere (ore totali / giorni lavorativi).'
    )

    @api.depends('attendance_ids', 'attendance_ids.hour_from', 'attendance_ids.hour_to', 'attendance_ids.dayofweek')
    def _compute_weekly_hours_stats(self):
        """
        Calcola le statistiche settimanali del calendario:
        - total_weekly_hours: somma delle ore di tutti gli slot
        - days_worked: numero di giorni distinti con almeno uno slot
        - hours_per_day: media ore giornaliera (con gestione divisione per zero)
        """
        for calendar in self:
            total_hours = 0.0
            worked_days = set()

            for attendance in calendar.attendance_ids:
                # Calcola le ore di ogni slot
                slot_hours = attendance.hour_to - attendance.hour_from
                if slot_hours > 0:
                    total_hours += slot_hours
                # Traccia i giorni lavorativi distinti (dayofweek è già string in Odoo)
                worked_days.add(attendance.dayofweek)

            days_count = len(worked_days)

            calendar.total_weekly_hours = total_hours
            calendar.days_worked = days_count
            # Gestione divisione per zero
            calendar.hours_per_day = total_hours / days_count if days_count > 0 else 0.0

    # =========================================================================
    # VALIDAZIONE CONFIGURAZIONE CALENDARIO PERSONALIZZATO
    # =========================================================================

    def _validate_custom_name(self, custom_name, employee_creator_id):
        """
        Valida che il nome personalizzato non sia vuoto per calendari
        creati da dipendenti del portale.

        Args:
            custom_name: Nome personalizzato del calendario
            employee_creator_id: ID del dipendente creatore

        Raises:
            ValidationError: Se il nome personalizzato è vuoto
        """
        if employee_creator_id and not custom_name:
            raise ValidationError(
                self.env._("Configurazione invalida: il nome del calendario è obbligatorio. "
                "Inserisci un nome personalizzato per il tuo calendario.")
            )

    def _validate_slot_configuration(self, slot_config_json, employee_creator_id):
        """
        Valida la configurazione degli slot orari:
        - Controlla che ci sia almeno un giorno attivo con slot configurati
        - Controlla che non ci siano slot sovrapposti nello stesso giorno

        Args:
            slot_config_json: Configurazione slot in formato JSON
            employee_creator_id: ID del dipendente creatore

        Raises:
            ValidationError: Se la configurazione non è valida
        """
        # Validazione solo per calendari creati da dipendenti del portale
        if not employee_creator_id:
            return

        # Parse del JSON
        if not slot_config_json:
            raise ValidationError(
                self.env._("Configurazione invalida: nessun orario di lavoro configurato. "
                "Aggiungi almeno uno slot orario per attivare il calendario.")
            )

        try:
            slot_data_list = json.loads(slot_config_json)
        except (json.JSONDecodeError, TypeError) as e:
            raise ValidationError(
                self.env._("Configurazione invalida: formato JSON non valido. Dettaglio: %s") % e
            )

        if not isinstance(slot_data_list, list):
            raise ValidationError(
                self.env._("Configurazione invalida: la configurazione degli slot deve essere una lista.")
            )

        # Validazione: almeno uno slot configurato (0 ore/settimana)
        if len(slot_data_list) == 0:
            raise ValidationError(
                self.env._("Configurazione invalida: nessun orario di lavoro configurato (0 ore/settimana). "
                "Aggiungi almeno uno slot orario per attivare il calendario.")
            )

        # Validazione: controllo sovrapposizioni nello stesso giorno
        self._validate_no_overlapping_slots(slot_data_list)

    def _validate_no_overlapping_slots(self, slot_data_list):
        """
        Verifica che non ci siano slot sovrapposti nello stesso giorno.

        Due slot si sovrappongono se uno inizia prima che l'altro finisca.

        Args:
            slot_data_list: Lista di dizionari con la configurazione degli slot

        Raises:
            ValidationError: Se esistono slot sovrapposti
        """
        # Mapping dei nomi dei giorni in italiano
        day_names = {
            0: 'Lunedì',
            1: 'Martedì',
            2: 'Mercoledì',
            3: 'Giovedì',
            4: 'Venerdì',
            5: 'Sabato',
            6: 'Domenica',
        }

        # Raggruppa gli slot per giorno
        slots_by_day = {}
        for idx, slot in enumerate(slot_data_list):
            if not isinstance(slot, dict):
                _logger.warning(
                    "Slot %d: expected dict, got %s - skipping in overlap validation",
                    idx, type(slot).__name__
                )
                continue

            dayofweek = slot.get('dayofweek')
            hour_from = slot.get('hour_from')
            hour_to = slot.get('hour_to')

            if dayofweek is None or hour_from is None or hour_to is None:
                _logger.warning(
                    "Slot %d: missing required field(s) - skipping in overlap validation",
                    idx
                )
                continue

            try:
                day_key = int(dayofweek)
                h_from = float(hour_from)
                h_to = float(hour_to)
            except (ValueError, TypeError) as e:
                _logger.warning(
                    "Slot %d: invalid value types - %s - skipping in overlap validation",
                    idx, str(e)
                )
                continue

            if day_key not in slots_by_day:
                slots_by_day[day_key] = []

            slots_by_day[day_key].append({
                'hour_from': h_from,
                'hour_to': h_to,
            })

        # Controlla sovrapposizioni per ogni giorno
        for day, slots in slots_by_day.items():
            # Ordina gli slot per orario di inizio
            sorted_slots = sorted(slots, key=lambda x: x['hour_from'])

            for i in range(len(sorted_slots) - 1):
                current_slot = sorted_slots[i]
                next_slot = sorted_slots[i + 1]

                # Sovrapposizione: lo slot corrente finisce dopo che il prossimo inizia
                if current_slot['hour_to'] > next_slot['hour_from']:
                    day_name = day_names.get(day, f'Giorno {day}')
                    raise ValidationError(
                        self.env._("Sovrapposizione rilevata: %s ha slot che si sovrappongono. "
                        "Lo slot %s-%s si sovrappone con %s-%s. "
                        "Correggi gli orari per evitare sovrapposizioni.") % (
                            day_name,
                            self._format_hour(current_slot['hour_from']),
                            self._format_hour(current_slot['hour_to']),
                            self._format_hour(next_slot['hour_from']),
                            self._format_hour(next_slot['hour_to'])
                        )
                    )

    def _format_hour(self, hour_float):
        """
        Formatta un valore orario float in formato HH:MM.

        Args:
            hour_float: Orario in formato float (es. 9.5 = 09:30)

        Returns:
            str: Orario formattato (es. "09:30")
        """
        hours = int(hour_float)
        minutes = int((hour_float - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"

    def _run_calendar_validations(self, vals, is_create=True):
        """
        Esegue tutte le validazioni sulla configurazione del calendario.
        Chiamato sia in create che in write.

        Args:
            vals: Dizionario dei valori da validare
            is_create: True se chiamato da create, False se da write

        Raises:
            ValidationError: Se una validazione fallisce
        """
        employee_creator_id = vals.get('employee_creator_id')
        custom_name = (vals.get('custom_name') or '').strip()
        slot_config_json = vals.get('slot_config_json')

        # Condizione per validazione obbligatoria alla creazione
        requires_full_validation = is_create and employee_creator_id

        # Validazione nome personalizzato
        if 'custom_name' in vals or requires_full_validation:
            self._validate_custom_name(custom_name, employee_creator_id)

        # Validazione configurazione slot
        if 'slot_config_json' in vals or requires_full_validation:
            self._validate_slot_configuration(slot_config_json, employee_creator_id)

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override del metodo create per impostare automaticamente gli attributi
        del calendario in base al dipendente creatore e creare gli slot orari.
        """
        for vals in vals_list:
            # Esegue le validazioni server-side per calendari personalizzati
            if vals.get('employee_creator_id'):
                self._run_calendar_validations(vals, is_create=True)

            if vals.get('employee_creator_id'):
                employee = self.env['hr.employee'].browse(vals['employee_creator_id'])
                if employee.exists():
                    # Genera il nome automaticamente
                    custom_name = vals.get('custom_name', '')
                    vals['name'] = self._generate_calendar_name(employee, custom_name)

                    # Assegna company_id dalla company del dipendente
                    if employee.company_id:
                        vals['company_id'] = employee.company_id.id

                    # Assegna timezone dal dipendente
                    if employee.tz:
                        vals['tz'] = employee.tz

                    # Imposta flexible_hours sempre a False
                    vals['flexible_hours'] = False

                    # Assicura che active sia True di default
                    if 'active' not in vals:
                        vals['active'] = True

        records = super().create(vals_list)

        # Processa la configurazione slot per ogni calendario creato
        # e assegna automaticamente il calendario al dipendente creatore
        for record, vals in zip(records, vals_list):
            if vals.get('slot_config_json'):
                record._process_slot_config()

            # Assegna automaticamente il calendario al dipendente creatore
            if record.employee_creator_id:
                record.employee_creator_id.sudo().write({
                    'resource_calendar_id': record.id
                })
                _logger.info(
                    "Calendar %s: Assigned to employee %s (resource_calendar_id=%s)",
                    record.id, record.employee_creator_id.name, record.id
                )

        return records

    def write(self, vals):
        """
        Override del metodo write per aggiornare il nome del calendario
        quando viene modificato il custom_name e sincronizzare gli slot orari.
        """
        # Esegue le validazioni server-side per calendari personalizzati durante update
        for record in self:
            if record.employee_creator_id:
                # Merge dei valori esistenti con quelli nuovi per validazione completa
                merged_vals = {
                    'employee_creator_id': record.employee_creator_id.id,
                    'custom_name': vals.get('custom_name', record.custom_name),
                    'slot_config_json': vals.get('slot_config_json', record.slot_config_json),
                }
                record._run_calendar_validations(merged_vals, is_create=False)

        res = super().write(vals)

        # Se viene aggiornato custom_name, rigenera il nome completo
        if 'custom_name' in vals:
            # Batch update per evitare scritture individuali nel loop
            records_to_update = self.filtered(lambda r: r.employee_creator_id)
            for record in records_to_update:
                new_name = self._generate_calendar_name(
                    record.employee_creator_id,
                    record.custom_name or ''
                )
                # Usa SQL diretto per update batch più efficiente
                super(ResourceCalendar, record).write({'name': new_name})

        # Se viene aggiornata la configurazione slot, sincronizza le attendance
        if 'slot_config_json' in vals:
            for record in self:
                record._process_slot_config()

        return res

    def _process_slot_config(self):
        """
        Processa la configurazione slot JSON e crea/sincronizza le attendance.
        """
        self.ensure_one()
        if not self.slot_config_json:
            return

        try:
            slot_data_list = json.loads(self.slot_config_json)
        except (json.JSONDecodeError, TypeError) as e:
            _logger.warning(
                "Calendar %s: Invalid JSON in slot_config_json: %s",
                self.id, str(e)
            )
            return

        if not isinstance(slot_data_list, list):
            _logger.warning(
                "Calendar %s: slot_config_json must be a list, got %s",
                self.id, type(slot_data_list).__name__
            )
            return

        # Validate and filter slot data
        valid_slots = []
        for idx, slot_data in enumerate(slot_data_list):
            if not isinstance(slot_data, dict):
                _logger.warning(
                    "Calendar %s: Slot %d is not a dict, skipping",
                    self.id, idx
                )
                continue

            # Check required fields
            dayofweek = slot_data.get('dayofweek')
            hour_from = slot_data.get('hour_from')
            hour_to = slot_data.get('hour_to')

            if dayofweek is None or hour_from is None or hour_to is None:
                _logger.warning(
                    "Calendar %s: Slot %d missing required fields (dayofweek, hour_from, hour_to), skipping",
                    self.id, idx
                )
                continue

            # Validate dayofweek range (0-6)
            try:
                dayofweek_int = int(dayofweek)
                if not 0 <= dayofweek_int <= 6:
                    _logger.warning(
                        "Calendar %s: Slot %d has invalid dayofweek %s (must be 0-6), skipping",
                        self.id, idx, dayofweek
                    )
                    continue
            except (ValueError, TypeError):
                _logger.warning(
                    "Calendar %s: Slot %d has invalid dayofweek %s, skipping",
                    self.id, idx, dayofweek
                )
                continue

            # Validate hours are numeric
            try:
                hour_from_float = float(hour_from)
                hour_to_float = float(hour_to)
                if not (0 <= hour_from_float <= 24 and 0 <= hour_to_float <= 24):
                    _logger.warning(
                        "Calendar %s: Slot %d has invalid hours (must be 0-24), skipping",
                        self.id, idx
                    )
                    continue
            except (ValueError, TypeError):
                _logger.warning(
                    "Calendar %s: Slot %d has invalid hour values, skipping",
                    self.id, idx
                )
                continue

            valid_slots.append({
                'dayofweek': dayofweek_int,
                'hour_from': hour_from_float,
                'hour_to': hour_to_float,
            })

        if valid_slots:
            # Usa il metodo di sincronizzazione del modello attendance
            AttendanceModel = self.env['resource.calendar.attendance']
            AttendanceModel.sync_attendances_from_slots(self, valid_slots)

    @api.model
    def _generate_calendar_name(self, employee, custom_name):
        """
        Genera il nome del calendario con il formato richiesto.

        Args:
            employee: Record hr.employee del dipendente creatore
            custom_name: Nome personalizzato fornito dall'utente

        Returns:
            str: Nome formattato "Calendario di [Nome Dipendente] - [Nome Personalizzato]"
        """
        employee_name = employee.name or ''
        if custom_name:
            return f"Calendario di {employee_name} - {custom_name}"
        return f"Calendario di {employee_name}"

    def save_update_calendar(self, slot_config=None, custom_name=None):
        """
        Salva o aggiorna il calendario generando automaticamente gli attendance_ids
        dalla configurazione slot fornita dall'utente.

        Questo metodo:
        - Mappa la struttura dinamica configurata (giorni attivi/slot) in record
          resource.calendar.attendance
        - Associa ogni attendance al calendario con dayofweek/hour_from/hour_to coerenti
        - Determina day_period automaticamente (morning se hour_from < 12, altrimenti afternoon)
        - Elimina le vecchie attendance prima di creare le nuove in caso di update

        Args:
            slot_config: Lista di dizionari con la configurazione degli slot orari.
                         Ogni dizionario deve contenere:
                         - dayofweek: int (0-6, dove 0 = Lunedì)
                         - hour_from: float (orario inizio, es. 9.0 per le 09:00)
                         - hour_to: float (orario fine, es. 13.0 per le 13:00)
                         Esempio: [{"dayofweek": 0, "hour_from": 9.0, "hour_to": 13.0}]
            custom_name: str, opzionale. Nuovo nome personalizzato per il calendario.

        Returns:
            recordset: Records resource.calendar.attendance creati

        Raises:
            ValueError: Se slot_config non è una lista o contiene slot non validi
        """
        self.ensure_one()

        # Aggiorna il nome personalizzato se fornito
        if custom_name is not None:
            self.write({'custom_name': custom_name})

        # Se non viene fornita una configurazione slot, ritorna vuoto
        if slot_config is None:
            return self.env['resource.calendar.attendance']

        # Valida che slot_config sia una lista
        if not isinstance(slot_config, list):
            raise ValueError(
                "slot_config deve essere una lista di dizionari con "
                "keys 'dayofweek', 'hour_from', 'hour_to'"
            )

        # Valida gli slot
        validated_slots = self._validate_slot_config(slot_config)

        # Usa il metodo esistente che elimina le vecchie attendance e crea le nuove
        AttendanceModel = self.env['resource.calendar.attendance']
        created_attendances = AttendanceModel.sync_attendances_from_slots(self, validated_slots)

        _logger.info(
            "Calendar %s: Created %d attendance records",
            self.id, len(created_attendances)
        )

        return created_attendances

    def _validate_slot_config(self, slot_config):
        """
        Valida la configurazione degli slot e ritorna solo gli slot validi.

        Args:
            slot_config: Lista di dizionari con la configurazione degli slot

        Returns:
            list: Lista di dizionari con gli slot validati

        Raises:
            ValueError: Se uno slot non è un dizionario o manca di campi obbligatori
        """
        validated_slots = []

        for idx, slot in enumerate(slot_config):
            if not isinstance(slot, dict):
                raise ValueError(
                    f"Slot {idx}: deve essere un dizionario, ricevuto {type(slot).__name__}"
                )

            # Verifica campi obbligatori
            dayofweek = slot.get('dayofweek')
            hour_from = slot.get('hour_from')
            hour_to = slot.get('hour_to')

            if dayofweek is None:
                raise ValueError(f"Slot {idx}: campo 'dayofweek' obbligatorio mancante")
            if hour_from is None:
                raise ValueError(f"Slot {idx}: campo 'hour_from' obbligatorio mancante")
            if hour_to is None:
                raise ValueError(f"Slot {idx}: campo 'hour_to' obbligatorio mancante")

            # Valida e converte dayofweek
            dayofweek_int = self._validate_dayofweek(idx, dayofweek)

            # Valida e converte hour_from e hour_to
            hour_from_float = self._validate_hour(idx, hour_from, 'hour_from')
            hour_to_float = self._validate_hour(idx, hour_to, 'hour_to')

            # Verifica che hour_from < hour_to
            if hour_from_float >= hour_to_float:
                raise ValueError(
                    f"Slot {idx}: hour_from ({hour_from}) deve essere minore di "
                    f"hour_to ({hour_to})"
                )

            validated_slots.append({
                'dayofweek': dayofweek_int,
                'hour_from': hour_from_float,
                'hour_to': hour_to_float,
            })

        return validated_slots

    def _validate_dayofweek(self, slot_idx, dayofweek):
        """
        Valida e converte il valore dayofweek.

        Args:
            slot_idx: Indice dello slot per messaggi di errore
            dayofweek: Valore da validare

        Returns:
            int: Valore dayofweek validato (0-6)

        Raises:
            ValueError: Se il valore non è valido
        """
        try:
            dayofweek_int = int(dayofweek)
        except (ValueError, TypeError):
            raise ValueError(
                f"Slot {slot_idx}: dayofweek deve essere un intero, ricevuto {dayofweek}"
            )

        if not 0 <= dayofweek_int <= 6:
            raise ValueError(
                f"Slot {slot_idx}: dayofweek deve essere tra 0 e 6, ricevuto {dayofweek}"
            )

        return dayofweek_int

    def _validate_hour(self, slot_idx, hour_value, field_name):
        """
        Valida e converte un valore di orario.

        Args:
            slot_idx: Indice dello slot per messaggi di errore
            hour_value: Valore da validare
            field_name: Nome del campo ('hour_from' o 'hour_to')

        Returns:
            float: Valore orario validato (0-24)

        Raises:
            ValueError: Se il valore non è valido
        """
        try:
            hour_float = float(hour_value)
        except (ValueError, TypeError):
            raise ValueError(
                f"Slot {slot_idx}: {field_name} deve essere un numero, ricevuto {hour_value}"
            )

        if not 0 <= hour_float <= 24:
            raise ValueError(
                f"Slot {slot_idx}: {field_name} deve essere tra 0 e 24, ricevuto {hour_value}"
            )

        return hour_float


