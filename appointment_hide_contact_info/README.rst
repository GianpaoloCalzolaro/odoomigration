============================
Appointment Hide Contact Info
============================

.. |badge1| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

|badge1|

Questo modulo nasconde le informazioni di contatto (email e telefono) dello staff user
dalla pagina di conferma appuntamento in Odoo 18.

**Indice**

.. contents::
   :local:

Funzionalità
============

* Nasconde email dello staff user nella card di validazione appuntamento
* Nasconde telefono dello staff user nella card di validazione appuntamento
* Mantiene visibili avatar, nome e funzione
* Approccio non distruttivo tramite template inheritance

Configurazione
==============

Non è richiesta alcuna configurazione. Il modulo funziona automaticamente
dopo l'installazione.

Utilizzo
========

1. Installare il modulo dall'interfaccia Apps di Odoo
2. Le informazioni di contatto (email e telefono) saranno automaticamente
   nascoste dalla pagina di conferma appuntamento
3. Avatar, nome e funzione dello staff user rimangono visibili

Implementazione Tecnica
=======================

Il modulo eredita il template ``appointment.appointment_validated_card``
e utilizza XPath per targetizzare i div contenenti email e telefono,
aggiungendo l'attributo ``t-if="False"`` per nasconderli dalla visualizzazione.

Bug Tracker
===========

In caso di problemi, contattare l'autore.

Credits
=======

Autori
------

* Gian Paolo Calzolaro

Contributori
------------

* Gian Paolo Calzolaro <info@infologis.biz>

Maintainer
----------

Questo modulo è mantenuto da Gian Paolo Calzolaro.
