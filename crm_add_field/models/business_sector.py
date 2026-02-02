# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BusinessSector(models.Model):
    """
    Business sector reference model for CRM leads classification
    """
    _name = 'business.sector'
    _description = 'Business Sector'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        help="Name of the business sector"
    )
    
    description = fields.Text(
        string='Description',
        help="Optional description of the business sector"
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help="If unchecked, it will allow you to hide the business sector without removing it."
    )
    
    lead_count = fields.Integer(
        string='Lead Count',
        compute='_compute_lead_count',
        help="Number of leads/opportunities associated with this business sector"
    )
    
    @api.depends()
    def _compute_lead_count(self):
        """
        Compute the number of leads/opportunities associated with this business sector.
        Uses on-demand calculation as it queries data from the crm.lead model.
        """
        lead_data = self.env['crm.lead']._read_group(
            [('business_sector_id', 'in', self.ids)],
            ['business_sector_id'], 
            ['__count']
        )
        
        # Create a dictionary with sector_id as key and count as value
        sector_count_map = {business_sector.id: count 
                          for business_sector, count in lead_data}
        
        # Set the count for each record or 0 if not found
        for sector in self:
            sector.lead_count = sector_count_map.get(sector.id, 0)
    
    def action_view_leads(self):
        """
        Open a view showing the leads linked to the business sector
        """
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("crm.crm_lead_all_leads")
        action['domain'] = [('business_sector_id', '=', self.id)]
        action['context'] = {
            'default_business_sector_id': self.id,
            'search_default_business_sector_id': self.id
        }
        action['name'] = _("Leads for %s") % self.name
        return action