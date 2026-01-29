# -*- coding: utf-8 -*-

import json
import pytz
import re

from pytz.exceptions import UnknownTimeZoneError

from babel.dates import format_datetime, format_date, format_time
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from markupsafe import Markup
from urllib.parse import quote, unquote_plus
from werkzeug.exceptions import Forbidden, NotFound
from werkzeug.urls import url_encode

from odoo import Command, exceptions, http, fields, _
from odoo.http import request, route
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf, email_normalize
from odoo.tools.mail import is_html_empty
from odoo.tools.misc import babel_locale_parse, get_lang
from odoo.addons.base.models.ir_qweb import keep_query
from odoo.addons.base.models.res_partner import _tz_get
from odoo.addons.phone_validation.tools import phone_validation
from odoo.exceptions import UserError
from odoo.addons.appointment.controllers.appointment import AppointmentController


class AppointmentControllerNoDuplicates(AppointmentController):
    """
    Estensione del controller degli appuntamenti per prevenire la creazione di contatti duplicati.
    
    Questo controller sovrascrive il metodo appointment_form_submit per implementare una logica
    di ricerca intelligente che:
    1. Cerca contatti esistenti per email normalizzata
    2. Se non trova, cerca per telefono formattato  
    3. Se trova un contatto, aggiorna solo i campi vuoti
    4. Solo se non trova nessun contatto, ne crea uno nuovo
    """

    def appointment_form_submit(self, appointment_type_id, datetime_str, duration_str, name, phone, email, staff_user_id=None, available_resource_ids=None, asked_capacity=1,
                                guest_emails_str=None, **kwargs):
        """
        Sovrascrive il metodo originale per implementare la ricerca di contatti duplicati.
        Mantiene tutti i parametri e la logica originale, modificando solo la sezione 
        di gestione del customer.
        """
        domain = self._appointments_base_domain(
            filter_appointment_type_ids=kwargs.get('filter_appointment_type_ids'),
            search=kwargs.get('search'),
            invite_token=kwargs.get('invite_token')
        )

        available_appointments = self._fetch_and_check_private_appointment_types(
            kwargs.get('filter_appointment_type_ids'),
            kwargs.get('filter_staff_user_ids'),
            kwargs.get('filter_resource_ids'),
            kwargs.get('invite_token'),
            domain=domain,
        )
        appointment_type = available_appointments.filtered(lambda appt: appt.id == int(appointment_type_id))

        if not appointment_type:
            raise NotFound()
        timezone = request.session.get('timezone') or appointment_type.appointment_tz
        tz_session = pytz.timezone(timezone)
        datetime_str = unquote_plus(datetime_str)
        date_start = tz_session.localize(fields.Datetime.from_string(datetime_str)).astimezone(pytz.utc).replace(tzinfo=None)
        duration = float(duration_str)
        date_end = date_start + relativedelta(hours=duration)
        invite_token = kwargs.get('invite_token')

        staff_user = request.env['res.users']
        resources = request.env['appointment.resource']
        resource_ids = None
        asked_capacity = int(asked_capacity)
        resources_remaining_capacity = None
        if appointment_type.schedule_based_on == 'resources':
            resource_ids = json.loads(unquote_plus(available_resource_ids))
            # Check if there is still enough capacity (in case someone else booked with a resource in the meantime)
            resources = request.env['appointment.resource'].sudo().browse(resource_ids).exists()
            if any(resource not in appointment_type.resource_ids for resource in resources):
                raise NotFound()
            resources_remaining_capacity = appointment_type._get_resources_remaining_capacity(resources, date_start, date_end, with_linked_resources=False)
            if resources_remaining_capacity['total_remaining_capacity'] < asked_capacity:
                return request.redirect('/appointment/%s?%s' % (appointment_type.id, keep_query('*', state='failed-resource')))
        else:
            # check availability of the selected user again (in case someone else booked while the client was entering the form)
            staff_user = request.env['res.users'].sudo().search([('id', '=', int(staff_user_id))])
            if staff_user not in appointment_type.staff_user_ids:
                raise NotFound()
            if staff_user and not staff_user.partner_id.calendar_verify_availability(date_start, date_end):
                return request.redirect('/appointment/%s?%s' % (appointment_type.id, keep_query('*', state='failed-staff-user')))

        guests = None
        if appointment_type.allow_guests:
            if guest_emails_str:
                guests = request.env['calendar.event'].sudo()._find_or_create_partners(guest_emails_str)

        # INIZIO MODIFICA: Sostituisce la chiamata a self._get_customer_partner() con la logica di ricerca duplicati
        customer = self._find_or_create_customer_smart(name, phone, email)
        # FINE MODIFICA

        # partner_inputs dictionary structures all answer inputs received on the appointment submission: key is question id, value
        # is answer id (as string) for choice questions, text input for text questions, array of ids for multiple choice questions.
        partner_inputs = {}
        appointment_question_ids = appointment_type.question_ids.ids
        for k_key, k_value in [item for item in kwargs.items() if item[1]]:
            question_id_str = re.match(r"\bquestion_([0-9]+)\b", k_key)
            if question_id_str and int(question_id_str.group(1)) in appointment_question_ids:
                partner_inputs[int(question_id_str.group(1))] = k_value
                continue
            checkbox_ids_str = re.match(r"\bquestion_([0-9]+)_answer_([0-9]+)\b", k_key)
            if checkbox_ids_str:
                question_id, answer_id = [int(checkbox_ids_str.group(1)), int(checkbox_ids_str.group(2))]
                if question_id in appointment_question_ids:
                    partner_inputs[question_id] = partner_inputs.get(question_id, []) + [answer_id]

        # The answer inputs will be created in _prepare_calendar_event_values from the values in answer_input_values
        answer_input_values = []
        base_answer_input_vals = {
            'appointment_type_id': appointment_type.id,
            'partner_id': customer.id,
        }

        for question in appointment_type.question_ids.filtered(lambda question: question.id in partner_inputs.keys()):
            if question.question_type == 'checkbox':
                answers = question.answer_ids.filtered(lambda answer: answer.id in partner_inputs[question.id])
                answer_input_values.extend([
                    dict(base_answer_input_vals, question_id=question.id, value_answer_id=answer.id) for answer in answers
                ])
            elif question.question_type in ['select', 'radio']:
                answer_input_values.append(
                    dict(base_answer_input_vals, question_id=question.id, value_answer_id=int(partner_inputs[question.id]))
                )
            elif question.question_type in ['char', 'text']:
                answer_input_values.append(
                    dict(base_answer_input_vals, question_id=question.id, value_text_box=partner_inputs[question.id].strip())
                )

        booking_line_values = []
        if appointment_type.schedule_based_on == 'resources':
            capacity_to_assign = asked_capacity
            for resource in resources:
                resource_remaining_capacity = resources_remaining_capacity.get(resource)
                new_capacity_reserved = min(resource_remaining_capacity, capacity_to_assign, resource.capacity)
                capacity_to_assign -= new_capacity_reserved
                booking_line_values.append({
                    'appointment_resource_id': resource.id,
                    'capacity_reserved': new_capacity_reserved,
                    'capacity_used': new_capacity_reserved if resource.shareable and appointment_type.resource_manage_capacity else resource.capacity,
                })

        if invite_token:
            appointment_invite = request.env['appointment.invite'].sudo().search([('access_token', '=', invite_token)])
        else:
            appointment_invite = request.env['appointment.invite']

        return self._handle_appointment_form_submission(
            appointment_type, date_start, date_end, duration, answer_input_values, name,
            customer, appointment_invite, guests, staff_user, asked_capacity, booking_line_values
        )

    def _find_or_create_customer_smart(self, name, phone, email):
        """
        Implementa la logica di ricerca intelligente per trovare contatti esistenti
        o creare un nuovo contatto solo se necessario.
        
        Strategia:
        1. Se utente autenticato, usa il partner dell'utente
        2. Altrimenti cerca per email normalizzata
        3. Se non trova, cerca per telefono formattato  
        4. Se trova un contatto, aggiorna solo i campi vuoti
        5. Se non trova nessun contatto, ne crea uno nuovo
        
        :param str name: nome dal form
        :param str phone: telefono dal form
        :param str email: email dal form
        :return: partner trovato o creato
        :rtype: res.partner
        """
        # Se l'utente è autenticato, usa il suo partner (comportamento originale)
        if not request.env.user._is_public():
            return request.env.user.partner_id
        
        # Per utenti pubblici, implementa la ricerca intelligente
        partner_model = request.env['res.partner'].sudo()
        found_partner = None
        
        # FASE 1: Ricerca per email normalizzata
        if email:
            try:
                normalized_email = email_normalize(email)
                if normalized_email:
                    # Cerca partner con email normalizzata, ordina per data di creazione (più recente primo)
                    found_partners = partner_model.search([
                        ('email_normalized', '=', normalized_email)
                    ], order='create_date desc', limit=1)
                    
                    if found_partners:
                        found_partner = found_partners[0]
            except Exception:
                # Se email_normalize fallisce, continua con la ricerca per telefono
                pass
        
        # FASE 2: Ricerca per telefono (solo se non trovato per email)
        if not found_partner and phone:
            try:
                # Ottieni il paese per la formattazione del telefono
                input_country = self._get_customer_country()
                formatted_phone = phone_validation.phone_format(
                    phone, 
                    input_country.code, 
                    input_country.phone_code, 
                    force_format="E164", 
                    raise_exception=False
                )
                
                if formatted_phone:
                    # Cerca partner con telefono formattato, ordina per data di creazione (più recente primo)
                    found_partners = partner_model.search([
                        ('phone', '=', formatted_phone)
                    ], order='create_date desc', limit=1)
                    
                    if found_partners:
                        found_partner = found_partners[0]
            except Exception:
                # Se phone_format fallisce, continua con la creazione di un nuovo partner
                pass
        
        # FASE 3: Aggiornamento partner esistente (se trovato)
        if found_partner:
            try:
                update_vals = {}
                
                # Aggiorna nome se vuoto
                if not found_partner.name and name:
                    update_vals['name'] = name
                
                # Aggiorna telefono se vuoto
                if not found_partner.phone and phone:
                    try:
                        input_country = self._get_customer_country()
                        formatted_phone = phone_validation.phone_format(
                            phone, 
                            input_country.code, 
                            input_country.phone_code, 
                            force_format="E164", 
                            raise_exception=False
                        )
                        update_vals['phone'] = formatted_phone or phone
                    except Exception:
                        update_vals['phone'] = phone
                
                # Aggiorna email se vuoto
                if not found_partner.email and email:
                    try:
                        normalized_email = email_normalize(email)
                        update_vals['email'] = normalized_email or email
                    except Exception:
                        update_vals['email'] = email
                
                # Applica gli aggiornamenti se necessari
                if update_vals:
                    found_partner.write(update_vals)
                
                return found_partner
                
            except Exception:
                # Se l'aggiornamento fallisce, ritorna il partner così com'è
                return found_partner
        
        # FASE 4: Creazione nuovo partner (solo se non trovato)
        try:
            # Prepara i dati per il nuovo partner
            create_vals = {
                'name': name,
                'lang': request.lang.code,
            }
            
            # Aggiungi email normalizzata
            if email:
                try:
                    normalized_email = email_normalize(email)
                    create_vals['email'] = normalized_email or email
                except Exception:
                    create_vals['email'] = email
            
            # Aggiungi telefono formattato
            if phone:
                try:
                    input_country = self._get_customer_country()
                    formatted_phone = phone_validation.phone_format(
                        phone, 
                        input_country.code, 
                        input_country.phone_code, 
                        force_format="E164", 
                        raise_exception=False
                    )
                    create_vals['phone'] = formatted_phone or phone
                except Exception:
                    create_vals['phone'] = phone
            
            # Crea il nuovo partner
            new_partner = partner_model.create(create_vals)
            return new_partner
            
        except Exception:
            # Fallback: crea partner con dati minimi per non interrompere il flusso
            fallback_partner = partner_model.create({
                'name': name or 'Cliente Appuntamento',
                'email': email or '',
                'phone': phone or '',
                'lang': request.lang.code,
            })
            return fallback_partner
