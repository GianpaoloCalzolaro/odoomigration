# -*- coding: utf-8 -*-

# Part of Contacts Patient Module. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict
import werkzeug
import base64
from datetime import datetime
import logging
from odoo import http, _
from odoo.http import request
from odoo import models, registry, SUPERUSER_ID
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

from odoo.osv.expression import OR

_logger = logging.getLogger(__name__)

class CustomerPortal(CustomerPortal):
    _items_per_page = 10

    def _employee_has_access_to_contact(self, employee, contact):
        """
        Helper function to check if an employee has access to a contact 
        as tutor or professional
        """
        if not employee or not contact:
            return False
        return (contact.tutor.id == employee.id or 
                contact.professional.id == employee.id)

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()  # Usa sintassi moderna
        current_user = request.env.user
        
        # Usa search invece di sudo quando possibile
        employee = request.env['hr.employee'].search([
            ('user_id', '=', current_user.id)
        ], limit=1)
        
        assigned_contacts_count = 0
        if employee:
            # Mantieni sudo solo se necessario per i permessi
            assigned_contacts_count = request.env['res.partner'].sudo().search_count([
                ('is_patient', '=', True),
                '|',
                ('tutor', '=', employee.id),
                ('professional', '=', employee.id)
            ])
        
        partner = current_user.partner_id
        equipe_count = 1 if partner.is_patient else 0
        
        values.update({
            'assigned_contacts_count': assigned_contacts_count,
            'equipe_count': equipe_count,
        })
        return values

    def _contact_get_page_view_values(self, contact, access_token, **kwargs):
        values = {
            'page_name': 'assigned_contact_detail',
            'contact': contact,
        }

        return self._get_page_view_values(contact, access_token, values, 'my_assigned_contacts', False, **kwargs)

    @http.route(['/my/assigned_contacts', '/my/assigned_contacts/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_assigned_contacts(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='name', **kw):
        current_user = request.env.user
        values = self._prepare_portal_layout_values()
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', current_user.id) ], limit=1)
        
        if not employee:
            return request.redirect('/my')
        
        contact_obj = http.request.env['res.partner']
        domain = [
            ('is_patient', '=', True),
            '|',
            ('tutor', '=', employee.id),
            ('professional', '=', employee.id)
        ]

        assigned_contacts_count = contact_obj.sudo().search_count(domain)
        
        # pager
        pager = portal_pager(
            url="/my/assigned_contacts",
            total=assigned_contacts_count,
            page=page,
            step=self._items_per_page
        )
        
        searchbar_sortings = {
            'name': {'label': _('Name Ascending'), 'order': 'name'},
            'name desc': {'label': _('Name Descending'), 'order': 'name desc'},
            'date_taken_charge': {'label': _('Date Taken Charge Ascending'), 'order': 'date_taken_charge'},
            'date_taken_charge desc': {'label': _('Date Taken Charge Descending'), 'order': 'date_taken_charge desc'},
        }
        
        searchbar_inputs = {
            'name': {'input': 'name', 'label': _('Search in Name')},
        }
        
        # default sort by value
        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            domain += search_domain

        # content according to pager and archive selected
        contacts = contact_obj.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'contacts': contacts,
            'page_name': 'assigned_contacts_list',
            'pager': pager,
            'default_url': '/my/assigned_contacts',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
        })
        return request.render("contacts_patient.portal_my_contacts", values)

    @http.route(['/my/assigned_contacts/<int:contact_id>'], type='http', auth="user", website=True)
    def portal_contact_detail(self, contact_id, access_token=None, **kw):
        employee = request.env.user.employee_id
        
        if not employee:
            return request.redirect('/my')
            
        try:
            contact_sudo = request.env['res.partner'].sudo().browse(contact_id)
            if not contact_sudo.exists() or not contact_sudo.is_patient or not self._employee_has_access_to_contact(employee, contact_sudo):
                raise AccessError(_("You don't have access to this contact."))
        except (AccessError, MissingError):
            return request.redirect('/my/assigned_contacts')

        surveys = request.env['survey.user_input'].sudo().search([
            ('partner_id', '=', contact_sudo.id),
            ('state', '=', 'done')
        ])

        values = self._contact_get_page_view_values(contact_sudo, access_token, **kw)
        values['surveys'] = surveys
        return request.render("contacts_patient.contact_detail_view", values)

    @http.route(['/my/assigned_contacts/<int:contact_id>/survey/<int:survey_input_id>/responses'], type='http', auth="user", website=True)
    def portal_survey_responses(self, contact_id, survey_input_id, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return request.redirect('/my')

        contact = request.env['res.partner'].sudo().browse(contact_id)
        if not contact.exists() or not contact.is_patient or not self._employee_has_access_to_contact(employee, contact):
            return request.redirect('/my/assigned_contacts')

        survey_input = request.env['survey.user_input'].sudo().browse(survey_input_id)
        if not survey_input.exists() or survey_input.partner_id != contact:
            return request.redirect(f'/my/assigned_contacts/{contact_id}')

        lines = request.env['survey.user_input.line'].sudo().search([
            ('user_input_id', '=', survey_input.id)
        ])

        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'survey_responses',
            'contact': contact,
            'survey': survey_input,
            'lines': lines,
        })
        return request.render('contacts_patient.survey_responses_portal', values)

    @http.route(['/my/assigned_contacts/<int:contact_id>/edit'], type='http', auth="user", website=True, methods=['GET'])
    def portal_contact_edit_form(self, contact_id, **kw):
        """Render the contact edit form"""
        employee = request.env.user.employee_id
        
        if not employee:
            return request.redirect('/my')
            
        try:
            contact = request.env['res.partner'].sudo().browse(contact_id)
            if not contact.exists() or not contact.is_patient or not self._employee_has_access_to_contact(employee, contact):
                raise AccessError(_("You don't have access to this contact."))
        except (AccessError, MissingError):
            return request.redirect('/my/assigned_contacts')
        
        # Ottieni professionisti disponibili per l'utente corrente
        available_professionals = request.env['hr.employee'].sudo().search([
            ('job_id.department_id', 'child_of', [5])  # Filtro per dipartimento
        ])
        
        # Ottieni i job types disponibili
        available_job_types = request.env['hr.job'].sudo().search([
            ('department_id', 'child_of', [5])
        ])
        
        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'edit_contact',
            'contact': contact,
            'available_professionals': available_professionals,
            'available_job_types': available_job_types,
        })
        
        return request.render("contacts_patient.contact_edit_form", values)
    
    @http.route(['/my/assigned_contacts/<int:contact_id>/edit'], type='http', auth="user", methods=['POST'], website=True)
    def portal_contact_edit_submit(self, contact_id, **kw):
        """Process the contact edit form submission"""
        employee = request.env.user.employee_id
        
        if not employee:
            return request.redirect('/my')
            
        try:
            contact = request.env['res.partner'].sudo().browse(contact_id)
            if not contact.exists() or not contact.is_patient or not self._employee_has_access_to_contact(employee, contact):
                raise AccessError(_("You don't have access to this contact."))
        except (AccessError, MissingError):
            return request.redirect('/my/assigned_contacts')
        
        vals = {}
        cs_vals = {}
        errors = []

        # Date fields
        if kw.get('date_tutor_assignment'):
            try:
                vals['date_tutor_assignment'] = datetime.strptime(kw.get('date_tutor_assignment'), '%Y-%m-%d').date()
            except (ValueError, TypeError):
                errors.append(_('Invalid tutor assignment date'))
        if kw.get('date_professional_assignment'):
            try:
                vals['date_professional_assignment'] = datetime.strptime(kw.get('date_professional_assignment'), '%Y-%m-%d').date()
            except (ValueError, TypeError):
                errors.append(_('Invalid professional assignment date'))
        if kw.get('date_taken_charge'):
            try:
                vals['date_taken_charge'] = datetime.strptime(kw.get('date_taken_charge'), '%Y-%m-%d').date()
            except (ValueError, TypeError):
                errors.append(_('Invalid taken charge date'))
        if kw.get('data_fine_incarico_tutor'):
            try:
                vals['data_fine_incarico_tutor'] = datetime.strptime(kw.get('data_fine_incarico_tutor'), '%Y-%m-%d').date()
            except (ValueError, TypeError):
                errors.append(_('Invalid tutor end date'))
        if kw.get('data_fine_incarico_professionista'):
            try:
                vals['data_fine_incarico_professionista'] = datetime.strptime(kw.get('data_fine_incarico_professionista'), '%Y-%m-%d').date()
            except (ValueError, TypeError):
                errors.append(_('Invalid professional end date'))

        if kw.get('birth_date'):
            try:
                vals['birth_date'] = datetime.strptime(kw.get('birth_date'), '%Y-%m-%d').date()
            except (ValueError, TypeError):
                errors.append(_('Invalid birth date'))

        allowed_fields = [
            'biological_sex', 'gender_identity', 'birthplace', 'nationality',
            'profession', 'marital_status', 'education_level'
        ]
        for field in allowed_fields:
            if field in kw:
                vals[field] = kw.get(field) or False

        # Campi équipe
        if kw.get('type_professional'):
            try:
                vals['type_professional'] = int(kw.get('type_professional'))
            except ValueError:
                errors.append(_('Invalid professional type'))

        if kw.get('professional'):
            try:
                vals['professional'] = int(kw.get('professional'))
            except ValueError:
                errors.append(_('Invalid professional'))
        if kw.get('tutor'):
            try:
                vals['tutor'] = int(kw.get('tutor'))
            except ValueError:
                errors.append(_('Invalid tutor'))

        # Team booleans (checkboxes)
        vals['tutor_non_attivo'] = 'tutor_non_attivo' in kw
        vals['professionista_non_attivo'] = 'professionista_non_attivo' in kw

        # Consents
        vals['informativa_privacy'] = 'informativa_privacy' in kw
        vals['consenso_prestazione_mod_unico'] = 'consenso_prestazione_mod_unico' in kw
        vals['consenso_informato_ac_valproico'] = 'consenso_informato_ac_valproico' in kw
        vals['consenso_al_trattamento_offlabel'] = 'consenso_al_trattamento_offlabel' in kw

        # Clinical Info fields (stored on clinical sheet)
        cs_text_fields = [
            'reason_for_consultation', 'problem_description', 'symptoms_duration',
            'previous_psychotherapies', 'current_issues', 'family_context',
            'social_context', 'work_context', 'diagnostic_criteria',
            'differential_diagnosis', 'comorbidity', 'treatment_plan',
            'primary_diagnosis', 'secondary_diagnosis', 'diagnosis_code'
        ]
        for field in cs_text_fields:
            if field in kw:
                cs_vals[field] = kw.get(field) or False

        if kw.get('symptoms_onset'):
            try:
                cs_vals['symptoms_onset'] = datetime.strptime(kw.get('symptoms_onset'), '%Y-%m-%d').date()
            except (ValueError, TypeError):
                errors.append(_('Invalid symptoms onset date'))

        if kw.get('risk_assessment'):
            if kw.get('risk_assessment') in ['low', 'medium', 'high']:
                cs_vals['risk_assessment'] = kw.get('risk_assessment')
            else:
                errors.append(_('Invalid risk assessment'))

        # Validation errors
        if errors:
            values = self._prepare_portal_layout_values()
            available_professionals = request.env['hr.employee'].sudo().search([
                ('job_id.department_id', 'child_of', [5])
            ])
            available_job_types = request.env['hr.job'].sudo().search([
                ('department_id', 'child_of', [5])
            ])
            values.update({
                'page_name': 'edit_contact',
                'contact': contact,
                'available_professionals': available_professionals,
                'available_job_types': available_job_types,
                'error_message': ' '.join(errors),
            })
            return request.render("contacts_patient.contact_edit_form", values)

        # Aggiornamento del contatto e della scheda clinica
        try:

            contact.write(vals)
            return request.redirect(f'/my/patient/{contact_id}/clinical-sheet')
        except Exception as e:
            request.env['ir.logging'].sudo().create({
                'name': 'Contact Save Error',
                'type': 'server',
                'level': 'ERROR',
                'message': f'Error updating contact {contact_id}: {str(e)}',
                'path': 'contacts_patient.portal',
                'line': '0',
                'func': 'portal_contact_edit_submit'
            })

            values = self._prepare_portal_layout_values()
            available_professionals = request.env['hr.employee'].sudo().search([
                ('job_id.department_id', 'child_of', [5])
            ])
            available_job_types = request.env['hr.job'].sudo().search([
                ('department_id', 'child_of', [5])
            ])
            values.update({
                'page_name': 'edit_contact',
                'contact': contact,

                'available_professionals': available_professionals,
                'available_job_types': available_job_types,
                'error_message': str(e),

            })
            return request.render("contacts_patient.contact_edit_form", values)
        
    # Aggiungi questa route al controller PatientPortal - MODIFICATO per includere nuovi campi
    @http.route(['/my/equipe_info'], type='http', auth="user", website=True)
    def portal_my_equipe_info_page(self, **kw):
        # Ottieni il partner dell'utente corrente
        partner = request.env.user.partner_id
        
        # Inizializza il dizionario per le informazioni dell'équipe
        equipe = {}
        
        # Recupera tutor e professionista (Many2one su hr.employee)
        tutor = partner.tutor if hasattr(partner, 'tutor') else False
        professional = partner.professional if hasattr(partner, 'professional') else False
        
        # Funzione per estrarre le informazioni dell'employee - MODIFICATO per includere nuovi campi
        def employee_info(employee):
            if not employee:
                return {}
            return {
                'name': employee.name,
                'job_title': employee.job_title,
                'professional_id': employee.professional_id,  # Numero iscrizione ordine
                'professional_type': employee.professional_type,  # Ordine/associazione
                'region': employee.region,  # Regione
                'registration_date': employee.registration_date,  # Data di registrazione
                'employee_id': employee.id,  # Aggiungi l'ID per costruire l'URL
                'has_image': bool(employee.image_1920),  # Flag per verificare se ha immagine
            }
        
        # Ottieni le informazioni di tutor e professionista
        equipe['tutor'] = employee_info(tutor)
        equipe['professional'] = employee_info(professional)
        
        # Passa i valori al template
        values = {
            'equipe': equipe,
            'page_name': 'equipe_info',
        }
        
        # Renderizza il template
        return request.render("contacts_patient.portal_my_equipe", values)

    @http.route(['/my/patient/<int:patient_id>/clinical-sheet'], type='http', auth="user", website=True)
    def clinical_sheet_portal(self, patient_id, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return request.redirect('/my')
            
        contact = request.env['res.partner'].sudo().browse(patient_id)
        if not contact.exists() or not contact.is_patient or not self._employee_has_access_to_contact(employee, contact):
            return request.redirect('/my/assigned_contacts')

        clinical_sheet = contact.clinical_sheet_id
        if not clinical_sheet:
            clinical_sheet = request.env['clinical.sheet'].sudo().create({'partner_id': contact.id})
            contact.clinical_sheet_id = clinical_sheet.id

        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'clinical_sheet', 
            'contact': contact, 
            'clinical_sheet': clinical_sheet
        })
        return request.render('contacts_patient.clinical_sheet_portal', values)

    @http.route(['/my/patient/<int:patient_id>/clinical-sheet/save'], type='http', auth="user", methods=['POST'], website=True)
    def clinical_sheet_save(self, patient_id, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return request.redirect('/my')
            
        contact = request.env['res.partner'].sudo().browse(patient_id)
        if not contact.exists() or not contact.is_patient or not self._employee_has_access_to_contact(employee, contact):
            return request.redirect('/my/assigned_contacts')

        clinical_sheet = contact.clinical_sheet_id
        if not clinical_sheet:
            clinical_sheet = request.env['clinical.sheet'].sudo().create({'partner_id': contact.id})
            contact.clinical_sheet_id = clinical_sheet.id

        # Raccogli tutti i campi dal form
        update_vals = {}
        
        # Lista di tutti i campi che possono essere aggiornati
        allowed_fields = [
            # Sezione 1: Consultazione
            'reason_for_consultation', 'symptoms_duration', 'triggering_factors', 'daily_life_impact',
            
            # Sezione 2: Anamnesi Psichiatrica
            'previous_psychiatric_diagnoses', 'previous_psychotherapies', 'previous_medications',
            'psychiatric_hospitalizations', 'previous_suicide_attempts', 'suicide_attempts_details',
            'self_harm_behaviors', 'self_harm_details', 'aggressive_behaviors', 'aggressive_details',
            'family_psychiatric_history', 'family_history_details',
            
            # Sezione 3: Anamnesi Medica
            'chronic_diseases', 'chronic_diseases_details', 'previous_surgeries', 'surgeries_details',
            'current_medications', 'allergies', 'allergies_details', 'pregnancy_breastfeeding', 'pregnancy_weeks',
            
            # Sezione 4: Sostanze
            'smoking', 'smoking_details', 'alcohol', 'alcohol_details', 'illegal_drugs', 'drugs_details',
            
            # Sezione 5: Sociale/Familiare
            'living_situation', 'social_support', 'social_support_description', 'significant_relationships',
            'developmental_history', 'family_context', 'social_context', 'work_context', 'cultural_aspects',
            
            # Sezione 6: Sintomi Attuali
            'problem_description', 'symptoms_onset', 'current_issues', 'sadness_depression', 'anhedonia',
            'irritability_anger', 'euphoria_elevated_mood', 'emotional_lability', 'generalized_anxiety',
            'panic_attacks', 'phobias', 'ocd_symptoms', 'ptsd_symptoms', 'hallucinations', 'delusions',
            'thought_disorganization', 'concentration_difficulties', 'memory_problems', 'planning_difficulties',
            'sleep_disturbances', 'appetite_changes', 'fatigue', 'somatic_symptoms',
            
            # Sezione 7: Esame Psichico
            'appearance_hygiene', 'attitude', 'mimics_gestures', 'psychomotor_activity', 'language_quality',
            'language_quantity', 'language_tone', 'reported_mood', 'observed_affect', 'thought_form',
            'thought_content', 'exam_hallucinations', 'illusions', 'derealization', 'orientation',
            'attention_concentration', 'memory_exam', 'abstraction_capacity', 'insight', 'judgment',
            
            # Sezione 8: Valutazione Rischio
            'risk_assessment', 'suicidal_ideation', 'suicide_planning', 'suicide_plan_details',
            'suicide_intention', 'suicide_means_available', 'suicide_means_details', 'suicide_risk_factors',
            'aggressive_ideation', 'aggression_target', 'aggression_planning', 'aggression_plan_details',
            'aggression_intention', 'aggression_means_available', 'aggression_means_details',
            'aggression_risk_factors', 'hygiene_risk', 'nutrition_risk', 'medication_risk',
            'financial_risk', 'housing_risk', 'exploitation_vulnerability', 'self_care_impact',
            
            # Sezione 9: Fattori Protettivi
            'individual_protective_factors', 'social_protective_factors', 'treatment_engagement', 'stability_factors',
            
            # Sezione 10: Conclusioni
            'patient_expectations', 'clinical_summary', 'diagnostic_hypotheses', 'main_problem_areas',
            'relevant_risk_protective_factors', 'primary_diagnosis', 'secondary_diagnosis', 'diagnosis_code',
            'diagnostic_criteria', 'differential_diagnosis', 'comorbidity', 'treatment_goals', 'treatment_plan'
        ]
        
        # Processa i campi dal form
        for field_name in allowed_fields:
            if field_name in kw:
                value = kw[field_name]
                
                # Gestione campi booleani (checkbox)
                if field_name in ['previous_suicide_attempts', 'self_harm_behaviors', 'aggressive_behaviors',
                                 'family_psychiatric_history', 'chronic_diseases', 'previous_surgeries', 'allergies',
                                 'smoking', 'alcohol', 'illegal_drugs', 'suicide_means_available',
                                 'aggression_means_available', 'hygiene_risk', 'nutrition_risk', 'medication_risk',
                                 'financial_risk', 'housing_risk', 'exploitation_vulnerability']:
                    update_vals[field_name] = bool(value and value != '0')
                
                # Gestione campi data
                elif field_name == 'symptoms_onset':
                    if value:
                        try:
                            from datetime import datetime
                            update_vals[field_name] = datetime.strptime(value, '%Y-%m-%d').date()
                        except (ValueError, TypeError):
                            pass
                
                # Gestione campi testo e selezione
                else:
                    update_vals[field_name] = value or False
        
        # Aggiorna la scheda clinica
        if update_vals:
            try:
                clinical_sheet.sudo().write(update_vals)
            except Exception as e:
                request.env['ir.logging'].sudo().create({
                    'name': 'Clinical Sheet Save Error',
                    'type': 'server',
                    'level': 'ERROR',
                    'message': f'Error saving clinical sheet for patient {patient_id}: {str(e)}',
                    'path': 'contacts_patient.portal',
                    'line': '0',
                    'func': 'clinical_sheet_save'
                })
                values = self._prepare_portal_layout_values()
                values.update({
                    'page_name': 'clinical_sheet',
                    'contact': contact,
                    'clinical_sheet': clinical_sheet,
                    'error_message': _('An error occurred while saving the clinical sheet. Please try again later.')
                })
                return request.render('contacts_patient.clinical_sheet_portal', values)

        return request.redirect(f'/my/patient/{patient_id}/clinical-sheet')

    @http.route([
        '/my/patient/<int:patient_id>/observations',
        '/my/patient/<int:patient_id>/observations/page/<int:page>'
    ], type='http', auth='user', website=True)
    def clinical_observation_list(self, patient_id, page=1, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return request.redirect('/my')

        contact = request.env['res.partner'].sudo().browse(patient_id)
        if not contact.exists() or not contact.is_patient or not self._employee_has_access_to_contact(employee, contact):
            return request.redirect('/my/assigned_contacts')

        if not contact.clinical_sheet_id:
            contact.clinical_sheet_id = request.env['clinical.sheet'].sudo().create({'partner_id': contact.id})

        domain = [('clinical_sheet_id', '=', contact.clinical_sheet_id.id)]
        observation_obj = request.env['clinical.observation'].sudo()
        observations_count = observation_obj.search_count(domain)

        pager = portal_pager(
            url=f'/my/patient/{patient_id}/observations',
            total=observations_count,
            page=page,
            step=self._items_per_page
        )

        observations = observation_obj.search(domain, order='date_created desc', limit=self._items_per_page, offset=pager['offset'])

        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'observations_list',
            'contact': contact,
            'observations': observations,
            'pager': pager,
        })
        return request.render('contacts_patient.clinical_observation_list', values)

    @http.route(['/my/patient/<int:patient_id>/observations/create'], type='http', auth='user', website=True, methods=['GET'])
    def clinical_observation_create(self, patient_id, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return request.redirect('/my')

        contact = request.env['res.partner'].sudo().browse(patient_id)
        if not contact.exists() or not contact.is_patient or not self._employee_has_access_to_contact(employee, contact):
            return request.redirect('/my/assigned_contacts')

        if not contact.clinical_sheet_id:
            contact.clinical_sheet_id = request.env['clinical.sheet'].sudo().create({'partner_id': contact.id})

        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'observation_edit',
            'contact': contact,
            'observation': False,
            'form_action': f'/my/patient/{patient_id}/observations/create'
        })
        return request.render('contacts_patient.clinical_observation_form', values)

    @http.route(['/my/patient/<int:patient_id>/observations/create'], type='http', auth='user', website=True, methods=['POST'])
    def clinical_observation_create_post(self, patient_id, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return request.redirect('/my')

        contact = request.env['res.partner'].sudo().browse(patient_id)
        if not contact.exists() or not contact.is_patient or not self._employee_has_access_to_contact(employee, contact):
            return request.redirect('/my/assigned_contacts')

        if not contact.clinical_sheet_id:
            contact.clinical_sheet_id = request.env['clinical.sheet'].sudo().create({'partner_id': contact.id})

        observation_text = kw.get('observation_text')
        if observation_text:
            request.env['clinical.observation'].sudo().create({
                'clinical_sheet_id': contact.clinical_sheet_id.id,
                'observation_text': observation_text,
                'author_id': request.env.user.id,
            })

        return request.redirect(f'/my/patient/{patient_id}/observations')

    @http.route(['/my/patient/<int:patient_id>/observations/<int:obs_id>/edit'], type='http', auth='user', website=True, methods=['GET'])
    def clinical_observation_edit(self, patient_id, obs_id, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return request.redirect('/my')

        contact = request.env['res.partner'].sudo().browse(patient_id)
        if not contact.exists() or not contact.is_patient or not self._employee_has_access_to_contact(employee, contact):
            return request.redirect('/my/assigned_contacts')

        observation = request.env['clinical.observation'].sudo().browse(obs_id)
        if not observation.exists() or observation.clinical_sheet_id != contact.clinical_sheet_id:
            return request.redirect(f'/my/patient/{patient_id}/observations')

        if observation.author_id.id != request.env.user.id and not request.env.user.has_group('base.group_system'):
            return request.redirect(f'/my/patient/{patient_id}/observations')

        values = self._prepare_portal_layout_values()
        values.update({
            'page_name': 'observation_edit',
            'contact': contact,
            'observation': observation,
            'form_action': f'/my/patient/{patient_id}/observations/{obs_id}/edit'
        })
        return request.render('contacts_patient.clinical_observation_form', values)

    @http.route(['/my/patient/<int:patient_id>/observations/<int:obs_id>/edit'], type='http', auth='user', website=True, methods=['POST'])
    def clinical_observation_edit_post(self, patient_id, obs_id, **kw):
        employee = request.env.user.employee_id
        if not employee:
            return request.redirect('/my')

        contact = request.env['res.partner'].sudo().browse(patient_id)
        if not contact.exists() or not contact.is_patient or not self._employee_has_access_to_contact(employee, contact):
            return request.redirect('/my/assigned_contacts')

        observation = request.env['clinical.observation'].sudo().browse(obs_id)
        if not observation.exists() or observation.clinical_sheet_id != contact.clinical_sheet_id:
            return request.redirect(f'/my/patient/{patient_id}/observations')

        if observation.author_id.id != request.env.user.id and not request.env.user.has_group('base.group_system'):
            return request.redirect(f'/my/patient/{patient_id}/observations')

        observation_text = kw.get('observation_text')
        if observation_text:
            observation.sudo().write({'observation_text': observation_text})

        return request.redirect(f'/my/patient/{patient_id}/observations')

    @http.route('/my/search/professionals', type='http', auth='user', methods=['GET'], website=False)
    def search_professionals(self, region=None, job_id=None, q=None, department_id=None, category_ids=None, **kw):
        """Return professionals filtered by region, job, department and name"""
        try:
            domain = []
            dep_filter = 5
            if department_id:
                try:
                    dep_filter = int(department_id)
                except (ValueError, TypeError):
                    _logger.warning('Invalid department_id parameter: %s', department_id)
            domain.append(('job_id.department_id', 'child_of', dep_filter))
            if region:
                domain.append(('region', '=', region))
            if job_id:
                try:
                    domain.append(('job_id', '=', int(job_id)))
                except (ValueError, TypeError):
                    _logger.warning('Invalid job_id parameter: %s', job_id)
            if category_ids:
                try:
                    if isinstance(category_ids, str):
                        category_ids = [int(t) for t in category_ids.split(',') if t]
                    else:
                        if not isinstance(category_ids, list):
                            category_ids = [category_ids]
                        category_ids = [int(t) for t in category_ids]
                    if category_ids:
                        domain.append(('specializzazioni', 'in', category_ids))
                except (ValueError, TypeError):
                    _logger.warning('Invalid category_ids parameter: %s', category_ids)
            if q:
                domain.append(('name', 'ilike', q))

            _logger.debug('Professional search domain: %s', domain)

            employees = request.env['hr.employee'].sudo().search(domain, limit=50)
            professionals = [{
                'id': e.id,
                'name': e.name,
                'job_title': e.job_title,
                'job_id': e.job_id.id,
                'job_name': e.job_id.name,
                'region': e.region,
                'professional_id': e.professional_id,
                'mobile_phone': e.mobile_phone,
                'work_email': e.work_email,
                'tags': [{'id': t.id, 'name': t.name} for t in e.specializzazioni],
            } for e in employees]

            region_groups = request.env['hr.employee'].sudo().read_group(
                [('job_id.department_id', 'child_of', dep_filter)], ['region'], ['region']
            )
            regions = sorted([g['region'] for g in region_groups if g['region']])

            data = {
                'professionals': professionals,
                'regions': regions,
            }
            return request.make_json_response(data)
        except Exception as e:
            _logger.exception('Error searching professionals: %s', e)
            return request.make_json_response({'error': 'Server Error'}, status=500)

    @http.route('/my/search/departments', type='http', auth='user', methods=['GET'], website=False)
    def get_departments(self, **kw):
        """Return list of departments in hierarchical order limited to depth 3"""
        try:
            Department = request.env['hr.department'].sudo()
            all_deps = Department.search([])

            def get_level(dep):
                level = 0
                current = dep.parent_id
                while current:
                    level += 1
                    current = current.parent_id
                return level

            departments = []
            visited = set()
            root_deps = all_deps.filtered(lambda d: not d.parent_id)

            def traverse(dep):
                if dep.id in visited:
                    return
                visited.add(dep.id)
                level = get_level(dep)
                if level > 2:
                    return
                name = ('- ' * level) + dep.name
                departments.append({
                    'id': dep.id,
                    'name': name,
                    'level': level,
                    'parent_id': dep.parent_id.id if dep.parent_id else False,
                })
                children = all_deps.filtered(lambda d: d.parent_id.id == dep.id)
                for child in children:
                    traverse(child)

            for d in root_deps:
                traverse(d)

            _logger.debug('Fetched departments: %s', departments)
            return request.make_json_response({'departments': departments})
        except Exception as e:
            _logger.exception('Error fetching departments: %s', e)
            return request.make_json_response({'departments': []}, status=500)

    @http.route('/my/search/tags', type='http', auth='user', methods=['GET'], website=False)
    def get_tags(self, **kw):
        """Return unique professional tags"""
        try:
            _logger.debug('Fetching specializations for department 5')
            employees = request.env['hr.employee'].sudo().search([
                ('job_id.department_id', 'child_of', [5]),
                ('specializzazioni', '!=', False)
            ])
            if not employees:
                _logger.info('No employees with specializations found in department 5')

            specialization_ids = set()
            for emp in employees:
                if emp.specializzazioni:
                    specialization_ids.update(emp.specializzazioni.ids)

            if not specialization_ids:
                _logger.info('No specializations found, attempting fallback')
                fallback = request.env['hr.specialization'].sudo().search([], limit=1)
                if fallback:
                    specialization_ids.add(fallback.id)

            tags = request.env['hr.specialization'].sudo().browse(list(specialization_ids))
            data = [{'id': t.id, 'name': t.name} for t in tags if t.exists()]
            _logger.debug('Specializations returned: %s', data)
            return request.make_json_response({'tags': data})
        except Exception as e:
            _logger.exception('Error fetching specializations: %s', e)
            return request.make_json_response({'tags': []}, status=500)

    @http.route('/my/search/jobs', type='http', auth='user', methods=['GET'], website=False)
    def get_jobs_by_department(self, department_id=None, **kw):
        """Return jobs filtered by department"""
        if not department_id:
            return request.make_json_response({'error': 'department_id required'}, status=400)
        try:
            department_id = int(department_id)
        except (ValueError, TypeError):
            return request.make_json_response({'error': 'invalid department_id'}, status=400)
        try:
            jobs = request.env['hr.job'].sudo().search([('department_id', 'child_of', department_id)])
            data = [{'id': j.id, 'name': j.name} for j in jobs]
            _logger.debug('Jobs for dept %s: %s', department_id, data)
            return request.make_json_response({'jobs': data})
        except Exception as e:
            _logger.exception('Error fetching jobs: %s', e)
            return request.make_json_response({'error': 'Server Error'}, status=500)
