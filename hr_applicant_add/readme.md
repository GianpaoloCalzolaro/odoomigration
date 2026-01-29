# HR Applicant Extension

## Overview
This module extends the standard HR Applicant functionality in Odoo 18 by adding detailed personal and professional fields for better candidate profiling and assessment. It is designed to capture comprehensive information about professional applicants, especially those in specialized fields like psychology, therapy, counseling, etc.

## Features
- Personal biographical information (fiscal code, birth date/place, nationality)
- Identification document details (type, number, expiry date)
- Additional professional information fields (ID, certification numbers, types)
- Professional experience tracking (years, specialization, orientation)
- Education and qualification details
- Administrative information (registration, insurance)
- Availability tracking
- Skills assessment (languages, digital proficiency, remote work experience)

## Installation
1. Copy this module to your Odoo addons directory.
2. Update the module list in your Odoo instance.
3. Install the module through the Odoo interface.

## Dependencies
- hr_recruitment: The standard Odoo recruitment module

## Usage
After installation, the additional fields will be available in the HR Applicant form view, organized in the following tabs:
- **Personal Information**: Personal details and identification document information
- **Professional Information**: Basic professional details and insurance information
- **Experience**: Professional experience, specialization, theoretical orientation, and education details
- **Availability**: Working schedule, availability, and skills information

## Configuration
No additional configuration is needed. The module works out of the box once installed.

## Contributing
Contributions to the improvement of this module are welcome. Please follow Odoo's coding standards when contributing.

## License
This module is licensed under LGPL-3.

## Changelog

- 2025-03-27:
  - Added contract start and end date fields
  - Added new contract information tab in the form view
  - Updated translations for new contract fields

- 2023-10-17: 
  - Initial release with professional fields for applicants
  - Added Italian translation support
  - Organized fields into logical groups with tabs
  - Added conditional visibility for insurance fields
- 2023-10-18:
  - Added personal information fields and dedicated tab
  - Added identification document fields
  - Updated translations for new fields

## Author
Odoo Developer

## Support
For support, please contact via the GitHub repository issues or visit [www.example.com](https://www.example.com).
