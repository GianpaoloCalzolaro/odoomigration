# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CalendarEventOutcome(models.Model):
    """
    Master table for defining outcome types that can be assigned to appointments
    after their completion.
    """
    _name = 'calendar.event.outcome'
    _description = 'Tipologia Esito Evento Calendario'
    _order = 'sequence, name'

    name = fields.Char(
        string='Nome Esito',
        required=True,
        translate=True,
        help='Nome descrittivo della tipologia di esito'
    )
    code = fields.Char(
        string='Codice',
        required=True,
        help='Codice identificativo univoco per la tipologia di esito'
    )
    description = fields.Text(
        string='Descrizione',
        translate=True,
        help='Descrizione dettagliata della tipologia di esito'
    )
    sequence = fields.Integer(
        string='Sequenza',
        default=10,
        help='Numero di ordinamento per la visualizzazione'
    )
    color = fields.Integer(
        string='Colore',
        help='Colore per identificare visivamente la tipologia di esito'
    )
    active = fields.Boolean(
        string='Attivo',
        default=True,
        help='Se deselezionato, la tipologia di esito non sarà disponibile per nuovi eventi'
    )
    riciesta_azione = fields.Boolean(
        string='Richiesta Azione',
        help='Indicare se per questo esito è richiesta una azione',
        store=True
    )
    display_name = fields.Char(compute='_compute_display_name', store=True)

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Il codice della tipologia di esito deve essere univoco!')
    ]

    @api.depends('code', 'name')
    def _compute_display_name(self):
        """Display name with code for better identification"""
        for record in self:
            record.display_name = f"[{record.code}] {record.name}" if record.code else record.name

    @api.constrains('code')
    def _check_code_format(self):
        """Validate code format: only lowercase letters, numbers and underscores"""
        for record in self:
            if record.code:
                if not record.code.replace('_', '').replace('-', '').isalnum():
                    raise ValidationError(self.env._(
                        "Il codice può contenere solo lettere, numeri, underscore (_) e trattini (-)."
                    ))
                if record.code != record.code.lower():
                    raise ValidationError(self.env._(
                        "Il codice deve essere in minuscolo."
                    ))
