# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Appointment Hide Contact Info',
    'version': '18.0.1.0.0',
    'category': 'Appointments',
    'summary': 'Nasconde email e telefono dello staff nella pagina di conferma appuntamento',
    'description': """
        Modulo per nascondere le informazioni di contatto dalla pagina di conferma appuntamento.
        
        Funzionalità:
        - Nasconde email dello staff user nella card di validazione appuntamento
        - Nasconde telefono dello staff user nella card di validazione appuntamento
        - Mantiene visibili avatar, nome e funzione
        - Approccio non distruttivo tramite template inheritance
        
        Questo modulo eredita il template appointment_validated_card e aggiunge
        attributi t-if="False" ai div contenenti email e telefono per nasconderli
        dalla visualizzazione, mantenendo il resto della card intatto.
    """,
    'author': 'Gian Paolo Calzolaro',
    'website': 'www.infologis.biz',
    'license': 'AGPL-3',
    'depends': ['appointment'],
    'data': [
        'views/appointment_templates_validation.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
