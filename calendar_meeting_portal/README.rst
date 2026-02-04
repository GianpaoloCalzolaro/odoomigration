======================================
Portal for Calendar Meetings for Attendees
======================================

Calendar Meeting Show to Attendees Portal Users / Portal for Calendar Meetings for Attendees

This app allows your attendees to view meetings on my account portal
of your website and send a message using portal login.

Portal for Calendar Meetings for Attendees
Calendar Meeting Show to Attendees Portal Users

Allow your portal users attendees to view all the calendar meetings where they are set as attendees.
They can also send a message from the list and form a view of the portal as shown.

Features
========

* Portal users can view calendar meetings where they are attendees
* Send messages from list and form views in the portal
* Employees can create appointments from the portal
* Invite customers to appointments
* Automatic Odoo videocall link generation
* Automatic notifications to participants
* Client-side and server-side form validation
* Meeting outcome management with predefined types

Version History
===============

v18.0.2.0.0
-----------
* Added functionality for employees to create appointments from the portal
* Only employee portal users can create appointments
* Ability to invite customers to appointments
* Automatic Odoo videocall link generation
* Automatic notifications to participants
* Client-side and server-side form validation
* JavaScript updated for Odoo 18 (jQuery removal)

v18.0.3.1.0
-----------
* Added functionality for employees to modify appointment status from the portal
* Display appointment_status field in detail page (employees only)
* Form to update status with dropdown (To Define, Confirmed, Cancelled)
* Security controls to verify only participating employees can modify status
* Success and error messages for user feedback

v18.0.4.0.0
-----------
* calendar.event.outcome model: appointment outcome types
  - Fields: name (translate), code (unique), description (translate), color, sequence, active
  - SQL constraint: code_unique
  - Python validation: code format (lowercase alphanumeric with _ and -)
  - Custom name_get: shows [code] name
* Extended calendar.event with esito_evento_id field (Many2one, tracking=True)
* Complete backend views:
  - Tree view with list attribute, editable="top", handle widget, decoration-muted
  - Form view: sheet layout, groups, color_picker, readonly="id" on code, boolean_toggle
  - Search view: full-text search, filters (Active default, Archived), grouping
  - Menu: Calendar > Configuration > Event Outcome Types
* Initial data (noupdate="1"): 7 predefined types in Italian
  - completed, partial, no_show, cancelled_pro, cancelled_patient, reschedule, pending_docs
* Integration in calendar.event form: outcome field after appointment_status with domain, options, placeholder

Credits
=======

Author
------

* Probuse Consulting Service Pvt. Ltd.

Contributors
------------

* Probuse Consulting Service Pvt. Ltd.

Maintainer
----------

This module is maintained by Probuse Consulting Service Pvt. Ltd.
