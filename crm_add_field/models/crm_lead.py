# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CrmLead(models.Model):
    """
    Extends the CRM Lead model to add business classification fields
    """
    _inherit = 'crm.lead'

    # Business classification fields
    company_type = fields.Selection([
        ('company', 'Società/Ente'),
        ('individual', 'Ditta Individuale'),
        ('professional_association', 'Associazione Professionale'),
        ('freelancer', 'Libero Professionista')
    ], string='Company Type', help="Type of company organization")

    company_size = fields.Selection([
        ('small', 'Piccola'),
        ('medium', 'Media'),
        ('large', 'Grande'),
        ('micro', 'Micro impresa')
    ], string='Company Size', help="Size of the company")

    region = fields.Selection([
        ('puglia', 'Puglia'),
        ('campania', 'Campania'),
        ('basilicata', 'Basilicata'),
        ('lombardia', 'Lombardia'),
        ('lazio', 'Lazio'),
        ('sicilia', 'Sicilia'),
        ('sardegna', 'Sardegna'),
        ('calabria', 'Calabria'),
        ('trentino', 'Trentino-Alto Adige'),
        ('marche', 'Marche'),
        ('piemonte', 'Piemonte'),
        ('emilia', 'Emilia-Romagna'),
        ('toscana', 'Toscana'),
        ('veneto', 'Veneto'),
        ('friuli', 'Friuli-Venezia Giulia'),
        ('abruzzo', 'Abruzzo'),
        ('liguria', 'Liguria'),
        ('umbria', 'Umbria'),
        ('molise', 'Molise'),
        ('valle', 'Valle d\'Aosta')
    ], string='Region', help="Geographical region in Italy")

    business_sector_id = fields.Many2one(
        'business.sector',
        string='Business Sector',
        help="Business sector the company operates in"
    )

    annual_volume = fields.Float(
        string='Annual Volume',
        help="Annual business volume in Euro"
    )

    employee_count = fields.Selection([
        ('1_50', '1-50'),
        ('50_100', '50-100'),
        ('100_300', '100-300'),
        ('300_500', '300-500'),
        ('500_1000', '500-1000'),
        ('1000_plus', 'oltre mille')
    ], string='Employee Count', help="Number of employees in the company")
