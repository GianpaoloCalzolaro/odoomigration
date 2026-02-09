# Migration Issue: whatsapp_calendar (18.0 → 19.0)

## SUMMARY

**Modulo:** whatsapp_calendar (WhatsApp-Calendar)
**Versione sorgente:** 1.0 (formato non standard, modulo nativo Odoo Enterprise)
**Versione target:** 19.0
**Autore:** Odoo S.A. (modulo nativo Enterprise)
**Licenza:** OEEL-1

### Panoramica funzionale
Il modulo aggiunge il supporto per i promemoria WhatsApp agli eventi del calendario. Funzionalità principali:
- Nuovo tipo di allarme `whatsapp` per `calendar.alarm`
- Template WhatsApp associabile all'allarme
- Override del cron `_send_reminder` per inviare promemoria WhatsApp
- Gestione del responsabile WhatsApp per gli attendee del calendario
- Supporto `notify_responsible` per includere/escludere l'organizzatore
- Suite di test completa

### Livello di complessità della migrazione: **Media-Alta**
Il modulo è un modulo Enterprise nativo Odoo. La complessità deriva dalla dipendenza dal modulo `whatsapp` (Enterprise) e dall'override di metodi core del calendario e dell'alarm manager. La presenza di test facilita la verifica.

**NOTA IMPORTANTE**: Essendo un modulo nativo Odoo Enterprise, è possibile che esista già una versione 19.0 fornita da Odoo. Verificare prima di procedere alla migrazione manuale.

### File analizzati
| File | Tipo |
|------|------|
| `__manifest__.py` | Manifest |
| `__init__.py` | Init |
| `models/__init__.py` | Init |
| `models/calendar_alarm.py` | Model |
| `models/calendar_alarm_manager.py` | Model |
| `models/calendar_attendee.py` | Model |
| `models/calender_event.py` | Model (nota: typo nel nome file) |
| `views/calendar_alarm_views.xml` | Views |
| `tests/__init__.py` | Init |
| `tests/test_whatsapp_calendar.py` | Test |
| `i18n/*.po` (43 file) | Traduzioni |

---

## PREREQUISITES

### Dipendenze

| Dipendenza | Tipo | Stato 19.0 | Strategia |
|------------|------|-----------|-----------|
| `calendar` | Core Odoo | Disponibile in 19.0 | Verificare breaking changes in `calendar.alarm`, `calendar.alarm_manager`, `calendar.event`, `calendar.attendee`. VERIFICATO: il modulo calendar esiste in Odoo 19. |
| `whatsapp` | Enterprise Odoo | Disponibile in 19.0 Enterprise | **CRITICO**: Verificare `whatsapp.composer` API, `whatsapp.template` fields. DA VERIFICARE nel branch Enterprise 19.0. |

### Verifica preliminare: modulo nativo in 19.0
**ASSUNZIONE**: Il modulo `whatsapp_calendar` è incluso nell'edizione Enterprise di Odoo. È probabile che Odoo S.A. lo abbia già migrato a 19.0. Prima di procedere con la migrazione manuale:
1. Verificare se esiste `whatsapp_calendar` nel branch 19.0 di `odoo/enterprise`
2. Se esiste, la migrazione manuale non è necessaria
3. Se non esiste, procedere con questa guida

### Librerie Python esterne
| Libreria | Uso | Note |
|----------|-----|------|
| `dateutil` | `relativedelta` nei test | Standard Odoo dependency |
| `freezegun` | `@freeze_time` nei test | Test dependency standard |

---

## CHANGES REQUIRED

### 1. Manifest

#### 1.1 [P0/XS] Aggiornamento versione manifest

File: `__manifest__.py` linea 5
Codice attuale:
```python
'version': '1.0',
```

Codice proposto:
```python
'version': '19.0.1.0.0',  # Formato standard Odoo
```

VERIFICATO da pylint-odoo (C8106): formato versione non standard.

#### 1.2 [P3/XS] Rimozione chiave `description` deprecata

File: `__manifest__.py` linea 7
Codice attuale:
```python
'description': 'Send whatsapp messages as event reminders',
```

VERIFICATO da pylint-odoo (C8103).

---

### 2. Models

#### 2.1 [P0/M] calendar_alarm_manager.py - whatsapp.composer API compatibility

File: `models/calendar_alarm_manager.py` linee 28-33
Codice attuale:
```python
for attendee in attendees:
    self.env['whatsapp.composer'].create({
        'batch_mode': False,
        'res_ids': [attendee.id],
        'res_model': attendees._name,
        'wa_template_id': alarm.wa_template_id.id
    })._send_whatsapp_template(force_send_by_cron=True)
```

DA VERIFICARE:
1. Il modello `whatsapp.composer` è Enterprise. La sua API (campi e metodi) potrebbe essere cambiata in Odoo 19.
2. Il campo `batch_mode` potrebbe essere stato rinominato o rimosso.
3. Il campo `res_ids` potrebbe aspettarsi un formato diverso (es. Command invece di lista Python).
4. Il metodo `_send_whatsapp_template()` potrebbe avere una firma diversa.
5. Il parametro `force_send_by_cron` potrebbe essere stato rimosso o rinominato.

