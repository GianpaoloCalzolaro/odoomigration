import random
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrSpecialization(models.Model):
    _name = 'hr.specialization'
    _description = 'Professional Specialization'
    _order = 'name'

    name = fields.Char(
        string='Specialization Name',
        required=True,
        help='Name of the professional specialization'
    )
    
    color = fields.Integer(
        string='Color Index',
        default=lambda self: random.randint(1, 11),
        help='Color index for display purposes'
    )
    
    description = fields.Text(
        string='Description',
        help='Detailed description of the specialization'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Whether this specialization is active'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        help='Company this specialization belongs to'
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Specialization name already exists!')
    ]

    def name_get(self):
        """Return name with description for better readability"""
        result = []
        for record in self:
            name = record.name
            if record.description:
                name = f"{name} - {record.description[:50]}{'...' if len(record.description) > 50 else ''}"
            result.append((record.id, name))
        return result
