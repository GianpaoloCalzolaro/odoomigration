from odoo import http
from odoo.addons.survey.controllers.main import Survey
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class SurveyMultipleCertification(Survey):
    """Controller ereditato per gestire la visualizzazione personalizzata delle soglie multiple."""
    @http.route(['/survey/submit/<string:survey_token>/<string:answer_token>'], 
            type='http', auth='public', website=True, methods=['POST'])
    def survey_submit(self, survey_token, answer_token, **kwargs):
        # Chiama prima il metodo originale
        response = super().survey_submit(survey_token, answer_token, **kwargs)
        _logger.info("SURVEY SUBMIT - CONTROLLER CHIAMATO")
        return response

    @http.route(['/survey/<string:survey_token>/<string:answer_token>', '/survey/fill/<string:survey_token>/<string:answer_token>'], 
            type='http', auth='public', website=True)
    def survey_fill(self, survey_token, answer_token, **kwargs):
        """Sovrascrivi il metodo per aggiungere i dati della soglia raggiunta al context."""
        
        # Chiama il metodo padre per ottenere la risposta standard
        response = super().survey_fill(survey_token, answer_token, **kwargs)
        
        # Se la risposta non è un rendering template, ritorna direttamente
        if not hasattr(response, 'qcontext'):
            return response
            
        # Recupera l'answer dal context (la variabile usata nel template originale)
        answer = response.qcontext.get('answer')
        if not answer:
            return response
            
        # Verifica se il sondaggio usa la modalità multiple
        survey = answer.survey_id
        _logger.info("Survey %s - certification_mode: %s, answer_state: %s", survey.id, survey.certification_mode, answer.state)
        
        # Calcola se l'utente può rifare il test (can_retake)
        # Questa logica sostituisce il campo answer.can_retake che non esiste nel modello
        can_retake = False
        if answer.state == 'done':
            # La logica di can_retake dipende dai tentativi del survey
            if hasattr(survey, 'attempts_limit') and survey.attempts_limit > 0:
                # Se c'è un limite di tentativi, controlla se ne ha ancora disponibili
                attempts_count = len(answer.history_ids) if hasattr(answer, 'history_ids') else 1
                can_retake = attempts_count < survey.attempts_limit
            else:
                # Se non c'è limite di tentativi, può sempre rifare il test
                # Ma solo se il survey consente ripetizioni (logica standard Odoo)
                can_retake = getattr(survey, 'users_can_go_back', False) or getattr(survey, 'users_login_required', False)
        
        # Aggiungi can_retake al contesto per tutti i tipi di survey
        response.qcontext['can_retake'] = can_retake
        _logger.info("Setting can_retake = %s for answer %s", can_retake, answer.id)
        
        # Calcola survey_url per sostituire answer.survey_id.website_url che non esiste
        survey_url = None
        if answer.state == 'done':
            # Costruisci l'URL per tornare al survey usando il token
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            survey_url = "%s/survey/start/%s" % (base_url, survey.access_token)
        
        # Aggiungi survey_url al contesto per tutti i tipi di survey
        response.qcontext['survey_url'] = survey_url
        _logger.info("Setting survey_url = %s for survey %s", survey_url, survey.id)
        
        if survey.certification_mode == 'multiple' and answer.state == 'done':
            # Modalità multiple: calcola sempre la soglia se non è già impostata
            threshold = answer.threshold_reached_id
            
            if not threshold and answer.scoring_percentage is not False:
                # Calcola la soglia se non è già impostata
                threshold = survey._get_threshold_for_percentage(answer.scoring_percentage)
                _logger.info("Calculated threshold for %s%%: %s", answer.scoring_percentage, threshold.name if threshold else 'None')
                
                # Salva la soglia nel database usando sudo per evitare problemi di permessi
                if threshold:
                    answer.sudo().write({'threshold_reached_id': threshold.id})
                    _logger.info("Threshold %s saved to database for answer %s", threshold.name, answer.id)
            
            # Imposta sempre is_multiple_certification = True per modalità multiple
            threshold_data = {
                'is_multiple_certification': True,
                'scoring_percentage': answer.scoring_percentage,
            }
            
            if threshold:
                threshold_data.update({
                    'threshold_reached': threshold,
                    'threshold_name': threshold.name,
                    'threshold_description': threshold.description_html or '',
                })
                _logger.info("Setting threshold data: %s", threshold.name)
            else:
                # Gestione caso edge: nessuna soglia trovata
                threshold_data.update({
                    'threshold_reached': None,
                    'threshold_name': 'Nessuna soglia configurata',
                    'threshold_description': 'Non sono state configurate soglie per questo punteggio.',
                })
                _logger.warning("No threshold found for percentage %s%%", answer.scoring_percentage)
            
            response.qcontext.update(threshold_data)
            
        else:
            # Modalità standard o answer non completato
            response.qcontext.update({
                'is_multiple_certification': False,
            })
            # can_retake è già stato impostato sopra per tutti i tipi di survey
            
        return response
