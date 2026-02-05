from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    threshold_reached_id = fields.Many2one('survey.certification.threshold', string='Threshold Reached', index=True)
    history_ids = fields.One2many('survey.user_input.history', 'user_input_id')
    current_certification_name = fields.Char(compute='_compute_current_certification_name')

    @api.depends('threshold_reached_id', 'threshold_reached_id.name')
    def _compute_current_certification_name(self):
        for rec in self:
            rec.current_certification_name = rec.threshold_reached_id.name if rec.threshold_reached_id else False

    @api.depends('survey_id.certification_mode', 'scoring_percentage', 'survey_id.scoring_success_min')
    def _compute_scoring_success(self):
        """
        Override del compute di scoring_success per gestire la modalità multiple certification.
        In modalità multiple, forza scoring_success a False per impedire la logica standard.
        In modalità single, mantiene la logica standard di Odoo.
        """
        for user_input in self:
            if user_input.survey_id.certification_mode == 'multiple':
                # In modalità multiple, forza sempre a False per impedire la certificazione standard
                user_input.scoring_success = False
                _logger.debug("Multiple certification mode: forcing scoring_success=False for user_input %s", user_input.id)
            else:
                # Modalità single: usa la logica standard di Odoo
                if (user_input.survey_id.scoring_type == 'scoring_with_answers' and 
                    user_input.survey_id.scoring_success_min and 
                    user_input.scoring_percentage is not False):
                    user_input.scoring_success = user_input.scoring_percentage >= user_input.survey_id.scoring_success_min
                else:
                    user_input.scoring_success = False

    def _mark_done(self):
        # PRIMA gestisce la logica delle soglie multiple
        for user_input in self:
            if user_input.survey_id.certification_mode == 'multiple':
                _logger.info("Processing multiple certification for user_input %s", user_input.id)
                _logger.info("Survey title: %s, certification_mode: %s", user_input.survey_id.title, user_input.survey_id.certification_mode)
                _logger.info("Scoring percentage: %s", user_input.scoring_percentage)
                
                # Calcola la soglia per la percentuale ottenuta
                threshold = user_input.survey_id._get_threshold_for_percentage(user_input.scoring_percentage)
                
                if threshold:
                    user_input.threshold_reached_id = threshold
                    _logger.info("Threshold set: %s (ID: %s)", threshold.name, threshold.id)
                    
                    # Crea la cronologia
                    self.env['survey.user_input.history'].create_from_user_input(user_input)
                    _logger.info("History created for threshold: %s", threshold.name)
                else:
                    _logger.warning("No threshold found for percentage %s%%", user_input.scoring_percentage)
        
        # POI chiama il metodo padre per la logica standard
        super_res = super()._mark_done()
        
        # INFINE forza scoring_success = False per modalità multiple DOPO super()
        for user_input in self:
            if user_input.survey_id.certification_mode == 'multiple':
                user_input.scoring_success = False
                _logger.info("Forced scoring_success=False for user_input %s", user_input.id)
        
        return super_res
