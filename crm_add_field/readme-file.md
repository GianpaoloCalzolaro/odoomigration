# CRM Extended Classification

## Overview
This module extends the Odoo CRM functionalities by adding specific fields for business classification. It allows categorizing sales opportunities based on company type, size, geographical region, business sector, and information about the company structure (annual volume and employee count).

## Features
- Adds business classification fields to CRM leads/opportunities
- Creates a new model for managing business sectors
- Provides new search and grouping options in CRM views
- Includes Italian localization

## Dependencies
- CRM module
- Base module

## Installation
1. Copy the module folder to your Odoo addons directory
2. Update the module list in Odoo
3. Install the "CRM Extended Classification" module

## Configuration
After installation:
1. Go to CRM > Configuration > Business Sectors to manage the available business sectors
2. CRM leads/opportunities will have a new "Business Information" page in their form view with the new fields

## Usage
When creating or editing a lead/opportunity:
1. Navigate to the "Business Information" page
2. Fill in the company classification information
3. Use the new fields for filtering and grouping in list views

## Technical Information
The module adds the following fields to the CRM lead model:
- Company Type (Selection)
- Company Size (Selection)
- Region (Selection)
- Business Sector (Many2one)
- Annual Volume (Float)
- Employee Count (Selection)

## Changelog
### [1.0.0] - 2025-04-03
- Initial release with business classification fields
- Added business sectors management
- Included Italian translation

## Author
Gian Paolo Calzolaro

## Website
www.infologis.biz
