from odoo import models, fields, api
import pytz
from pytz import timezone

class PortalNote(models.Model):
    _name = 'portal.note'
    _description = 'Portal Diario'
    _order = 'create_date desc'

    title = fields.Char(string="Titel", required=True)
    content = fields.Html(string="Inhalt")  # Cambiato da Text a Html per permettere formattazione ricca
    user_id = fields.Many2one('res.users', string="Benutzer", default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='Partner', related='user_id.partner_id', store=True, readonly=True)
    partner_name = fields.Char(string='Partner Name', related='partner_id.name', store=True, readonly=True)
    # Aggiunto campo di selezione "Come sto" con valori richiesti
    how_i_feel = fields.Selection([
        ('sto_male', 'STO MALE'),
        ('sto_migliorando', 'STO MIGLIORANDO'),
        ('sto_meglio', 'STO MEGLIO'),
        ('sto_bene', 'MÒ STO BENE')
    ], string="Come sto", help="Indica il tuo stato d'animo attuale")
    
    @api.depends('create_date')
    def _compute_formatted_create_date(self):
        """Computed field per formattare la data di creazione in formato italiano con orario"""
        for record in self:
            if record.create_date:
                user_tz = record.env.user.tz or 'Europe/Rome'
                
                create_date_utc = record.create_date
                if create_date_utc.tzinfo is None:
                    create_date_utc = pytz.utc.localize(create_date_utc)
                
                user_timezone = timezone(user_tz)
                create_date_local = create_date_utc.astimezone(user_timezone)
                
                record.formatted_create_date = create_date_local.strftime('%d/%m/%Y %H:%M')
            else:
                record.formatted_create_date = ''
    
    # Campo computed per visualizzare la data formattata
    formatted_create_date = fields.Char(
        string="Data Creazione",
        compute='_compute_formatted_create_date',
        store=False
    )

