# -*- coding: utf-8 -*-
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2023 Leap4Logic Solutions PVT LTD
#    Email : sales@leap4logic.com
#################################################

from odoo import models, fields, api


class ResourceCalendarAttendance(models.Model):
    """
    Estensione del modello resource.calendar.attendance per supportare
    la creazione dinamica degli slot orari dai calendari personalizzati.

    Funzionalità implementate:
    - Mapping automatico alla creazione/modifica del calendar
    - Generazione nomi slot con formato "Giorno Periodo" (es. "Lunedì Mattina")
    - Determinazione automatica day_period in base all'orario
    - Supporto week_type per calendari a settimana singola
    """

    _inherit = 'resource.calendar.attendance'

    # Mapping dei codici giorno ai nomi italiani
    DAY_NAME_MAPPING = {
        '0': 'Lunedì',
        '1': 'Martedì',
        '2': 'Mercoledì',
        '3': 'Giovedì',
        '4': 'Venerdì',
        '5': 'Sabato',
        '6': 'Domenica',
    }

    # Mapping per i periodi della giornata
    PERIOD_NAME_MAPPING = {
        'morning': 'Mattina',
        'afternoon': 'Pomeriggio',
    }

    @api.model
    def _get_day_name(self, dayofweek):
        """
        Ritorna il nome italiano del giorno della settimana.

        Args:
            dayofweek: Codice giorno (0-6, dove 0 = Lunedì)

        Returns:
            str: Nome italiano del giorno
        """
        return self.DAY_NAME_MAPPING.get(str(dayofweek), '')

    @api.model
    def _get_period_name(self, day_period):
        """
        Ritorna il nome italiano del periodo della giornata.

        Args:
            day_period: Codice periodo ('morning' o 'afternoon')

        Returns:
            str: Nome italiano del periodo
        """
        return self.PERIOD_NAME_MAPPING.get(day_period, '')

    @api.model
    def _determine_day_period(self, hour_from):
        """
        Determina il periodo della giornata in base all'orario di inizio.

        Args:
            hour_from: Orario di inizio in formato float (es. 9.0 = 09:00)

        Returns:
            str: 'morning' se hour_from < 12, altrimenti 'afternoon'
        """
        return 'morning' if hour_from < 12.0 else 'afternoon'

    @api.model
    def _generate_attendance_name(self, dayofweek, day_period):
        """
        Genera il nome completo dello slot orario.

        Args:
            dayofweek: Codice giorno (0-6)
            day_period: Periodo della giornata ('morning' o 'afternoon')

        Returns:
            str: Nome formattato "Giorno Periodo" (es. "Lunedì Mattina")
        """
        day_name = self._get_day_name(dayofweek)
        period_name = self._get_period_name(day_period)
        return f"{day_name} {period_name}".strip()

    @api.model
    def create_attendance_from_slot(self, calendar_id, dayofweek, hour_from, hour_to):
        """
        Crea un record attendance a partire da una configurazione slot.

        Args:
            calendar_id: ID del resource.calendar
            dayofweek: Codice giorno (0-6, dove 0 = Lunedì)
            hour_from: Orario inizio in formato float (es. 9.0)
            hour_to: Orario fine in formato float (es. 13.0)

        Returns:
            recordset: Record resource.calendar.attendance creato
        """
        day_period = self._determine_day_period(hour_from)
        name = self._generate_attendance_name(dayofweek, day_period)

        vals = {
            'name': name,
            'dayofweek': str(dayofweek),
            'hour_from': hour_from,
            'hour_to': hour_to,
            'day_period': day_period,
            'week_type': False,  # False for calendars without two-weeks mode
            'calendar_id': calendar_id,
        }

        return self.create(vals)

    @api.model
    def sync_attendances_from_slots(self, calendar, slot_data_list):
        """
        Sincronizza le attendance di un calendario in base alla lista di slot.
        Rimuove le attendance esistenti e ne crea di nuove.

        Args:
            calendar: Record resource.calendar
            slot_data_list: Lista di dizionari con keys:
                - dayofweek: int (0-6)
                - hour_from: float
                - hour_to: float

        Returns:
            recordset: Records resource.calendar.attendance creati
        """
        # Rimuove le attendance esistenti del calendario
        existing_attendances = self.search([('calendar_id', '=', calendar.id)])
        existing_attendances.unlink()

        # Crea le nuove attendance
        created_attendances = self.env['resource.calendar.attendance']
        for slot_data in slot_data_list:
            attendance = self.create_attendance_from_slot(
                calendar_id=calendar.id,
                dayofweek=slot_data.get('dayofweek', 0),
                hour_from=slot_data.get('hour_from', 0.0),
                hour_to=slot_data.get('hour_to', 0.0),
            )
            created_attendances |= attendance

        return created_attendances