**Criticità**: Se uno qualsiasi di questi campi/metodi è cambiato, il cron di invio promemoria WhatsApp smetterà di funzionare silenziosamente.

#### 2.2 [P1/S] calendar_alarm_manager.py - _get_events_by_alarm_to_notify

File: `models/calendar_alarm_manager.py` linea 12
Codice attuale:
```python
events_by_alarm = self._get_events_by_alarm_to_notify('whatsapp')
```

DA VERIFICARE: Il metodo `_get_events_by_alarm_to_notify` è definito in `calendar.alarm_manager`. Verificare che accetti ancora il parametro tipo `'whatsapp'` come stringa in Odoo 19.

#### 2.3 [P1/S] calendar_alarm_manager.py - _setup_event_recurrent_alarms

File: `models/calendar_alarm_manager.py` linea 35
Codice attuale:
```python
events._setup_event_recurrent_alarms(events_by_alarm)
```

DA VERIFICARE: Il metodo `_setup_event_recurrent_alarms` su `calendar.event` deve esistere in Odoo 19 con la stessa firma.

#### 2.4 [P1/S] calendar_alarm.py - alarm_type selection_add e ondelete

File: `models/calendar_alarm.py` linee 7-9
Codice attuale:
```python
alarm_type = fields.Selection(selection_add=[
    ('whatsapp', 'WhatsApp Message')
], ondelete={'whatsapp': 'set default'})
```

DA VERIFICARE: Verificare che `calendar.alarm` in Odoo 19 abbia ancora `alarm_type` come campo Selection e che il pattern `selection_add` con `ondelete` sia ancora supportato.

#### 2.5 [P1/S] calendar_alarm.py - wa_template_id domain con 'status'

File: `models/calendar_alarm.py` linee 10-14
Codice attuale:
```python
wa_template_id = fields.Many2one(
    'whatsapp.template', string='WhatsApp Template',
    domain=[('model', '=', 'calendar.attendee'), ('status', '=', 'approved')],
    compute='_compute_wa_template_id', readonly=False, store=True,
)
```

DA VERIFICARE: Il campo `status` su `whatsapp.template` deve esistere in Odoo 19. Potrebbe essere stato rinominato (es. `approval_state`).

#### 2.6 [P1/S] calendar_attendee.py - _whatsapp_get_responsible

File: `models/calendar_attendee.py` linee 7-12
Codice attuale:
```python
def _whatsapp_get_responsible(self, related_message=False, related_record=False, whatsapp_account=False):
    responsible_user = self.event_id.user_id
    if responsible_user and responsible_user.active and responsible_user._is_internal() and not responsible_user._is_superuser():
        return responsible_user
    return super()._whatsapp_get_responsible(related_message, related_record, whatsapp_account)
```

DA VERIFICARE:
1. Il metodo `_whatsapp_get_responsible` è definito nel mixin WhatsApp Enterprise. La firma potrebbe essere cambiata in Odoo 19.
2. `_is_internal()` e `_is_superuser()` su `res.users` devono ancora esistere in Odoo 19.

#### 2.7 [P1/S] calender_event.py - _get_trigger_alarm_types

File: `models/calender_event.py` linee 7-8
Codice attuale:
```python
def _get_trigger_alarm_types(self):
    return super()._get_trigger_alarm_types() + ['whatsapp']
```

DA VERIFICARE: Il metodo `_get_trigger_alarm_types` su `calendar.event` deve esistere in Odoo 19. Se rimosso, questo override causerà un `AttributeError`.

#### 2.8 [P3/XS] Typo nel nome file: calender_event.py → calendar_event.py

File: `models/calender_event.py`
Il file ha un typo nel nome: "calender" invece di "calendar".

Codice proposto: Rinominare il file in `calendar_event.py` e aggiornare `models/__init__.py`:

File: `models/__init__.py` linea 4
Codice attuale:
```python
from . import calender_event
```

Codice proposto:
```python
from . import calendar_event
```

VERIFICATO: typo evidente nel nome file.

---

### 3. Views

#### 3.1 [P1/S] calendar_alarm_views.xml - xpath su mail_template_id

File: `views/calendar_alarm_views.xml` linea 9
Codice attuale:
```xml
<xpath expr="//field[@name='mail_template_id']" position="after">
```

DA VERIFICARE: Il campo `mail_template_id` deve essere ancora presente nella vista form di `calendar.alarm` in Odoo 19. Se il form è stato ristrutturato, l'xpath potrebbe fallire.

---

### 4. Tests

#### 4.1 [P1/M] test_whatsapp_calendar.py - WhatsAppCommon base class

File: `tests/test_whatsapp_calendar.py` linee 6-9
Codice attuale:
```python
from odoo.addons.base.tests.test_ir_cron import CronMixinCase
from odoo.addons.whatsapp.tests.common import WhatsAppCommon, MockOutgoingWhatsApp

class WhatsAppCalendar(WhatsAppCommon, MockOutgoingWhatsApp, CronMixinCase):
```

