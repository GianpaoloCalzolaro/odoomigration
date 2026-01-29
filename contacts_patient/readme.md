# Contacts Patient Module

## Overview
The Contacts Patient module extends the standard Odoo Contacts module to add medical patient information to partners. This module allows businesses in the healthcare sector to track patients and their medical records directly in Odoo.

## Features
- Mark contacts as patients with a simple checkbox
- Record comprehensive medical information on a dedicated "Medical Record" tab
- Manage the treatment team on an "Équipe" tab
- All fields are only visible when the contact is marked as a patient

## Medical Record Fields
- Reason for consultation
- Problem description
- Symptoms onset and duration
- Previous treatments
- Current issues
- Family, social, and work context
- Primary and secondary diagnosis
- Diagnosis code and criteria
- Differential diagnosis and comorbidity
- Risk assessment
- Treatment goals
- Referrals to other specialists

## Team Fields
- Tutor
- Psychologist
- Coach
- Psychotherapist

## Dependencies
- Contacts module (`contacts`)
- Human Resources module (`hr`)

## Installation
1. Download the module and place it in your addons folder
2. Update the app list in Odoo
3. Install the "Contacts Patient" module
4. The new patient fields will be available on contacts

## Usage
1. Go to Contacts
2. Create a new contact or edit an existing one
3. Mark the contact as a patient using the checkbox at the top of the form
4. Fill in the medical information in the "Cartella clinica" tab
5. Assign team members in the "Équipe" tab

## Security
This module inherits the access rights from the contacts module. Users who can modify contacts will also be able to modify patient information.

## Technical Information
This module extends the `res.partner` model and inherits from the standard contact form view. The patient fields are only displayed when the `is_patient` flag is set.

## Changelog
### v1.0.0 (2025-03-15)
- Initial release
- Added patient flag field
- Added medical record tab with clinical information fields
- Added team tab with employee relationship fields
