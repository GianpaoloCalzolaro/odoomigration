# [MIG] portal_time_off: Migration from Odoo 18.0 to 19.0

## SUMMARY

**Module:** `portal_time_off`
**Migration Complexity:** 🟡 **MEDIUM**
**Estimated Effort:** 2-3 days

Il modulo `portal_time_off` permette ai dipendenti di gestire le richieste di ferie tramite il portale Odoo. Il modulo include:
- Controller HTTP per gestione time off e calendari personali
- Estensione model `hr.employee` per creazione utenti portal
- Template QWeb per interfaccia portal
- Widget JavaScript per gestione slot orari calendari

### Principali aree di intervento:
1. **Manifest**: Aggiornamento versione e conformità OCA
2. **Traduzioni**: Migrazione da `_()` a `self.env._()` (Odoo 19 best practice)
3. **Security**: Completamento ACL mancanti e validazione Record Rules
4. **JavaScript**: Verifica compatibilità import OWL/legacy widget
5. **Code Quality**: Rimozione print statements, gestione context

---

## PREREQUISITES

### Dipendenze da verificare/aggiornare per Odoo 19:

| Dipendenza | Stato | Note |
|------------|-------|------|
| `hr` | ✅ Core | Verificare eventuali cambiamenti API employee |
| `portal` | ✅ Core | Nessun breaking change noto |
| `website` | ✅ Core | Nessun breaking change noto |
| `hr_holidays` | ⚠️ Core | **ATTENZIONE**: Verificare cambiamenti `hr.leave` e `hr.leave.type` |
| `l4l_timesheet_portal` | ❓ Custom | **CRITICO**: Dipendenza custom - deve essere migrata PRIMA |

### Librerie Python:
- Nessuna libreria esterna aggiuntiva richiesta

### Tools consigliati:
- `openupgradelib` - Per eventuali script di migrazione dati
- `pylint-odoo` >= 10.0.0 - Per validazione codice

---

## CHANGES REQUIRED

### 1. MANIFEST (`__manifest__.py`)

| Linea | Modifica Richiesta | Azione |
|-------|-------------------|--------|
| 3 | `'version': '1.0'` → `'version': '19.0.1.0.0'` | Adeguare formato versione OCA |
| 5-12 | Chiave `description` deprecata | Rimuovere e spostare contenuto in `README.rst` |
| 17 | Dipendenza `l4l_timesheet_portal` | Verificare disponibilità per v19 o rimuovere se non necessaria |
| 19 | `# 'security/ir.model.access.csv'` commentato | Decommentare e completare ACL |
| 31-32 | `installable` e `application` superflui | Rimuovere (valori di default) |
| - | Chiave `support` mancante | Aggiungere (richiesta per moduli a pagamento) |
| - | Chiave `author` | Aggiungere `'Odoo Community Association (OCA)'` se contribuito a OCA |

**Esempio manifest corretto:**
```python
{
    'name': 'Employee Apply Leave (Time Off) as a Portal User',
    'version': '19.0.1.0.0',
    'summary': 'Manage and apply leaves via portal user',
    'author': 'Areterix Technologies',
    'support': 'support@areterix.com',
    'category': 'Human Resources',
    'depends': ['hr', 'portal', 'website', 'hr_holidays'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/employee_view.xml',
        'views/portal_time_off_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'portal_time_off/static/src/css/calendar_form.css',
            'portal_time_off/static/src/js/calendar_manager.js',
        ],
    },
    'license': 'LGPL-3',
    'images': ['static/description/banner.gif'],
}
```

---

### 2. MODELS

#### File: `models/employee_portal_user.py`

| Linea | Issue | Modifica Richiesta | Azione |
|-------|-------|-------------------|--------|
| 1 | Import non utilizzato | Rimuovere `fields` se non usato | Cleanup |
| 12-13 | Traduzione deprecata | `_("...")` → `self.env._("...")` | Odoo 19 best practice per traduzioni in metodi |
| 14-23 | Loop dopo `ensure_one()` | Rimuovere `for record in self:` ridondante | Cleanup |
| 16-21 | Creazione user senza company | Aggiungere `company_id` e `company_ids` | Multi-company safety |

**Codice corretto:**
```python
from odoo import models, api
from odoo.exceptions import UserError


class EmployeePortalUser(models.Model):
    _inherit = 'hr.employee'

    def action_create_portal_user(self):
        self.ensure_one()
        if not self.work_email and not self.private_email:
            raise UserError(
                self.env._("Please set either a work email or a private email address before creating a portal user."))

        if not self.user_id:
            user_vals = {
                'name': self.name,
                'login': self.work_email or self.private_email,
                'email': self.work_email or self.private_email,
                'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
                'company_id': self.company_id.id,
                'company_ids': [(6, 0, self.company_id.ids)],
            }
            user = self.env['res.users'].sudo().create(user_vals)
            self.user_id = user
```