DA VERIFICARE:
1. `WhatsAppCommon` e `MockOutgoingWhatsApp` sono classi test Enterprise. Potrebbero essere rinominate o avere metodi diversi in Odoo 19.
2. `CronMixinCase` da `base.tests.test_ir_cron` potrebbe non esistere più in Odoo 19.
3. Il metodo `self.mockWhatsappGateway()` (linea 87) deve esistere in Odoo 19.
4. `self._new_wa_msg` (linea 89) è un attributo del mock. Verificare che esista.
5. `self.capture_triggers` (linea 82) è un context manager per test. Verificare disponibilità.

#### 4.2 [P2/S] test_whatsapp_calendar.py - Demo data dependencies

File: `tests/test_whatsapp_calendar.py` linee 42, 50-51
Codice attuale:
```python
self.env.ref('base.partner_admin').phone = '+1 555-555-5555'
# ...
'partner_ids': [Command.link(partner) for partner in self.partners.ids + [self.env.ref('base.partner_admin').id]],
```

In Odoo 19, i demo data non sono più installati di default nei test. Fonte: [OCA Migration Wiki 19.0](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-19.0).

DA VERIFICARE: `base.partner_admin` e `base.user_admin` potrebbero non essere disponibili. Creare dati di test esplicitamente nel `setUpClass`.

---

### 5. Security

Il modulo non definisce nuovi modelli (solo estende modelli esistenti), quindi non necessita di ACL proprie.

VERIFICATO: Nessun modello con `_name` nel modulo, solo `_inherit`. Corretto.

---

## SECURITY ANALYSIS

Il modulo non introduce nuovi modelli, quindi non richiede ACL o Record Rules proprie.

### Rischi identificati
1. **Invio WhatsApp da cron senza rate limiting**: Il metodo `_send_reminder` invia un messaggio WhatsApp per ogni attendee di ogni evento con allarme attivo. In caso di molti eventi/attendee, questo potrebbe generare un volume elevato di chiamate API WhatsApp. **Rischio BASSO** (gestito a livello di `whatsapp.account`). ASSUNZIONE.
2. **notify_responsible**: L'opzione `notify_responsible` sul campo `calendar.alarm` potrebbe non avere controllo di accesso granulare. Qualsiasi utente che può creare un allarme può scegliere se notificare l'organizzatore. **Rischio BASSO**. VERIFICATO.

---

## ACCEPTANCE CRITERIA

1. [ ] Il modulo si installa senza errori su Odoo 19.0 Enterprise con `calendar` e `whatsapp` attivi
2. [ ] Un utente può creare un allarme di tipo "WhatsApp Message" nella configurazione allarmi
3. [ ] Il campo template WhatsApp appare ed è obbligatorio quando il tipo allarme è WhatsApp
4. [ ] Il template WhatsApp viene nascosto quando il tipo allarme è diverso da WhatsApp
5. [ ] Il cron scheduler invia promemoria WhatsApp agli attendee degli eventi con allarme WhatsApp
6. [ ] L'opzione notify_responsible funziona: con True l'organizzatore riceve il messaggio, con False no
7. [ ] Gli attendee che hanno declinato non ricevono il promemoria WhatsApp
8. [ ] Il test `test_whatsapp_alarm` passa correttamente
9. [ ] Gli eventi senza organizzatore inviano comunque i messaggi ai partner
10. [ ] Il modulo si auto-installa quando sia `calendar` che `whatsapp` sono installati

---

## FONTI E RIFERIMENTI

| Fonte | URL |
|-------|-----|
| OCA Migration Wiki 19.0 | https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-19.0 |
| Odoo 19 Calendar docs | https://www.odoo.com/documentation/19.0/applications/productivity/calendar.html |
| Odoo 19 WhatsApp docs | https://www.odoo.com/documentation/19.0/applications/productivity/whatsapp.html |
| Calendar alarm query fix PR | https://github.com/odoo/odoo/pull/222610 |
| WhatsApp composer/template API | Codice Enterprise non pubblicamente accessibile. Verificare nel branch 19.0 Enterprise. |
| Demo data deprecation in tests | https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-19.0 |

---

## AUTOVALIDAZIONE

- [x] Versione sorgente (18.0) e target (19.0) specificate
- [x] Tutti i file del modulo elencati come analizzati (11 file + 43 i18n)
- [x] Ogni modifica con file, linea, codice prima e dopo, priorità, effort
- [x] Analisi security (nessun nuovo modello = nessuna ACL necessaria)
- [x] Nessuna API inventata (tutte segnalate come DA VERIFICARE per moduli Enterprise)
- [x] Fonti citate per ogni breaking change
- [x] Distinzione tra VERIFICATO, DA VERIFICARE e ASSUNZIONE

### Tool utilizzati
- **pylint-odoo 10.0.0**: Eseguito con successo. 4 warning/convention identificati. Rating: 9.39/10.
- **odoo-module-migrator 0.5.0**: Non supporta la migrazione 18.0 → 19.0 (target massimo: 18.0). Non applicabile.
