from odoo import api, fields, models


class HrApplicant(models.Model):
    _inherit = "hr.applicant"

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
        'applicant_volunteer_activity_rel',
        'applicant_id',
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
        'applicant_specialization_rel',
        'applicant_id',
        'specialization_id',
        string='Specializations',
        help='Professional specializations of the applicant'
    )

    def create_employee_from_applicant(self):
        result = super().create_employee_from_applicant()

        if isinstance(result, dict) and 'res_id' in result:
            employee = self.env['hr.employee'].browse(result['res_id'])
        else:
            employee = result

        # Mappatura campo origine -> campo destinazione
        fields_mapping = {
            'fiscal_code': 'fiscal_code',
            'birth_date': 'birthday',
            'birth_place': 'birth_place',
        'nationality': 'nationality',
        'gender': 'gender',
        'id_document_type': 'id_document_type',
        'id_document_number': 'id_document_number',
        'id_document_expiry': 'id_document_expiry',
        'professional_id': 'professional_id',
        'professional_order': 'professional_order',
        'professional_type': 'professional_type',
        'contract_start_date': 'contract_start_date',
        'contract_end_date': 'contract_end_date',
        'years_experience': 'years_experience',
        'specialization': 'specialization',
        'theoretical_orientation': 'theoretical_orientation',
        'education_level': 'education_level',
        'university': 'university',
        'graduation_year': 'graduation_year',
        'registration_date': 'registration_date',
        'professional_insurance': 'professional_insurance',
        'insurance_company': 'insurance_company',
        'insurance_policy_number': 'insurance_policy_number',
        'availability_start_date': 'availability_start_date',
        'weekly_availability_hours': 'weekly_availability_hours',
        'preferred_working_days': 'preferred_working_days',
        'volunteer_activities': 'volunteer_activities',
        'languages': 'languages',
        'digital_skills': 'digital_skills',
        'remote_session_experience': 'remote_session_experience',
        'cv': 'cv',
        'insurance_expiry_date': 'insurance_expiry_date',
        'category_ids': 'category_ids',
        'specializzazioni': 'specializzazioni',
        'x_avatar_image': 'image_1920',
        }

        values = {}
        
        for source_field, target_field in fields_mapping.items():
            # image_1920 non viene più gestito separatamente; lasciare il ciclo gestirlo come gli altri campi
                
            if target_field in employee._fields and hasattr(self, source_field):
                field_type = employee._fields[target_field].type
                value = self[source_field]
                
                if field_type == 'many2many':
                    # Per i campi Many2many, usa i comandi speciali
                    if value:
                        values[target_field] = [(6, 0, value.ids)]  # Replace all records
                    else:
                        values[target_field] = [(5, 0, 0)]  # Clear all records
                elif field_type in ['many2one', 'one2many']:
                    # Per altri campi relazionali
                    values[target_field] = value.id if hasattr(value, 'id') and value else False
                else:
                    # Per campi semplici
                    values[target_field] = value
 
        employee.write(values)
      
        return employee

