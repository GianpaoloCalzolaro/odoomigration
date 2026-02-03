{
    'name': 'HR Applicant Extension',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Recruitment',
    'summary': 'Adds personal and professional fields to HR applicants',
    'description': """
        This module extends the HR Applicant functionality by adding detailed 
        personal and professional fields for better candidate profiling and assessment.
        
        Features:
        - Personal and biographical information
        - Identification document details
        - Additional professional information fields
        - Professional experience tracking
        - Education and qualification details
        - Other relevant professional data
    """,
    'author': 'Gian Paolo Calzolaro',
    'website': 'https://www.infologis.biz',
    'license': 'LGPL-3',
    'depends': ['hr', 'hr_recruitment', 'product'],
    "data": [
        "security/ir.model.access.csv",
        "data/hr_specialization_data.xml",
        "data/hr_volunteer_activity_data.xml",
        "views/hr_add_employee_views.xml",
        "views/hr_applicant_views.xml",
        "views/hr_employee_settings_fields.xml",
        "views/hr_employee_views.xml",
        "views/hr_job_views.xml",
        "views/hr_specialization_views.xml",
        "data/ir_cron.xml"
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
