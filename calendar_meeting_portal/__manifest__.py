# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Portal for Calendar Meetings for Attendees",
    'version': '18.0.4.0.0',  # MODIFICATO: Aggiornato per FASE 1 - gestione esiti eventi
    'license': 'Other proprietary',
    'price': 39.0,
    'currency': 'EUR',
    'summary':  """Calendar Meeting Show to Attendees Portal Users / Portal for Calendar Meetings for Attendees""",
    'description': """
Calendar Meeting Show to Attendees Portal Users / Portal for Calendar Meetings for Attendees
This app allows your attendees to view meetings on my account portal
of your website and send a message using portal login. 
Portal for Calendar Meetings for Attendees
Calendar Meeting Show to Attendees Portal Users
Allow your portal users attendees to view all the calendar meetings where they are set as attendees.
They can also send a message from the list and form a view of the portal as shown.
Portal for Calendar Meetings for Attendees

AGGIORNAMENTO v18.0.2.0.0:
- Aggiunta funzionalità per dipendenti di creare appuntamenti dal portale
- Solo utenti portali dipendenti possono creare appuntamenti
- Possibilità di invitare clienti agli appuntamenti
- Link videochiamata Odoo generato automaticamente
- Notifiche automatiche ai partecipanti
- Validazione form client-side e server-side
- JavaScript aggiornato per Odoo 18 (rimozione jQuery)

AGGIORNAMENTO v18.0.3.1.0:
- Aggiunta funzionalità per dipendenti di modificare lo stato dell'appuntamento dal portale
- Visualizzazione campo appointment_status nella pagina di dettaglio (solo per dipendenti)
- Form per aggiornare lo stato con dropdown (Da Definire, Confermato, Cancellato)
- Controlli di sicurezza per verificare che solo dipendenti partecipanti possano modificare lo stato
- Messaggi di successo ed errore per feedback all'utente

AGGIORNAMENTO v18.0.4.0.0 - FASE 2:
- Modello calendar.event.outcome: tipologie esito appuntamenti
  * Campi: name (translate), code (univoco), description (translate), color, sequence, active
  * Constraint SQL: code_unique
  * Validazione Python: formato code (lowercase alphanumeric con _ e -)
  * name_get personalizzato: mostra [code] name
- Esteso calendar.event con campo esito_evento_id (Many2one, tracking=True)
- Viste backend complete:
  * Tree view con <list> attribute, editable="top", handle widget, decoration-muted
  * Form view: sheet layout, gruppi, color_picker, readonly="id" su code, boolean_toggle
  * Search view: full-text search, filtri (Attivi default, Archiviati), grouping
  * Menu: Calendario > Configurazione > Tipologie Esito Evento
- Dati iniziali (noupdate="1"): 7 tipologie predefinite in italiano
  * completed, partial, no_show, cancelled_pro, cancelled_patient, reschedule, pending_docs
- Integrazione form calendar.event: campo esito dopo appointment_status con domain, options, placeholder
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/image.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/calendar_meeting_portal/1018',#'https://youtu.be/kuh2AWBuT8U',
    'category': 'Productivity/Calendar',
    'depends': [
        'calendar',
        'portal',
        'hr',
        'website'  # AGGIUNTA: Dipendenza HR per verificare se l'utente è dipendente
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/calendar_event_security.xml',  # FASE 3: Record rules per sicurezza granulare
        'data/calendar_event_outcome_data.xml',  # FASE 2: Dati iniziali tipologie esito predefinite
        'views/calendar_event_outcome_views.xml',  # FASE 2: Viste backend complete per modello esiti eventi
        'views/calendar_event_views.xml',  # FASE 2: Estensione calendar.event con campo esito
        'views/customer_calendar_template.xml',
        'views/calendar_portal_templates.xml',
        'views/portal_meeting_create.xml',  # AGGIUNTA: Nuovo template per creazione appuntamenti
    ],
    'assets': {
        'web.assets_frontend': [
            '/calendar_meeting_portal/static/src/js/calendar_comment.js',
            '/calendar_meeting_portal/static/src/js/meeting_create_validation.js',  # AGGIUNTA: Validazione form creazione
        ],
    },
    'installable': True,
    'application': False,
}


