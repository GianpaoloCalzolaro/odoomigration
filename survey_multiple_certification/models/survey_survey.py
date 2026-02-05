from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class Survey(models.Model):
    _inherit = 'survey.survey'

    certification_mode = fields.Selection([
        ('single', 'Single'),
        ('multiple', 'Multiple')
    ], default='single', string='Certification Mode', 
       help='Single: Use standard Odoo certification. Multiple: Use multiple certification thresholds.')
    threshold_ids = fields.One2many('survey.certification.threshold', 'survey_id', string='Certification Thresholds')
    threshold_count = fields.Integer(compute='_compute_threshold_count')

    @api.depends('threshold_ids')
    def _compute_threshold_count(self):
        for survey in self:
            survey.threshold_count = len(survey.threshold_ids)

    def _get_threshold_for_percentage(self, percentage):
        """
        Trova la soglia appropriata per una determinata percentuale.
        Versione migliorata con logging e gestione dei casi edge.
        """
        self.ensure_one()
        
        if percentage is False or percentage is None:
            _logger.warning("Survey %s: Invalid percentage value: %s", self.id, percentage)
            return False
            
        # Ordina le soglie per sequenza (da più bassa a più alta)
        thresholds = self.threshold_ids.sorted(key=lambda t: t.sequence)
        
        if not thresholds:
            _logger.warning("Survey %s: No thresholds configured for multiple certification mode", self.id)
            return False
        
        _logger.info("Survey %s: Looking for threshold for %s%% among %s thresholds", self.id, percentage, len(thresholds))
        
        # Trova la prima soglia che contiene la percentuale
        for threshold in thresholds:
            _logger.debug("Checking threshold %s: %s-%s%%", threshold.name, threshold.percentage_min, threshold.percentage_max)
            
            # Verifica se la percentuale rientra in questa soglia
            # percentage_min è escluso, percentage_max è incluso (tranne per la prima soglia)
            min_included = threshold.percentage_min if threshold.percentage_min == 0 else threshold.percentage_min
            max_included = threshold.percentage_max
            
            if min_included <= percentage <= max_included:
                _logger.info("Found matching threshold: %s for %s%%", threshold.name, percentage)
                return threshold
        
        # Se nessuna soglia contiene la percentuale, logga un warning
        _logger.warning("Survey %s: No threshold found for percentage %s%%. Available thresholds: %s", self.id, percentage, [(t.name, t.percentage_min, t.percentage_max) for t in thresholds])
        return False

    def action_open_threshold_wizard(self):
        """Apre il wizard per configurare le soglie"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Configure Certification Thresholds'),
            'res_model': 'survey.threshold.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_survey_id': self.id,
            }
        }
