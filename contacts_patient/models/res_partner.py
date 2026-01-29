from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_patient = fields.Boolean(string="Paziente", default=False)

    # Campo gestione equipe
    date_taken_charge = fields.Date(string="Data di presa in carico")

    tutor = fields.Many2one('hr.employee', string="Tutor")
    # Nel campo interessato, impostare un dominio che filtri i record visualizzati mostrando solo i dipendenti (hr.employee) la cui posizione lavorativa (job_id.tipo_incarico) è impostata su Tutor.
    date_tutor_assignment = fields.Date(string="Data di assegnazione del tutor")
    tutor_non_attivo = fields.Boolean(string="Tutor non attivo", default=False)
    data_fine_incarico_tutor = fields.Date(string="Data fine incarico tutor")
    type_professional = fields.Many2one('hr.job', string="Tipo di professionista", domain=[('department_id', 'child_of', [5])])
    overall_completion = fields.Float(related='clinical_sheet_id.overall_completion', readonly=True)
    professional = fields.Many2one('hr.employee', string="Professionista", domain="[('job_id', 'in', [type_professional])]")
    date_professional_assignment = fields.Date(string="Data di assegnazione del professionista")
    professionista_non_attivo = fields.Boolean(string="Professionista non attivo", default=False)
    data_fine_incarico_professionista = fields.Date(string="Data fine incarico professionista")
    # campi gestione consensi
    informativa_privacy = fields.Boolean(string="Informativa Privacy", help="Il paziente ha firmato l'informativa sulla privacy")
    consenso_prestazione_mod_unico= fields.Boolean(string="Consenso Prestazione Mod. Unico", help="Il paziente ha firmato il consenso per la prestazione sanitaria")
    consenso_informato_ac_valproico = fields.Boolean(string="Consenso Informato AC Valproico", help="Il paziente ha firmato il consenso informato per l'AC Valproico")
    consenso_al_trattamento_offlabel = fields.Boolean(string="Consenso al Trattamento Off-Label", help="Il paziente ha firmato il consenso per il trattamento off-label")
    # Campo gestione cartella clinica
    clinical_sheet_id = fields.Many2one('clinical.sheet', string='Scheda Clinica', ondelete='set null')
    has_clinical_sheet = fields.Boolean(string='Ha Scheda Clinica', compute='_compute_has_clinical_sheet')

    # Informazioni anagrafiche
    birth_date = fields.Date(string='Data di Nascita')
    biological_sex = fields.Selection([
        ('m', 'M'),
        ('f', 'F'),
        ('other', 'Altro')
    ], string='Sesso Biologico')
    gender_identity = fields.Char(string='Identità di Genere')
    birthplace = fields.Char(string='Luogo di Nascita')
    nationality = fields.Char(string='Nazionalità')
    profession = fields.Char(string='Professione/Occupazione')
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('separated', 'Separated')
    ], string='Stato Civile')
    education_level = fields.Selection([
        ('elementary', 'Elementary'),
        ('middle', 'Middle'),
        ('high', 'High'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'Phd')
    ], string='Livello di Istruzione')
    age = fields.Integer(string='Età', compute='_compute_age')

    @api.depends('clinical_sheet_id')
    def _compute_has_clinical_sheet(self):
        for partner in self:
            partner.has_clinical_sheet = bool(partner.clinical_sheet_id)

    @api.depends('birth_date')
    def _compute_age(self):
        today = fields.Date.today()
        for partner in self:
            if partner.birth_date:
                delta = today - partner.birth_date
                partner.age = delta.days // 365
            else:
                partner.age = 0

    @api.model
    def create(self, vals):
        # Se il booleano viene impostato in fase di create, gestiamo la data di fine incarico
        if vals.get('tutor_non_attivo') is True:
            vals['data_fine_incarico_tutor'] = fields.Date.context_today(self)
        if vals.get('tutor_non_attivo') is False:
            vals['data_fine_incarico_tutor'] = False
        if vals.get('professionista_non_attivo') is True:
            vals['data_fine_incarico_professionista'] = fields.Date.context_today(self)
        if vals.get('professionista_non_attivo') is False:
            vals['data_fine_incarico_professionista'] = False
        return super(ResPartner, self).create(vals)

    def write(self, vals):
        # Applichiamo la logica record-per-record quando i booleani vengono aggiornati
        boolean_keys = set(vals.keys()) & {'tutor_non_attivo', 'professionista_non_attivo'}
        if not boolean_keys or len(self) == 0:
            return super(ResPartner, self).write(vals)
        res = True
        for rec in self:
            rec_vals = dict(vals)
            if 'tutor_non_attivo' in vals:
                if vals.get('tutor_non_attivo'):
                    rec_vals['data_fine_incarico_tutor'] = fields.Date.context_today(rec)
                else:
                    rec_vals['data_fine_incarico_tutor'] = False
            if 'professionista_non_attivo' in vals:
                if vals.get('professionista_non_attivo'):
                    rec_vals['data_fine_incarico_professionista'] = fields.Date.context_today(rec)
                else:
                    rec_vals['data_fine_incarico_professionista'] = False
            res = res and super(ResPartner, rec).write(rec_vals)
        return res

    @api.onchange('tutor_non_attivo')
    def _onchange_tutor_non_attivo(self):
        for rec in self:
            if rec.tutor_non_attivo:
                rec.data_fine_incarico_tutor = fields.Date.context_today(rec)
            else:
                rec.data_fine_incarico_tutor = False

    @api.onchange('professionista_non_attivo')
    def _onchange_professionista_non_attivo(self):
        for rec in self:
            if rec.professionista_non_attivo:
                rec.data_fine_incarico_professionista = fields.Date.context_today(rec)
            else:
                rec.data_fine_incarico_professionista = False

    def action_create_clinical_sheet(self):
        self.ensure_one()
        if not self.clinical_sheet_id:
            sheet = self.env['clinical.sheet'].create({'partner_id': self.id})
            self.clinical_sheet_id = sheet.id
        return self.action_open_clinical_sheet()

    def action_open_clinical_sheet(self):
        self.ensure_one()
        if not self.clinical_sheet_id:
            return self.action_create_clinical_sheet()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Cartella Clinica - {self.name}',
            'res_model': 'clinical.sheet',
            'res_id': self.clinical_sheet_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
