gli utenti disponibili, il modulo permette di definire criteri dinamici utilizzando
i domini Odoo.
# Appointment Dynamic Staff Selection

[![Maturity](https://img.shields.io/badge/maturity-Beta-yellow.png)](https://odoo-community.org/page/development-status)
[![License: LGPL-3](https://img.shields.io/badge/licence-LGPL--3-blue.png)](https://www.gnu.org/licenses/lgpl-3.0-standalone.html)
[![GitHub](https://img.shields.io/badge/github-GianpaoloCalzolaro%2Fsviluppodoo-lightgray.png?logo=github)](https://github.com/GianpaoloCalzolaro/sviluppodoo/tree/main/appointment_dynamic_staff)

This module extends Odoo **Appointments** to support **dynamic staff selection** using standard Odoo domains.

## Contents

- [Description](#description)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Known issues / Roadmap](#known-issues--roadmap)
- [Bug Tracker](#bug-tracker)
- [Credits](#credits)
- [License](#license)

## Description

Normally, appointment staff is configured by manually selecting users/resources.
With this addon you can instead define a **domain** (Odoo domain syntax) that is evaluated to compute the available staff dynamically.

Main goals:

- Reduce manual maintenance when staff changes frequently.
- Allow flexible selection rules (department, skills, tags, custom fields, etc.).
- Keep configuration consistent across multiple appointment types.

## Installation

1. Add `appointment_dynamic_staff` to your Odoo addons path.
2. Update the Apps list.
3. Install **Appointment Dynamic Staff Selection**.

This addon is meant to be used together with Odoo's Appointments module.

## Configuration

1. Go to **Services → Configuration → Appointment Types**.
2. Open (or create) an appointment type.
3. Set the staff selection rule introduced by this addon (an Odoo domain).
4. Save.

Notes:

- Domains follow the standard Odoo syntax, for example: `[("department_id", "=", 3)]`.
- The domain should target the model used by the appointment staff selection in your database (typically users/employees/resources depending on your setup).

## Usage

Once configured, the available staff shown/used for an appointment type is computed dynamically from the configured domain.
This means you can update staff eligibility by changing data (department, tags, fields, etc.) without manually editing the appointment type each time.

## Known issues / Roadmap

- No known issues at the moment.

If you find a bug or want to propose improvements, please open an issue (see below).

## Bug Tracker

Bugs are tracked on GitHub Issues:

- https://github.com/GianpaoloCalzolaro/sviluppodoo/issues

Before reporting a problem, please check if it has already been reported.
If you are the first one to report it, please provide a clear reproduction path and relevant logs.

Do not contact contributors directly for support.

## Credits

### Authors

- Gianpaolo Calzolaro

### Contributors

- Gianpaolo Calzolaro (gianpaolo@infologis.biz)

### Maintainers

This module is maintained by Gianpaolo Calzolaro.

Project repository:

- https://github.com/GianpaoloCalzolaro/sviluppodoo

More information:

- https://www.infologis.biz

## License

This addon is licensed under the LGPL-3.0 license.
