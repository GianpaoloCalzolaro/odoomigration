# -*- coding: utf-8 -*-
{
    'name': 'Customer Diario Portal',  # Aggiornato da 'customer notes portal' a 'Customer Diario Portal'
    'summary': 'I clienti possono creare il proprio diario personale nel portale',  # Aggiornato riassunto
    'description': '''
Questo modulo introduce la possibilità di creare e gestire facilmente un diario personale all'interno del portale clienti per una migliore organizzazione e tracciamento delle emozioni.

Caratteristiche principali:
- Creazione e aggiunta semplice di voci di diario direttamente nel portale clienti.
- Eliminazione conveniente delle voci quando non più necessarie per mantenere uno spazio organizzato e pulito.
- Annotazione di promemoria importanti come scadenze fatture, traguardi progetti e altri dettagli rilevanti.
- Accesso rapido alle tue voci di diario all'interno del portale per tenere traccia delle informazioni essenziali in un unico posto.
- Campo "Come sto" per tracciare il proprio stato d'animo quotidiano.
- Editor HTML per contenuti ricchi e formattati.
- Visualizzazione della data di creazione per ogni voce.

    ''',

    'author': "Elite ERP",
    'website': "eliteweb44@gmail.com",

    'category': 'portal customer website',

    'version': '1.6.0',  # Incrementata versione per il raggruppamento note

    'license': 'OPL-1',
    'depends': ['portal', 'website', 'contacts_patient'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/portal_note_backend_views.xml',
        'views/res_partner_note_button.xml',
    ],
    'installable': True,
    'images': [
        'static/description/main_screenshot.gif',
    ],
}
