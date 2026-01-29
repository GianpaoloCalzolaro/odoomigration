from odoo import http, fields
from datetime import datetime, date
from odoo.http import request
from odoo.exceptions import ValidationError, UserError
import urllib.parse
import json


class PortalTimeOff(http.Controller):

    @http.route(['/my/time_off'], type='http', auth="user", website=True)
    def portal_time_off(self, **kwargs):
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        time_offs = request.env['hr.leave'].sudo().search([('employee_id.user_id', '=', user.id)])
        print("time off is:::", time_offs)
        leave_types = request.env['hr.leave.type'].sudo().search([])
        print("leave_types is:::", leave_types)
        
        resource_calendars = request.env['resource.calendar'].sudo().search([
            '|',
            ('employee_creator_id', '=', False),
            ('employee_creator_id', '=', employee.id if employee else False)
        ])
        
        # Recupera i calendari personali del dipendente per la sezione inline
        my_calendars = []
        if employee:
            my_calendars = request.env['resource.calendar'].sudo().search([
                ('employee_creator_id', '=', employee.id)
            ])
        
        return request.render('portal_time_off.portal_time_off_page', {
            'time_offs': time_offs,
            'leave_types': leave_types,
            'employee': employee,
            'resource_calendars': resource_calendars,
            'my_calendars': my_calendars,
        })

    @http.route(['/my/time_off/update_calendar'], type='http', auth="user", website=True, methods=['POST'])
    def update_employee_calendar(self, **post):
        """
        Handle the form submission for updating employee's resource calendar.
        """
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)

        if not employee:
            return request.redirect('/my/time_off')

        calendar_id = post.get('resource_calendar_id')
        if calendar_id:
            employee.sudo().write({
                'resource_calendar_id': int(calendar_id)
            })

        return request.redirect('/my/time_off')

    @http.route(['/my/apply_time_off'], type='http', auth="user", website=True)
    def portal_apply_time_off(self, **kwargs):
        """
        Render the 'Apply Time Off' page where the user can submit their leave application.
        """
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        time_off_types = self._get_time_off_types(employee)

        return request.render('portal_time_off.portal_apply_time_off_form', {
            'time_off_types': time_off_types,
            'csrf_token': request.csrf_token(),
        })

    @http.route(['/my/apply_time_off/submit'], type='http', auth="user", website=True, methods=['POST'])
    def portal_submit_time_off(self, **post):
        """
        Handle the form submission for time off application with better error handling.
        """
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)

        if not employee:
            return request.redirect('/my/home')

        try:
            # Parse dates more carefully
            date_from_str = post.get('date_from')
            date_to_str = post.get('date_to')
            
            if not date_from_str or not date_to_str:
                raise UserError("Date di inizio e fine sono obbligatorie")
            
            # Parse the datetime strings
            date_from_dt = datetime.strptime(date_from_str, '%Y-%m-%dT%H:%M')
            date_to_dt = datetime.strptime(date_to_str, '%Y-%m-%dT%H:%M')
            
            # Convert to proper format for Odoo
            date_from = fields.Datetime.to_string(date_from_dt)
            date_to = fields.Datetime.to_string(date_to_dt)
            
            # Validate dates
            if date_from_dt >= date_to_dt:
                raise UserError("La data di fine deve essere successiva alla data di inizio")
            
            # Aggiungere una variabile per recuperare l'ID del tipo di ferie dai dati del form  
            time_off_type_id = int(post.get('time_off_type'))
            
            # Recuperare l'oggetto completo del tipo di ferie usando l'ID
            leave_type = request.env['hr.leave.type'].sudo().browse(time_off_type_id)
            
            # Creare una variabile booleana che controlla se il tipo di ferie ha request_unit uguale a 'hour'
            is_hourly_request = leave_type.request_unit == 'hour'
            
            # Check for overlapping leaves (solo per ferie non orarie)
            if not is_hourly_request:
                overlapping_leaves = request.env['hr.leave'].sudo().search([
                    ('employee_id', '=', employee.id),
                    ('state', 'not in', ['cancel', 'refuse']),
                    '|',
                    '&', ('date_from', '<=', date_from), ('date_to', '>=', date_from),
                    '&', ('date_from', '<=', date_to), ('date_to', '>=', date_to),
                    '|',
                    '&', ('date_from', '>=', date_from), ('date_to', '<=', date_to),
                    '&', ('date_from', '<=', date_from), ('date_to', '>=', date_to),
                ])
                
                if overlapping_leaves:
                    # Create error message with details
                    overlapping_details = []
                    for leave in overlapping_leaves:
                        overlapping_details.append(
                            f"dal {leave.date_from.strftime('%d/%m/%Y')} al {leave.date_to.strftime('%d/%m/%Y')} - {leave.holiday_status_id.name}"
                        )
                    error_msg = f"Hai già prenotato ferie che si sovrappongono con questo periodo:\n" + "\n".join(overlapping_details)
                    
                    return request.render('portal_time_off.portal_apply_time_off_form', {
                        'time_off_types': self._get_time_off_types(employee),
                        'csrf_token': request.csrf_token(),
                        'error_message': error_msg,
                        'form_data': post,  # Pass back form data to repopulate
                    })
            
            # Sostituire la creazione diretta del record con la preparazione di un dizionario di valori
            # Includere nel dizionario tutti i campi originali
            leave_vals = {
                'holiday_status_id': time_off_type_id,
                'employee_id': employee.id,
                'date_from': date_from,
                'date_to': date_to,
                'name': post.get('description') or 'Richiesta ferie dal portale',
                'request_date_from': date_from_dt.date(),
                'request_date_to': date_to_dt.date(),
            }
            
            # Aggiungere una condizione che controlla la variabile booleana
            # Se la condizione è vera, aggiungere al dizionario il campo request_unit_hours con valore True
            if is_hourly_request:
                # Calcolare le ore di inizio e fine come float (es: 14.5 per 14:30)
                request_hour_from = date_from_dt.hour + date_from_dt.minute / 60.0
                request_hour_to = date_to_dt.hour + date_to_dt.minute / 60.0
                
                leave_vals.update({
                    'request_unit_hours': True,
                    'request_hour_from': request_hour_from,
                    'request_hour_to': request_hour_to,
                })
            
            # Creare il record usando il dizionario preparato con contesto appropriato
            context = dict(request.env.context)
            
            # Gestire il contesto in base al tipo di validazione e al tipo di richiesta
            if leave_type.leave_validation_type == 'no_validation':
                # Auto-approvazione: non usare leave_fast_create per permettere l'auto-approvazione
                if is_hourly_request:
                    context.update({'skip_validation': True})
            else:
                # Approvazione richiesta: usa leave_fast_create solo per ferie orarie problematiche
                if is_hourly_request:
                    context.update({
                        'skip_validation': True,
                        'leave_fast_create': True,
                    })
            
            leave = request.env['hr.leave'].with_context(context).sudo().create(leave_vals)
            
            # Redirect con messaggio di successo usando URL encoding
            return request.redirect('/my/time_off?success=1&leave_type=%s&date_from=%s&date_to=%s' % (
                urllib.parse.quote(leave.holiday_status_id.name),
                urllib.parse.quote(leave.date_from.strftime('%d/%m/%Y %H:%M') if is_hourly_request else leave.date_from.strftime('%d/%m/%Y')),
                urllib.parse.quote(leave.date_to.strftime('%d/%m/%Y %H:%M') if is_hourly_request else leave.date_to.strftime('%d/%m/%Y'))
            ))
            
        except ValidationError as e:
            return request.render('portal_time_off.portal_apply_time_off_form', {
                'time_off_types': self._get_time_off_types(employee),
                'csrf_token': request.csrf_token(),
                'error_message': str(e),
                'form_data': post,
            })
        except Exception as e:
            return request.render('portal_time_off.portal_apply_time_off_form', {
                'time_off_types': self._get_time_off_types(employee),
                'csrf_token': request.csrf_token(),
                'error_message': f"Errore durante la creazione della richiesta: {str(e)}",
                'form_data': post,
            })

    def _get_time_off_types(self, employee):
        """Helper method to get time off types for an employee"""
        time_off_types = []
        if employee:
            leave_types = request.env['hr.leave.type'].sudo().search([
                '|',
                ('requires_allocation', '=', 'no'),
                '&',
                ('has_valid_allocation', '=', True),
                '|',
                ('allows_negative', '=', True),
                '&',
                ('virtual_remaining_leaves', '>', 0),
                ('allows_negative', '=', False),
            ])

            for leave_type in leave_types:
                remaining_leaves = leave_type.virtual_remaining_leaves
                max_allocation = leave_type.max_leaves
                label = f"{leave_type.name} ({remaining_leaves} remaining out of {max_allocation if max_allocation else 'Unlimited'} days)"

                time_off_types.append({
                    'id': leave_type.id,
                    'label': label,
                })
        return time_off_types

    @http.route(['/my/allocations'], type='http', auth="user", website=True)
    def portal_my_allocations(self, **kwargs):
        """
        Render the allocations page.
        """
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        time_off_types = self._get_time_off_types(employee)
        
        # Convert for allocations view
        allocations = []
        for time_off_type in time_off_types:
            leave_type = request.env['hr.leave.type'].sudo().browse(time_off_type['id'])
            allocations.append({
                'id': leave_type.id,
                'leave_name': leave_type.name,
                'remain_leave': leave_type.virtual_remaining_leaves,
                'total_leave': leave_type.max_leaves,
            })
            
        return request.render('portal_time_off.portal_my_allocations', {
            'employee': employee,
            'allocations': allocations,
        })

    # =========================================================================
    # ROUTES PER GESTIONE CALENDARI PERSONALI
    # =========================================================================

    @http.route(['/my/time_off/calendars'], type='http', auth="user", website=True)
    def portal_time_off_calendars(self, **kwargs):
        """
        Ritorna la lista dei calendari personali dell'utente.
        I calendari sono filtrati per mostrare solo quelli creati dal dipendente corrente.
        """
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)

        if not employee:
            return request.render('portal_time_off.portal_calendars_page', {
                'employee': None,
                'calendars': [],
                'error_message': 'Non sei registrato come dipendente nel sistema.',
            })

        # Recupera i calendari personali del dipendente
        calendars = request.env['resource.calendar'].sudo().search([
            ('employee_creator_id', '=', employee.id)
        ])

        return request.render('portal_time_off.portal_calendars_page', {
            'employee': employee,
            'calendars': calendars,
            'csrf_token': request.csrf_token(),
        })

    @http.route(['/my/time_off/calendar/create'], type='http', auth="user", website=True, methods=['GET', 'POST'])
    def portal_time_off_calendar_create(self, **post):
        """
        GET: Mostra il form per creare un nuovo calendario.
        POST: Crea un nuovo calendario e le relative attendances.
        """
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)

        if not employee:
            return request.redirect('/my/time_off/calendars')

        if request.httprequest.method == 'GET':
            return request.render('portal_time_off.portal_calendar_create_form', {
                'employee': employee,
                'csrf_token': request.csrf_token(),
            })

        # POST: Crea il calendario
        redirect_to = post.get('redirect_to', '/my/time_off/calendars')
        
        try:
            custom_name = post.get('custom_name', '').strip()
            if not custom_name:
                raise UserError("Il nome del calendario è obbligatorio.")

            # Recupera la configurazione degli slot orari dal form
            slot_config_json = post.get('slot_config_json', '[]')

            # Valida il JSON
            try:
                slot_data = json.loads(slot_config_json)
                if not isinstance(slot_data, list):
                    raise ValueError("slot_config_json deve essere una lista")
            except (json.JSONDecodeError, ValueError) as e:
                raise UserError(f"Configurazione slot orari non valida: {e}")

            # Crea il calendario
            calendar_vals = {
                'custom_name': custom_name,
                'employee_creator_id': employee.id,
                'slot_config_json': slot_config_json,
            }

            calendar = request.env['resource.calendar'].sudo().create(calendar_vals)

            # Costruisci redirect URL in base a redirect_to
            if redirect_to == '/my/time_off':
                return request.redirect('/my/time_off?calendar_success=1&calendar_name=%s' % (
                    urllib.parse.quote(calendar.name),
                ))
            else:
                return request.redirect('/my/time_off/calendars?success=1&calendar_name=%s' % (
                    urllib.parse.quote(calendar.name),
                ))

        except (UserError, ValidationError) as e:
            error_msg = str(e)
            if redirect_to == '/my/time_off':
                return request.redirect('/my/time_off?calendar_error=%s' % urllib.parse.quote(error_msg))
            return request.render('portal_time_off.portal_calendar_create_form', {
                'employee': employee,
                'csrf_token': request.csrf_token(),
                'error_message': error_msg,
                'form_data': post,
            })
        except Exception as e:
            error_msg = f"Errore durante la creazione del calendario: {e}"
            if redirect_to == '/my/time_off':
                return request.redirect('/my/time_off?calendar_error=%s' % urllib.parse.quote(error_msg))
            return request.render('portal_time_off.portal_calendar_create_form', {
                'employee': employee,
                'csrf_token': request.csrf_token(),
                'error_message': error_msg,
                'form_data': post,
            })

    @http.route(['/my/time_off/calendar/<int:calendar_id>'], type='http', auth="user", website=True)
    def portal_time_off_calendar_detail(self, calendar_id, **kwargs):
        """
        Ritorna i dettagli di un calendario specifico.
        Verifica che il calendario appartenga al dipendente corrente.
        """
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)

        if not employee:
            return request.redirect('/my/time_off/calendars')

        # Recupera il calendario verificando che appartenga al dipendente
        calendar = request.env['resource.calendar'].sudo().search([
            ('id', '=', calendar_id),
            ('employee_creator_id', '=', employee.id)
        ], limit=1)

        if not calendar:
            return request.render('portal_time_off.portal_calendar_detail_page', {
                'employee': employee,
                'calendar': None,
                'attendances': [],
                'error_message': 'Calendario non trovato o non autorizzato.',
            })

        # Recupera le attendances del calendario
        attendances = request.env['resource.calendar.attendance'].sudo().search([
            ('calendar_id', '=', calendar.id)
        ], order='dayofweek, hour_from')

        return request.render('portal_time_off.portal_calendar_detail_page', {
            'employee': employee,
            'calendar': calendar,
            'attendances': attendances,
        })

    @http.route(['/my/time_off/calendar/<int:calendar_id>/use'], type='http', auth="user", website=True, methods=['POST'])
    def portal_time_off_calendar_use(self, calendar_id, **post):
        """
        Imposta un calendario come orario di lavoro del dipendente (azione "Usa Questo").
        Aggiorna il campo resource_calendar_id di hr.employee con l'ID del calendario.
        """
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        redirect_to = post.get('redirect_to', '/my/time_off/calendars')

        if not employee:
            return request.redirect(redirect_to)

        # Recupera il calendario verificando che appartenga al dipendente
        calendar = request.env['resource.calendar'].sudo().search([
            ('id', '=', calendar_id),
            ('employee_creator_id', '=', employee.id)
        ], limit=1)

        if not calendar:
            return request.redirect(redirect_to)

        # Aggiorna resource_calendar_id del dipendente
        employee.sudo().write({
            'resource_calendar_id': calendar.id
        })

        # Costruisci redirect URL in base a redirect_to
        if redirect_to == '/my/time_off':
            return request.redirect('/my/time_off?calendar_success=2&calendar_name=%s' % (
                urllib.parse.quote(calendar.name),
            ))
        else:
            return request.redirect('/my/time_off/calendars?success=2&calendar_name=%s' % (
                urllib.parse.quote(calendar.name),
            ))

    @http.route(['/my/time_off/calendar/<int:calendar_id>/stats'], type='http', auth="user", website=True, methods=['GET'])
    def portal_time_off_calendar_stats(self, calendar_id, **kwargs):
        """
        API endpoint per ottenere le statistiche orarie di un calendario.
        Ritorna i campi calcolati: total_weekly_hours, days_worked, hours_per_day.
        
        Returns:
            Response: JSON con le statistiche del calendario o errore se non trovato/non autorizzato
        """
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)

        if not employee:
            return request.make_json_response({'error': 'Dipendente non trovato.'}, status=404)

        # Recupera il calendario verificando che appartenga al dipendente
        calendar = request.env['resource.calendar'].sudo().search([
            ('id', '=', calendar_id),
            ('employee_creator_id', '=', employee.id)
        ], limit=1)

        if not calendar:
            return request.make_json_response({'error': 'Calendario non trovato o non autorizzato.'}, status=404)

        return request.make_json_response({
            'id': calendar.id,
            'name': calendar.name,
            'custom_name': calendar.custom_name,
            'total_weekly_hours': calendar.total_weekly_hours,
            'days_worked': calendar.days_worked,
            'hours_per_day': calendar.hours_per_day,
        })