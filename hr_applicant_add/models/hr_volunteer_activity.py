from odoo import fields, models


class HrVolunteerActivity(models.Model):
    _name = 'hr.volunteer.activity'
    _description = 'Volunteer Activity Types'
    _order = 'sequence, name'

    name = fields.Char(string='Activity Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description', translate=True)
    color = fields.Integer(string='Color', help='Color used in kanban view')
    sequence = fields.Integer(string='Sequence', default=10, help='Used to order activities')
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Activity code must be unique!'),
    ]

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.name))
        return result