---

### 3. CONTROLLERS

#### File: `controllers/portal_time_off.py`

| Linea | Issue | Modifica Richiesta | Priorità |
|-------|-------|-------------------|----------|
| 16, 18 | `print()` statements | Sostituire con `_logger.debug()` | 🔴 Alta |
| 90, 102, 313, 324 | Stringhe non tradotte in `UserError` | Usare `request.env._()` | 🟡 Media |
| 168-181 | Context override con `dict()` | Usare `with_context(**kwargs)` | 🟡 Media |
| 14-15, etc. | Uso eccessivo di `sudo()` | Valutare Record Rules appropriate | 🟡 Media |

**Modifiche dettagliate:**

```python
# Aggiungere all'inizio del file
import logging
_logger = logging.getLogger(__name__)

# Linea 16, 18 - Sostituire print
_logger.debug("time off is: %s", time_offs)
_logger.debug("leave_types is: %s", leave_types)

# Linea 90 - Traduzione
raise UserError(request.env._("Date di inizio e fine sono obbligatorie"))

# Linea 102 - Traduzione
raise UserError(request.env._("La data di fine deve essere successiva alla data di inizio"))

# Linea 168-183 - Context override corretto
leave = request.env['hr.leave'].with_context(
    skip_validation=True,
    leave_fast_create=is_hourly_request and leave_type.leave_validation_type != 'no_validation',
).sudo().create(leave_vals)
```

---

### 4. SECURITY

#### File: `security/ir.model.access.csv`

**Stato attuale:** File commentato nel manifest, contiene solo 1 ACL incompleta.

| Modello | Gruppo | Read | Write | Create | Unlink | Stato |
|---------|--------|------|-------|--------|--------|-------|
| `hr.employee` | `base.group_portal` | 1 | 0 | 0 | 0 | ❌ Mancante |
| `hr.leave` | `base.group_portal` | 1 | 0 | 1 | 0 | ❌ Mancante |
| `hr.leave.type` | `base.group_portal` | 1 | 0 | 0 | 0 | ❌ Mancante |
| `hr.leave.allocation` | `base.group_portal` | 1 | 0 | 0 | 0 | ❌ Mancante |
| `resource.calendar` | `base.group_portal` | 1 | 1 | 1 | 0 | ❌ Mancante |
| `resource.calendar.attendance` | `base.group_portal` | 1 | 0 | 0 | 0 | ❌ Mancante |

