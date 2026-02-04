# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict
import werkzeug
import logging

import base64
from datetime import datetime
import pytz
from odoo import http
from odoo.http import request
from odoo import models
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

from odoo.osv.expression import OR

_logger = logging.getLogger(__name__)

class CustomerPortal(CustomerPortal):
    _items_per_page = 10


    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        partner = request.env.user.partner_id
 
        CalendarMeeting = request.env['calendar.event']
        custom_meeting_count = CalendarMeeting.search_count([
            ('partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('active', '=', True),
            ('res_model', '!=', 'hr.leave'),
        ])
        values.update({
            'custom_meeting_count': custom_meeting_count,
        })
        return values

    def _meeting_get_page_view_values(self, custom_meeting_request, access_token, **kwargs):
        partner = request.env.user.partner_id
        attendee = request.env['calendar.attendee'].sudo().search([
            ('event_id', '=', custom_meeting_request.id),
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
        ], limit=1)

        values = {
            'page_name': 'custom_meeting_page_probc',
            'custom_meeting_request': custom_meeting_request,
            'show_confirm_button': bool(attendee and attendee.state != 'accepted'),
        }

        return self._get_page_view_values(custom_meeting_request, access_token, values, 'my_meeting_history', False, **kwargs)

    def _is_employee_user(self):
        """
        Verifica se l'utente corrente è un dipendente.
        Un utente è considerato dipendente se ha almeno un record in hr.employee collegato.
        """
        user = request.env.user
        # Controlla se esiste un employee collegato a questo utente
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        return bool(employee)

    def _get_portal_meeting_allowed_partners_domain(self, employee):
        domain = [
            ('is_company', '=', False),     # Solo persone fisiche
            ('email', '!=', False),         # Solo partner con email
            ('active', '=', True),          # Solo partner attivi
        ]

        if employee:
            domain.extend([
                '|',
                ('tutor', '=', employee.id),
                ('professional', '=', employee.id),
            ])

        return domain

    @http.route(['/my/custom_meeting_request', '/my/custom_meeting_request/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_custom_meeting(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='name', **kw):

        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        meeting_obj = http.request.env['calendar.event']
        domain = [
            ('partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('active', '=', True),
            ('res_model', '!=', 'hr.leave'),
        ]

        attendee_obj = request.env['calendar.attendee'].sudo()
        unconfirmed_ids = attendee_obj.search([
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
            ('state', '!=', 'accepted'),
            ('event_id.active', '=', True),
            ('event_id.res_model', '!=', 'hr.leave'),
        ]).mapped('event_id').ids

        outcome_obj = request.env['calendar.event.outcome'].sudo()
        outcomes = outcome_obj.search([('active', '=', True)])

        searchbar_filters = {
            'all': {'label': request.env._('All'), 'domain': []},
            'unconfirmed': {'label': request.env._('Non confermati'), 'domain': [('id', 'in', unconfirmed_ids)]},
            'no_outcome': {'label': request.env._('Senza esito'), 'domain': [('esito_evento_id', '=', False)]},
        }

        for outcome in outcomes:
            searchbar_filters[f'outcome_{outcome.id}'] = {
                'label': outcome.display_name,
                'domain': [('esito_evento_id', '=', outcome.id)],
            }

        searchbar_sortings = {
            'start': {'label': request.env._('Start Date Ascending'), 'order': 'start'},
            'start desc': {'label': request.env._('Start Date Descending'), 'order': 'start desc'},
        }

        searchbar_inputs = {
            'name': {'input': 'name', 'label': request.env._('Search in Subject')},
        }

        if not sortby or sortby not in searchbar_sortings:
            sortby = 'start'
        order = searchbar_sortings[sortby]['order']

        if not filterby or filterby not in searchbar_filters:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            domain += search_domain

        custom_meeting_count = meeting_obj.sudo().search_count(domain)

        pager = portal_pager(
            url="/my/custom_meeting_request",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'filterby': filterby},
            total=custom_meeting_count,
            page=page,
            step=self._items_per_page
        )

        meetings = meeting_obj.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        # AGGIUNTA: Verifica se l'utente è un dipendente per mostrare il pulsante di creazione
        is_employee = self._is_employee_user()
        
        # AGGIUNTA: Gestione messaggio di successo dopo creazione
        success_message = kw.get('success')

        values.update({
            'meetings': meetings,
            'page_name': 'custom_meeting_page_probc',
            'pager': pager,
            'default_url': '/my/custom_meeting_request',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_filters': searchbar_filters,
            'search_in': search_in,
            'sortby': sortby,
            'filterby': filterby,
            'is_employee': is_employee,  # AGGIUNTA: flag per mostrare pulsante creazione
            'success_message': success_message,  # AGGIUNTA: messaggio successo
        })
        return request.render("calendar_meeting_portal.portal_my_meeting_custom", values)

    @http.route(['/my/custom_meeting_request/<int:meeting_id>'], type='http', auth="public", website=True)
    def custom_portal_my_meeting(self, meeting_id, access_token=None, **kw):
        try:
            meeting_sudo = self._document_check_access('calendar.event', meeting_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._meeting_get_page_view_values(meeting_sudo, access_token, **kw)
        values.update({
            'confirm_message': kw.get('confirm'),
            'is_employee': self._is_employee_user(),
            'success_message': kw.get('success'),
            'error_message': kw.get('error'),
        })
        return request.render("calendar_meeting_portal.custom_portal_my_meeting", values)

    @http.route(['/my/custom_meeting_request/<int:meeting_id>/confirm'], type='http', auth="user")
    def custom_meeting_confirm(self, meeting_id, **kw):
        meeting = request.env['calendar.event'].sudo().browse(meeting_id)
        partner = request.env.user.partner_id
        if not meeting.partner_ids.filtered_domain([('id', 'child_of', partner.commercial_partner_id.id)]):
            return request.redirect('/my')
        attendee = request.env['calendar.attendee'].sudo().search([
            ('event_id', '=', meeting_id),
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
        ], limit=1)
        if attendee:
            attendee.write({'state': 'accepted'})
        return request.redirect('/my/custom_meeting_request/%s?confirm=1' % meeting_id)

    @http.route(['/my/custom_meeting_request/<int:meeting_id>/cancel'], type='http', auth="user")
    def custom_meeting_cancel(self, meeting_id, **kw):
        meeting = request.env['calendar.event'].sudo().browse(meeting_id)
        partner = request.env.user.partner_id
        if not meeting.partner_ids.filtered_domain([('id', 'child_of', partner.commercial_partner_id.id)]):
            return request.redirect('/my')
        meeting.write({'active': False})
        try:
            meeting.message_post(
                body=request.env._('The meeting has been cancelled.'),
                message_type='email',
                partner_ids=meeting.partner_ids.ids,
            )
        except Exception as e:
            _logger.warning("Failed to send meeting cancellation email: %s", e)
        return request.redirect('/my/custom_meeting_request')

    # NUOVE ROUTE PER CREAZIONE APPUNTAMENTI

    @http.route(['/my/meeting/create'], type='http', auth="user", website=True)
    def portal_meeting_create(self, **kw):
        """
        Mostra il form per la creazione di un nuovo appuntamento.
        Accessibile solo ai dipendenti.
        """
        # Verifica che l'utente sia un dipendente
        if not self._is_employee_user():
            return request.redirect('/my')

        # Recupera il dipendente collegato all'utente corrente
        employee = request.env['hr.employee'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        # Recupera la lista dei partner/pazienti assegnati al dipendente
        # Filtra per pazienti che hanno il dipendente come tutor O professionista
        domain = self._get_portal_meeting_allowed_partners_domain(employee)
        partners = request.env['res.partner'].sudo().search(domain, order='name')

        # Recupera il timezone dell'utente
        user_tz = request.env.user.tz or 'UTC'
        
        # Normalizza partner_id (singolo) da query string
        partner_id_raw = kw.get('partner_id')
        partner_id = False
        if partner_id_raw:
            try:
                partner_id = int(partner_id_raw)
            except (ValueError, TypeError):
                partner_id = False
        kw['partner_id'] = partner_id or ''

        # Se abbiamo partner_id ma non un testo da mostrare, prova a derivarlo (solo se permesso dal domain)
        if partner_id and not (kw.get('partner_name') or kw.get('partner_id_search')):
            allowed_partner = request.env['res.partner'].sudo().search(domain + [('id', '=', partner_id)], limit=1)
            if allowed_partner:
                kw['partner_name'] = allowed_partner.name + (f" ({allowed_partner.email})" if allowed_partner.email else '')
        
        values = {
            'page_name': 'meeting_create',
            'partners': partners,
            'form_data': kw,  # Per mantenere i dati in caso di errore
            'error_message': kw.get('error'),
            'user_timezone': user_tz,  # Passa il timezone al template
        }
        
        return request.render("calendar_meeting_portal.portal_meeting_create", values)

    @http.route(['/my/meeting/save'], type='http', auth="user", website=True, methods=['POST'], csrf=True)
    def portal_meeting_save(self, **post):
        """
        Salva il nuovo appuntamento creato dal form.
        Accessibile solo ai dipendenti.
        """
        # Verifica che l'utente sia un dipendente
        if not self._is_employee_user():
            return request.redirect('/my')

        try:
            # Validazione campi obbligatori
            meeting_name = post.get('meeting_name', '').strip()
            start_date_str = post.get('start_date', '').strip()
            end_date_str = post.get('end_date', '').strip()

            if not meeting_name:
                raise ValidationError(request.env._("Il nome dell'appuntamento è obbligatorio."))
            
            if not start_date_str:
                raise ValidationError(request.env._("La data di inizio è obbligatoria."))
                
            if not end_date_str:
                raise ValidationError(request.env._("La data di fine è obbligatoria."))

            # Conversione e validazione date con gestione timezone
            try:
                # Recupera il timezone dell'utente
                user_tz_name = request.env.user.tz or 'UTC'
                user_tz = pytz.timezone(user_tz_name)
                
                # Parse delle date come datetime naive (senza timezone)
                start_date_naive = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
                end_date_naive = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
                
                # Localizza le date nel timezone dell'utente
                start_date_local = user_tz.localize(start_date_naive)
                end_date_local = user_tz.localize(end_date_naive)
                
                # Converti in UTC per il salvataggio nel database e rimuovi tzinfo (richiesto da Odoo)
                start_date = start_date_local.astimezone(pytz.UTC).replace(tzinfo=None)
                end_date = end_date_local.astimezone(pytz.UTC).replace(tzinfo=None)
                
            except ValueError:
                raise ValidationError(request.env._("Formato data non valido."))
            except pytz.exceptions.UnknownTimeZoneError:
                raise ValidationError(request.env._("Timezone non valido."))

            if end_date <= start_date:
                raise ValidationError(request.env._("La data di fine deve essere successiva alla data di inizio."))

            # Validazione partecipante (obbligatorio e deve essere tra quelli permessi)
            partner_id_raw = (post.get('partner_id') or '').strip()
            if not partner_id_raw:
                raise ValidationError(request.env._("Seleziona un partecipante."))

            try:
                partner_id = int(partner_id_raw)
            except (ValueError, TypeError):
                raise ValidationError(request.env._("Partecipante non valido."))

            employee = request.env['hr.employee'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            domain = self._get_portal_meeting_allowed_partners_domain(employee)
            allowed_partner = request.env['res.partner'].sudo().search(domain + [('id', '=', partner_id)], limit=1)
            if not allowed_partner:
                raise ValidationError(request.env._("Partecipante non valido o non autorizzato."))

            # Preparazione dei dati per il meeting
            user = request.env.user
            meeting_vals = {
                'name': meeting_name,
                'start': start_date,
                'stop': end_date,
                'user_id': user.id,
                'description': post.get('description', ''),
                'location': post.get('location', ''),
                'allday': False,
            }

            # Gestione partecipanti
            attendee_ids = [user.partner_id.id]

            # Aggiungi il partecipante selezionato (singolo)
            if partner_id not in attendee_ids:
                attendee_ids.append(partner_id)

            meeting_vals['partner_ids'] = [(6, 0, attendee_ids)]

            # Creazione del meeting
            meeting = request.env['calendar.event'].sudo().with_context(dont_notify=False, from_portal=True).create(meeting_vals)

            # INVIO EMAIL INVITO AI PARTECIPANTI (template standard Odoo)
            # Nota: il template calendar.calendar_template_meeting_invitation lavora su calendar.attendee (res_id=attendee.id)
            try:
                template = request.env.ref('calendar.calendar_template_meeting_invitation', raise_if_not_found=False)
                if not template:
                    _logger.warning(
                        "Template email invito meeting non trovato: calendar.calendar_template_meeting_invitation. "
                        "Meeting ID: %s",
                        meeting.id,
                    )
                else:
                    template = template.sudo()
                    attendees = meeting.sudo().attendee_ids
                    total_attendees = len(attendees)
                    sent_count = 0
                    skipped_no_email = 0
                    skipped_creator = 0
                    sent_to = []

                    _logger.info(
                        "Invio inviti meeting: meeting_id=%s, attendees_totali=%s",
                        meeting.id,
                        total_attendees,
                    )

                    creator_partner_id = request.env.user.partner_id.id

                    for attendee in attendees:
                        partner = attendee.partner_id
                        email_to = (partner.email or '').strip() if partner else ''

                        if not partner or not email_to:
                            skipped_no_email += 1
                            _logger.info(
                                "Invito meeting saltato (no email): meeting_id=%s, attendee_id=%s, partner_id=%s",
                                meeting.id,
                                attendee.id,
                                partner.id if partner else False,
                            )
                            continue

                        if partner.id == creator_partner_id:
                            skipped_creator += 1
                            _logger.info(
                                "Invito meeting saltato (creatore): meeting_id=%s, attendee_id=%s, partner_id=%s, email=%s",
                                meeting.id,
                                attendee.id,
                                partner.id,
                                email_to,
                            )
                            continue

                        try:
                            template.send_mail(
                                attendee.id,
                                force_send=True,
                                email_values={'email_to': email_to},
                            )
                            sent_count += 1
                            sent_to.append(email_to)
                            _logger.info(
                                "Invito meeting inviato: meeting_id=%s, attendee_id=%s, partner_id=%s, email=%s",
                                meeting.id,
                                attendee.id,
                                partner.id,
                                email_to,
                            )
                        except Exception:
                            _logger.exception(
                                "Errore invio invito meeting: meeting_id=%s, attendee_id=%s, partner_id=%s, email=%s",
                                meeting.id,
                                attendee.id,
                                partner.id,
                                email_to,
                            )

                    _logger.info(
                        "Invio inviti meeting completato: meeting_id=%s, attendees_totali=%s, email_inviate=%s, "
                        "saltate_no_email=%s, saltate_creatore=%s, destinatari=%s",
                        meeting.id,
                        total_attendees,
                        sent_count,
                        skipped_no_email,
                        skipped_creator,
                        sent_to,
                    )
            except Exception:
                # Non bloccare mai la creazione del meeting per problemi email
                _logger.exception(
                    "Errore inatteso durante l'invio degli inviti email per meeting_id=%s",
                    meeting.id,
                )

            # Invio notifiche ai partecipanti (Odoo lo fa automaticamente)
            # Il sistema di calendar di Odoo gestisce automaticamente l'invio delle email

            # Redirect alla lista con messaggio di successo
            return request.redirect('/my/custom_meeting_request?success=1')

        except ValidationError as e:
            # In caso di errore di validazione, ritorna al form con il messaggio di errore
            error_params = {
                'error': str(e),
                'meeting_name': post.get('meeting_name', ''),
                'start_date': post.get('start_date', ''),
                'end_date': post.get('end_date', ''),
                'description': post.get('description', ''),
                'location': post.get('location', ''),
                'partner_id': post.get('partner_id', ''),
                'partner_name': post.get('partner_id_search', ''),
            }
            return request.redirect('/my/meeting/create?' + werkzeug.urls.url_encode(error_params))

        except Exception as e:
            # Errore generico
            _logger.exception("Errore durante la creazione dell'appuntamento da portale")
            error_params = {
                'error': 'Si è verificato un errore durante la creazione dell\'appuntamento. Riprova.',
                'meeting_name': post.get('meeting_name', ''),
                'start_date': post.get('start_date', ''),
                'end_date': post.get('end_date', ''),
                'description': post.get('description', ''),
                'location': post.get('location', ''),
                'partner_id': post.get('partner_id', ''),
                'partner_name': post.get('partner_id_search', ''),
            }
            return request.redirect('/my/meeting/create?' + werkzeug.urls.url_encode(error_params))



    @http.route(['/my/custom_meeting_request/<int:meeting_id>/update_outcome'], type='http', auth="user", methods=['POST'], csrf=True, website=True)
    def custom_meeting_update_outcome(self, meeting_id, **post):
        """
        Aggiorna l'esito dell'appuntamento.
        Accessibile solo ai dipendenti che sono partecipanti al meeting.
        
        FASE 3: Implementazione validazioni sicurezza multi-livello:
        1. Verifica utente è dipendente
        2. Verifica dipendente è partecipante al meeting
        3. Validazione esito esiste e active=True
        4. Gestione errori con messaggi user-friendly
        """
        try:
            # VALIDAZIONE 1: Verifica che l'utente sia un dipendente
            employee = request.env['hr.employee'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
            
            if not employee:
                _logger.warning(
                    "Tentativo di aggiornamento esito da utente non dipendente. "
                    "User ID: %s, Meeting ID: %s",
                    request.env.user.id, meeting_id
                )
                error_msg = 'Non hai i permessi necessari per modificare questo appuntamento'
                params = werkzeug.urls.url_encode({'error': error_msg})
                return request.redirect(f'/my/custom_meeting_request/{meeting_id}?{params}')

            # Recupera il meeting
            meeting = request.env['calendar.event'].sudo().browse(meeting_id)
            
            # Verifica che il meeting esista
            if not meeting.exists():
                _logger.warning(
                    "Tentativo di aggiornamento esito per meeting inesistente. "
                    "User ID: %s, Meeting ID: %s",
                    request.env.user.id, meeting_id
                )
                return request.redirect('/my/custom_meeting_request')

            # VALIDAZIONE 2: Verifica che l'utente corrente sia tra i partecipanti del meeting
            current_partner = request.env.user.partner_id
            if not meeting.partner_ids.filtered(lambda p: p.id == current_partner.id):
                _logger.warning(
                    "Tentativo di aggiornamento esito da utente non partecipante. "
                    "User ID: %s, Partner ID: %s, Meeting ID: %s",
                    request.env.user.id, current_partner.id, meeting_id
                )
                error_msg = 'Non hai i permessi necessari per modificare questo appuntamento'
                params = werkzeug.urls.url_encode({'error': error_msg})
                return request.redirect(f'/my/custom_meeting_request/{meeting_id}?{params}')

            # Recupera il nuovo valore di esito_evento_id dai dati POST
            outcome_id_str = post.get('esito_evento_id')
            
            # Se il valore è vuoto o "False", rimuovi l'esito
            if not outcome_id_str or outcome_id_str == 'False':
                meeting.sudo().write({'esito_evento_id': False})
                return request.redirect(f'/my/custom_meeting_request/{meeting_id}?success=1')
            
            # VALIDAZIONE 3: Validazione esito esiste e active=True
            try:
                outcome_id = int(outcome_id_str)
            except (ValueError, TypeError):
                _logger.warning(
                    "Tentativo di aggiornamento esito con ID non valido. "
                    "User ID: %s, Meeting ID: %s, Outcome ID: %s",
                    request.env.user.id, meeting_id, outcome_id_str
                )
                error_msg = "L'esito selezionato non è valido o non è più disponibile"
                params = werkzeug.urls.url_encode({'error': error_msg})
                return request.redirect(f'/my/custom_meeting_request/{meeting_id}?{params}')
            
            # Verifica che l'esito esista e sia attivo
            outcome = request.env['calendar.event.outcome'].sudo().search([
                ('id', '=', outcome_id),
                ('active', '=', True)
            ], limit=1)
            
            if not outcome:
                _logger.warning(
                    "Tentativo di aggiornamento con esito inesistente o inattivo. "
                    "User ID: %s, Meeting ID: %s, Outcome ID: %s",
                    request.env.user.id, meeting_id, outcome_id
                )
                error_msg = "L'esito selezionato non è valido o non è più disponibile"
                params = werkzeug.urls.url_encode({'error': error_msg})
                return request.redirect(f'/my/custom_meeting_request/{meeting_id}?{params}')

            # Aggiorna il meeting con il nuovo esito
            meeting.sudo().write({'esito_evento_id': outcome_id})
            
            _logger.info(
                "Esito aggiornato con successo. "
                "User ID: %s, Meeting ID: %s, Outcome ID: %s (%s)",
                request.env.user.id, meeting_id, outcome_id, outcome.name
            )

            # Redirect alla pagina di dettaglio con messaggio di successo
            return request.redirect(f'/my/custom_meeting_request/{meeting_id}?success=1')

        except ValidationError as e:
            # In caso di errore di validazione
            _logger.error(
                "Errore di validazione durante aggiornamento esito. "
                "User ID: %s, Meeting ID: %s, Error: %s",
                request.env.user.id, meeting_id, str(e)
            )
            error_msg = str(e)
            params = werkzeug.urls.url_encode({'error': error_msg})
            return request.redirect(f'/my/custom_meeting_request/{meeting_id}?{params}')

        except AccessError as e:
            # In caso di errore di accesso
            _logger.error(
                "Errore di accesso durante aggiornamento esito. "
                "User ID: %s, Meeting ID: %s, Error: %s",
                request.env.user.id, meeting_id, str(e)
            )
            error_msg = 'Non hai i permessi necessari per modificare questo appuntamento'
            params = werkzeug.urls.url_encode({'error': error_msg})
            return request.redirect(f'/my/custom_meeting_request/{meeting_id}?{params}')

        except Exception as e:
            # Errore generico
            _logger.exception(
                "Errore generico durante aggiornamento esito. "
                "User ID: %s, Meeting ID: %s",
                request.env.user.id, meeting_id
            )
            error_msg = "Si è verificato un errore durante l'aggiornamento"
            params = werkzeug.urls.url_encode({'error': error_msg})
            return request.redirect(f'/my/custom_meeting_request/{meeting_id}?{params}')