import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class HrJob(models.Model):
    _inherit = "hr.job"

    limite_incarichi = fields.Integer(
        string="Limite Incarichi",
        help="Numero massimo di incarichi consentiti per questo ruolo. Lasciare vuoto per nessun limite."
    )
    tipo_incarico = fields.Selection([
        ('tutor', 'Tutor'),
        ('professionista', 'Professionista')
    ], string="Tipo Incarico", help="Tipo di incarico per questo ruolo")

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # Personal Information Fields
    fiscal_code = fields.Char(string="Fiscal Code", help="Tax identification number")
    birth_date = fields.Date(string="Birth Date", help="Date of birth")
    birth_place = fields.Char(string="Birth Place", help="Place of birth")
    nationality = fields.Many2one('res.country', string="Nationality", help="Country of nationality")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string="Gender")
    id_document_type = fields.Selection([
        ('passport', 'Passport'),
        ('id_card', 'ID Card'),
        ('driver_license', 'Driver\'s License'),
        ('other', 'Other')
    ], string="ID Document Type")
    id_document_number = fields.Char(string="ID Document Number")
    id_document_expiry = fields.Date(string="ID Document Expiry Date")
    certification_number = fields.Char(string="certification number")
    # Professional Information Fields
    professional_id = fields.Char(string="Professional ID", help="Unique identifier for the professional")
    professional_order = fields.Selection([
        ('Psicologi/Psicoterapeuti', 'Psicologi/Psicoterapeuti'),
        ('Medici Psichiatri', 'Medici Psichiatri'),
        ('Associazione Counselor', 'Associazione Counselor'),
        ('coach_association', 'Associazione Coach'),
    ], string="Ordine Professionale", help="Selezione ordine professionale")
    professional_type = fields.Selection([
        ('Psicologo', 'Psicologo'),
        ('Psicoterapeuta', 'Psicoterapeuta'),
        ('counselor', 'Counselor'),
        ('coach', 'Coach'),
        ('Altro', 'Altro'),
        ('Psichiatra', 'Psichiatra'),
    ], string="Tipo Professionale", help="Tipo di professionale")
    region = fields.Selection([
    ('abruzzo', 'Abruzzo'),
    ('basilicata', 'Basilicata'),
    ('calabria', 'Calabria'),
    ('campania', 'Campania'),
    ('emiliaromagna', 'Emilia Romagna'),
    ('friuliveneziagiulia', 'Friuli Venezia Giulia'),
    ('lazio', 'Lazio'),
    ('liguria', 'Liguria'),
    ('lombardia', 'Lombardia'),
    ('marche', 'Marche'),
    ('molise', 'Molise'),
    ('piemonte', 'Piemonte'),
    ('puglia', 'Puglia'),
    ('sardegna', 'Sardegna'),
    ('sicilia', 'Sicilia'),
    ('toscana', 'Toscana'),
    ('trentinoaltoadige', 'Trentino-Alto Adige'),
    ('umbria', 'Umbria'),
    ('valledaosta', 'Valle d\'Aosta'),
    ('veneto', 'Veneto')
    ], string="Region", help="Region of practice")


    # Contract date fields
    contract_start_date = fields.Date(string="Contract Start Date", help="Date when the contract starts")
    contract_end_date = fields.Date(string="Contract End Date", help="Date when the contract ends")

    
    # Experience Fields
    years_experience = fields.Integer(string="Years of Experience", help="Total years of professional experience")
    specialization = fields.Selection([
        ('clinical', 'Clinical'),
        ('educational', 'Educational'),
        ('organizational', 'Organizational'),
        ('counseling', 'Counseling'),
        ('developmental', 'Developmental'),
        ('cognitive', 'Cognitive'),
        ('behavioral', 'Behavioral'),
        ('social', 'Social'),
        ('other', 'Other')
    ], string="Specialization", help="Area of specialization")
    theoretical_orientation = fields.Selection([
        ('psychodynamic', 'Psychodynamic'),
        ('cognitive_behavioral', 'Cognitive Behavioral'),
        ('humanistic', 'Humanistic'),
        ('systemic', 'Systemic'),
        ('integrative', 'Integrative'),
        ('constructivist', 'Constructivist'),
        ('other', 'Other')
    ], string="Theoretical Orientation", help="Therapeutic approach/orientation")
    
    # Education Fields
    education_level = fields.Selection([
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('phd', 'Ph.D.'),
        ('specialization', 'Specialization'),
        ('certification', 'Certification'),
        ('other', 'Other')
    ], string="Education Level", help="Highest level of education achieved")
    university = fields.Char(string="University", help="University or educational institution attended")
    graduation_year = fields.Integer(string="Graduation Year", help="Year of graduation")
    
    # Administrative Fields
    registration_date = fields.Date(string="Registration Date", help="Date of registration with professional body")
    professional_insurance = fields.Boolean(string="Professional Insurance", help="Has professional insurance")
    insurance_company = fields.Char(string="Insurance Company", help="Name of the insurance company")
    insurance_policy_number = fields.Char(string="Insurance Policy Number", help="Policy number of professional insurance")
    insurance_expiry_date = fields.Date(string="Insurance Expiry Date", help="Expiry date of the professional insurance policy")
    # Availability Fields
    availability_start_date = fields.Date(string="Availability Start Date", help="Date from which the professional is available")
    weekly_availability_hours = fields.Float(string="Weekly Availability Hours", help="Hours available per week")
    preferred_working_days = fields.Char(string="Preferred Working Days", help="Preferred days of the week to work")
    volunteer_activities = fields.Many2many(
        'hr.volunteer.activity',
        'employee_volunteer_activity_rel',
        'employee_id',
        'activity_id',
        string='Volunteer Activities',
        help='Types of volunteer activities preferred'
    )
    
    # Skills Fields
    languages = fields.Char(string="Languages", help="Languages spoken")
    digital_skills = fields.Selection([
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert')
    ], string="Digital Skills", help="Level of digital proficiency")
    remote_session_experience = fields.Boolean(string="Remote Session Experience", help="Has experience with remote sessions")
    
    # Document Fields
    cv = fields.Binary(string="CV", help="Upload CV file")
    
    # Specializations Field
    specializzazioni = fields.Many2many(
        'hr.specialization',
        'employee_specialization_rel',
        'employee_id',
        'specialization_id',
        string='Specializations',
        help='Professional specializations of the employee'
    )

    # setting
    link=fields.Char(string="Link", help="Link to appointment")
    service = fields.Many2one('product.template', string="Service")

    # Employee type - extending the base selection with 'professionista'
    employee_type = fields.Selection(
        selection=[
            ('employee', 'Employee'),
            ('student', 'Student'),
            ('trainee', 'Trainee'),
            ('contractor', 'Contractor'),
            ('freelance', 'Freelance'),
            ('professionista', 'Professionista'),
        ],
        string='Employee Type',
        default='employee',
    )

    limite_incarichi_raggiunto = fields.Boolean(
        string="Limite Incarichi Raggiunto",
        compute="_compute_limite_incarichi_raggiunto",
        store=True,
        help="Indica se il dipendente ha raggiunto il limite massimo di incarichi"
    )
    numero_incarichi = fields.Integer(
        string="Numero Incarichi",
        compute="_compute_limite_incarichi_raggiunto",
        store=True,
        help="Numero attuale di incarichi assegnati"
    )
    percentuale_incarichi = fields.Float(
        string="Percentuale Utilizzo Incarichi",
        compute="_compute_limite_incarichi_raggiunto",
        store=True,
        help="Percentuale di incarichi utilizzati rispetto al limite"
    )

    @api.depends('job_id.limite_incarichi')
    def _compute_limite_incarichi_raggiunto(self):
        """Compute limite incarichi fields.
        
        Note: This compute depends on external data (res.partner records) that cannot
        be expressed in @api.depends. Fields are stored for performance, but may become
        stale until the cron job recalculates them. Consider removing store=True if
        real-time accuracy is more important than performance.
        """
        partner_obj = self.env['res.partner']
        for employee in self:
            limit = employee.job_id.limite_incarichi if employee.job_id else 0
            
            tutor_count = partner_obj.search_count([('tutor', '=', employee.id), ('tutor_non_attivo', '=', False)])
            professional_count = partner_obj.search_count([('professional', '=', employee.id), ('professionista_non_attivo', '=', False)])
            total_count = tutor_count + professional_count
            
            employee.numero_incarichi = total_count
            
            if limit > 0:
                employee.limite_incarichi_raggiunto = total_count >= limit
                employee.percentuale_incarichi = (total_count / limit)
            else:
                employee.limite_incarichi_raggiunto = False
                employee.percentuale_incarichi = 0.0

    @api.model
    def _cron_recalc_limite_incarichi(self, batch_size=100):
        """Recalculate limite_incarichi for all employees in batches.
        
        Uses proper cache invalidation instead of direct compute method calls.
        """
        all_ids = self.search([]).ids
        for start in range(0, len(all_ids), batch_size):
            try:
                batch = self.browse(all_ids[start:start + batch_size])
                # Invalidate cache to force recompute
                batch.invalidate_recordset(['limite_incarichi_raggiunto', 'numero_incarichi', 'percentuale_incarichi'])
                # Trigger recompute by accessing the fields
                batch.mapped('limite_incarichi_raggiunto')
                batch.mapped('numero_incarichi')
                batch.mapped('percentuale_incarichi')
            except Exception as exc:
                _logger.exception("Errore ricalcolo limite incarichi: %s", exc)
        return True