**Azione:** Creare file `ir.model.access.csv` completo:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_hr_employee_portal,hr.employee.portal,hr.model_hr_employee,base.group_portal,1,0,0,0
access_hr_leave_portal,hr.leave.portal,hr_holidays.model_hr_leave,base.group_portal,1,0,1,0
access_hr_leave_type_portal,hr.leave.type.portal,hr_holidays.model_hr_leave_type,base.group_portal,1,0,0,0
access_hr_leave_allocation_portal,hr.leave.allocation.portal,hr_holidays.model_hr_leave_allocation,base.group_portal,1,0,0,0
access_resource_calendar_portal,resource.calendar.portal,resource.model_resource_calendar,base.group_portal,1,1,1,0
access_resource_calendar_attendance_portal,resource.calendar.attendance.portal,resource.model_resource_calendar_attendance,base.group_portal,1,0,0,0
```

#### File: `security/security.xml`

**Issue:** ACL definite in XML invece che CSV (duplicazione con CSV).

**Azione:**
1. Spostare tutte le ACL in `ir.model.access.csv`
2. Mantenere in `security.xml` solo eventuali Record Rules

**Record Rules da aggiungere:**

```xml
<!-- Record Rule per hr.leave - Portal users vedono solo le proprie richieste -->
<record id="hr_leave_portal_rule" model="ir.rule">
    <field name="name">Portal: own leaves only</field>
    <field name="model_id" ref="hr_holidays.model_hr_leave"/>
    <field name="domain_force">[('employee_id.user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
</record>

<!-- Record Rule per resource.calendar - Portal users vedono solo i propri calendari -->
<record id="resource_calendar_portal_rule" model="ir.rule">
    <field name="name">Portal: own calendars only</field>
    <field name="model_id" ref="resource.model_resource_calendar"/>
    <field name="domain_force">['|', ('employee_creator_id', '=', False), ('employee_creator_id.user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
</record>
```

---

### 5. VIEWS (XML)

#### File: `views/employee_view.xml`

| Issue | Modifica Richiesta | Priorità |
|-------|-------------------|----------|
| xpath `//header` potenzialmente ambiguo | Verificare unicità in Odoo 19 | 🟢 Bassa |

**Stato:** ✅ Nessuna modifica critica richiesta. La sintassi è compatibile con Odoo 19.

#### File: `views/portal_time_off_templates.xml`

| Linea | Issue | Modifica Richiesta | Priorità |
|-------|-------|-------------------|----------|
| 5 | xpath lungo e fragile | Considerare xpath più specifico | 🟢 Bassa |
| 355 | Accesso diretto a `_fields['state'].selection` | Usare metodo helper | 🟡 Media |
| 442-461 | JavaScript inline nel template | Spostare in file JS separato | 🟡 Media |

**Modifica linea 355:**
```xml
<!-- Da: -->
<t t-esc="dict(time_off._fields['state'].selection).get(time_off.state, 'Unknown')"/>

<!-- A: (creare metodo helper nel model o usare selection_field) -->
<t t-esc="time_off._get_state_display()"/>
```

---

### 6. ASSETS E FRONTEND

#### File: `static/src/js/calendar_manager.js`

| Linea | Issue | Modifica Richiesta | Priorità |
|-------|-------|-------------------|----------|
| 15 | Import legacy widget | Verificare compatibilità Odoo 19 | 🔴 Alta |
| 24 | `publicWidget.Widget.extend` | Potrebbe richiedere migrazione a OWL Component | 🟡 Media |

**Analisi import:**
```javascript
// Attuale (legacy)
import publicWidget from "@web/legacy/js/public/public_widget";

// Odoo 19 - verificare se il path è ancora valido
// Il modulo legacy è ancora supportato ma potrebbe essere deprecato in futuro
```

**Azione consigliata:**
1. Testare il modulo JS in ambiente Odoo 19
2. Se funziona, mantenere con commento deprecation warning
3. Se non funziona, migrare a OWL Component pattern

**Esempio migrazione OWL (se necessario):**
```javascript
/** @odoo-module **/
import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class CalendarManager extends Component {
    static template = "portal_time_off.CalendarManager";

    setup() {
        this.state = useState({
            slots: [],
            totalHours: 0,
        });
        onMounted(() => this.initializeTimepickers());
    }
    // ... resto della logica
}

registry.category("public_components").add("CalendarManager", CalendarManager);
```

---

### 7. DATA / MIGRATIONS

#### Script di migrazione richiesti:

**Non sono necessari script di migrazione dati** per questo modulo poiché:
- Non ci sono rinominazioni di campi
- Non ci sono modifiche strutturali ai dati
- Non ci sono nuove tabelle con dati da migrare

#### Verifica XMLID:

| XMLID | Modello | Stato |
|-------|---------|-------|
| `portal_time_off.view_employee_form_inherit_portal` | `ir.ui.view` | ✅ OK |
| `portal_time_off.portal_time_off_template` | `ir.ui.view` | ✅ OK |
| `portal_time_off.portal_my_home_inherit` | `ir.ui.view` | ✅ OK |
| `portal_time_off.access_*` | `ir.model.access` | ⚠️ Verificare conflitti |

---

### 8. API MAIL E CRON

#### Compatibilità `message_post`:

Il modulo **non utilizza** `message_post` o altre API mail direttamente. Nessuna modifica richiesta.

#### Scheduled Actions (Cron):

Il modulo **non definisce** Scheduled Actions. Nessuna modifica richiesta.

---

## CHECKLIST PRE-MIGRAZIONE

- [ ] Verificare che `l4l_timesheet_portal` sia disponibile per Odoo 19 o rimuovere dipendenza
- [ ] Aggiornare versione nel manifest a `19.0.1.0.0`
- [ ] Creare file `README.rst` con descrizione modulo
- [ ] Completare `ir.model.access.csv` con tutte le ACL necessarie
- [ ] Aggiungere Record Rules per sicurezza portal
- [ ] Sostituire `print()` con `_logger`
- [ ] Aggiornare traduzioni a `self.env._()` / `request.env._()`
- [ ] Testare widget JavaScript `calendar_manager.js` in Odoo 19
- [ ] Eseguire test funzionali completi
- [ ] Eseguire `pylint --load-plugins=pylint_odoo` per validazione finale

## CHECKLIST POST-MIGRAZIONE

- [ ] Verificare creazione utenti portal funzionante
- [ ] Verificare richiesta ferie da portal
- [ ] Verificare gestione calendari personali
- [ ] Verificare visualizzazione allocazioni
- [ ] Verificare sicurezza: utenti portal vedono solo propri dati
- [ ] Test multi-company (se applicabile)

---

## RIFERIMENTI

- [Odoo 19 ORM Changelog](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm/changelog.html)
- [Odoo 19 Release Notes](https://www.odoo.com/odoo-19-release-notes)
- [OCA Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Ede/guidelines/guideline_module.rst)
- [OpenUpgradeLib](https://github.com/OCA/openupgradelib)
- [pylint-odoo](https://github.com/OCA/pylint-odoo)

---

**Analisi generata con:** pylint-odoo 10.0.0
**Data analisi:** 2026-02-04
**Analista:** Claude Code (Migration Assistant)
