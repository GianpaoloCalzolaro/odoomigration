# -*- coding: utf-8 -*-
{
    'name': 'appointment_no_duplicates',
    'version': '1.0.0',
    'category': 'Website/Appointment',
    'summary': 'Previene la creazione di contatti duplicati negli appuntamenti',
    'description': """
        Questo modulo estende il sistema di gestione appuntamenti di Odoo per prevenire
        la creazione di contatti duplicati quando gli utenti pubblici prenotano appuntamenti.
        
        Il modulo implementa una ricerca intelligente che controlla prima per email normalizzata,
        poi per telefono formattato, e solo in caso di mancata corrispondenza crea un nuovo contatto.
        
        Caratteristiche:
        - Ricerca contatti esistenti per email normalizzata
        - Ricerca contatti esistenti per telefono formattato  
        - Aggiornamento intelligente dei campi vuoti nei contatti esistenti
        - Mantenimento dell'integrità dei dati esistenti
        - Compatibilità completa con il flusso originale degli appuntamenti
    """,
    'author': 'Gian Paolo Calzolaro',
    'website': 'www.infologis.biz',
    'depends': ['base', 'appointment'],
    'data': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
