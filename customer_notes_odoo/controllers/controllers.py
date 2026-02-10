from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
import logging

_logger = logging.getLogger(__name__)

class PortalNotes(http.Controller):

    @http.route('/my/notes', type='http', auth="user", website=True)
    def portal_notes(self, **kw):
        """Visualizza l'elenco delle voci di diario"""
        group_param = request.params.get('group_by_user')
        group_by_user = str(group_param) in ('1', 'True', 'true')

        Note = request.env['portal.note'].sudo()
        employee = request.env.user.employee_id
        if employee:
            domain = [
                ('user_id.partner_id.is_patient', '=', True),
                '|',
                ('user_id.partner_id.tutor', '=', employee.id),
                ('user_id.partner_id.professional', '=', employee.id),
            ]
            notes = Note.search(domain, order='create_date desc')
        else:
            notes = Note.search([('user_id', '=', request.env.user.id)], order='create_date desc')

        notes.mapped('user_id.partner_id')

        notes_grouped = {}
        if group_by_user:
            for note in notes:
                notes_grouped.setdefault(note.user_id, request.env['portal.note'])
                notes_grouped[note.user_id] |= note

        values = {
            'notes': notes,
            'show_new_button': not employee,
            'group_by_user': group_by_user,
            'notes_grouped': notes_grouped,
        }
        return request.render('customer_notes_odoo.portal_notes_page', values)

    @http.route('/my/notes/create', type='http', auth="user", website=True)
    def create_note(self, **kw):
        """Mostra la pagina per creare una nuova voce di diario"""
        return request.render('customer_notes_odoo.portal_create_note', {})

    @http.route('/my/notes/save', type='http', auth="user", methods=['POST'], website=True)
    def save_note(self, **post):
        """Salva una nuova voce di diario con gestione del campo 'Come sto'"""
        # Prepara i dati per la creazione della voce
        note_data = {
            'title': post.get('title'),
            'content': post.get('content'),
            'user_id': request.env.user.id
        }
        
        # Aggiunge il campo 'Come sto' se presente
        how_i_feel = post.get('how_i_feel')
        if how_i_feel:
            note_data['how_i_feel'] = how_i_feel
        
        # Crea la nuova voce di diario
        request.env['portal.note'].sudo().create(note_data)
        
        return request.redirect('/my/notes')

    @http.route('/my/notes/<int:note_id>', type='http', auth="user", website=True)
    def portal_note_detail(self, note_id, **kw):
        """Visualizza i dettagli di una specifica voce di diario"""
        note = request.env['portal.note'].sudo().browse(note_id)
        employee = request.env.user.employee_id
        allowed = False
        if note.exists():
            if employee:
                allowed = (
                    note.user_id.partner_id.is_patient and (
                        note.user_id.partner_id.tutor.id == employee.id or
                        note.user_id.partner_id.professional.id == employee.id
                    )
                )
            else:
                allowed = note.user_id.id == request.env.user.id

        if allowed:
            return request.render('customer_notes_odoo.portal_note_detail', {'note': note})

        return request.redirect('/my/notes')

    @http.route('/my/notes/delete', type='http', auth="user", methods=['POST'], website=True)
    def delete_note(self, **post):
        """Elimina una voce di diario dell'utente corrente"""
        try:
            note_id = int(post.get('note_id'))
            note = request.env['portal.note'].sudo().browse(note_id)
            employee = request.env.user.employee_id
            allowed = False
            if note.exists():
                if employee:
                    allowed = (
                        note.user_id.partner_id.is_patient and (
                            note.user_id.partner_id.tutor.id == employee.id or
                            note.user_id.partner_id.professional.id == employee.id
                        )
                    )
                else:
                    allowed = note.user_id.id == request.env.user.id
            if allowed:
                note.unlink()
        except (ValueError, TypeError):
            _logger.warning("Invalid note_id parameter in delete request")

        return request.redirect('/my/notes')


# Estende il controller portal per aggiungere il conteggio voci diario
class CustomerPortalDiario(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        employee = request.env.user.employee_id
        
        values['show_diario_card'] = bool(employee) or request.env.user.partner_id.is_patient
        return values
