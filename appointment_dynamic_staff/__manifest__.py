# -*- coding: utf-8 -*-

{
    'name': 'Appointment Dynamic Staff Selection',
    'summary': 'Selezione dinamica dello staff per appuntamenti tramite domini Odoo',
    'description': """
Appointment Dynamic Staff Selection
====================================

Questo modulo estende il modulo Appointment di Odoo per permettere la selezione
dinamica dello staff attraverso l'uso di domini Odoo.

Funzionalità Principali
------------------------
* Selezione dinamica del personale disponibile per gli appuntamenti
* Utilizzo di domini Odoo per filtrare lo staff in base a criteri specifici
* Integrazione completa con il modulo Appointment esistente
* Flessibilità nella configurazione dei criteri di selezione

Benefici
--------
* Maggiore flessibilità nella gestione del personale per gli appuntamenti
* Riduzione del lavoro manuale di selezione dello staff
* Possibilità di definire criteri complessi per la selezione automatica
* Miglioramento dell'efficienza operativa
    """,
    'author': 'Gianpaolo Calzolaro',
    'website': 'www.infologis.biz',
    'category': 'Services/Appointment',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'appointment',
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/appointment_type_views.xml',
    ],
}
