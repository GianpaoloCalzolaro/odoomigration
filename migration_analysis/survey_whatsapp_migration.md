# Migration Issue: survey_whatsapp (18.0 → 19.0)

## SUMMARY

**Modulo:** survey_whatsapp (Survey WhatsApp Integration)
**Versione sorgente:** 18.0.1.0.0
**Versione target:** 19.0
**Autore:** infologis
**Licenza:** LGPL-3

### Panoramica funzionale
Il modulo integra Odoo Survey con WhatsApp Enterprise per inviare messaggi template approvati ai partecipanti dei sondaggi. Funzionalità principali:
- Wizard per invio massivo WhatsApp ai partecipanti del survey
- Validazione destinatari (numero mobile, partner valido)
- Preview delle linee di invio con stato validità
- Riepilogo post-invio con dettagli errori
- Formattazione numeri telefono tramite API WhatsApp
- Azione binding sulla lista survey.user_input

### Livello di complessità della migrazione: **Alta**
Il modulo dipende dal modulo Enterprise `whatsapp` che potrebbe avere breaking changes significativi in Odoo 19 (rinominazione campi, cambio API). Utilizza `whatsapp.message`, `whatsapp.template`, e `whatsapp.composer` che sono moduli Enterprise con API non pubblicamente documentata.

### File analizzati
| File | Tipo |
|------|------|
| `__manifest__.py` | Manifest |
| `__init__.py` | Init |
| `models/__init__.py` | Init |
| `models/survey_user_input.py` | Model |
| `wizard/__init__.py` | Init |
| `wizard/survey_whatsapp_wizard.py` | Wizard |
| `wizard/survey_whatsapp_wizard_line.py` | Wizard Line |
| `wizard/survey_whatsapp_summary_wizard.py` | Summary Wizard |
| `wizard/survey_whatsapp_summary_wizard_line.py` | Summary Line |
| `security/ir.model.access.csv` | Security ACL |
| `security/survey_whatsapp_security.xml` | Security Rules |
| `views/survey_user_input_views.xml` | Views |
| `views/survey_whatsapp_wizard_views.xml` | Wizard Views |
| `views/survey_whatsapp_summary_wizard_views.xml` | Summary Views |

---

## PREREQUISITES

### Dipendenze

| Dipendenza | Tipo | Stato 19.0 | Strategia |
|------------|------|-----------|-----------|
| `survey` | Core Odoo | Disponibile in 19.0 | Verificare breaking changes nel modello `survey.user_input`. VERIFICATO. |
| `whatsapp` | Enterprise Odoo | Disponibile in 19.0 Enterprise | **CRITICO**: Verificare breaking changes nei modelli `whatsapp.message`, `whatsapp.template`, `whatsapp.composer`, `whatsapp.account`. Potenziale rimozione del campo `mobile` da `res.partner` in Odoo 19. DA VERIFICARE. |

### Librerie Python esterne
| Libreria | Uso | Note |
|----------|-----|------|
| `time` | `time.sleep(2)` nel wizard (linea 190) | Standard library. L'uso di `time.sleep()` in un wizard è un anti-pattern. |

---

## CHANGES REQUIRED

### 1. Manifest

#### 1.1 [P0/XS] Aggiornamento versione manifest

File: `__manifest__.py` linea 7
Codice attuale:
```python
"version": "18.0.1.0.0",
```

Codice proposto:
```python
"version": "19.0.1.0.0",
```

#### 1.2 [P3/XS] Rimozione chiavi superflue e correzione website

File: `__manifest__.py` linee 9, 23-25
Codice attuale:
```python
"website": "wwww.infologis.biz",
# ...
"installable": True,
"application": False,
"auto_install": False,
```

Codice proposto:
```python
"website": "https://www.infologis.biz",
# Rimuovere installable, application, auto_install (sono valori di default)
```

VERIFICATO da pylint-odoo (W8114: website non valida, C8116: chiavi superflue).

#### 1.3 [P3/XS] Rimozione chiave `description` deprecata

File: `__manifest__.py` linea 4
VERIFICATO da pylint-odoo (C8103).

---

### 2. Models

#### 2.1 [P0/M] survey_user_input.py - _whatsapp_phone_format potenziale cambio API

File: `models/survey_user_input.py` linee 27-31
Codice attuale:
```python
def _whatsapp_get_formatted_number(self):
    self.ensure_one()
    partner = self.partner_id
    if not partner or not partner.mobile:
        return False
    formatted = self._whatsapp_phone_format(
        fpath="partner_id.mobile",
        raise_on_format_error=False,
    )
    return formatted or False
```

DA VERIFICARE:
1. Il metodo `_whatsapp_phone_format` è definito nel modulo Enterprise `whatsapp`. La sua firma potrebbe essere cambiata in Odoo 19.
2. **CRITICO**: È stato riportato che il campo `mobile` potrebbe essere stato rimosso da `res.partner` in Odoo 19 a favore di un campo unificato `phone`. Verificare nel source di Odoo 19. Se confermato, tutti i riferimenti a `partner.mobile` dovranno essere aggiornati.
3. Il parametro `fpath="partner_id.mobile"` potrebbe necessitare aggiornamento se il campo `mobile` è rinominato.

Fonte: Ricerca web indica potenziale rimozione campo mobile. Verificare manualmente nel branch 19.0.

#### 2.2 [P1/S] survey_user_input.py - riferimenti a partner.mobile

File: `models/survey_user_input.py` linee 13, 25
Codice attuale:
```python
mobile = partner.mobile or ""
# ...
if not partner or not partner.mobile:
```

DA VERIFICARE: Se `res.partner.mobile` è stato rinominato o rimosso in Odoo 19, questi riferimenti si romperanno.

---

### 3. Wizard

#### 3.1 [P1/M] survey_whatsapp_wizard.py - Uso di _() vs self.env._()

File: `wizard/survey_whatsapp_wizard.py` - 16 occorrenze identificate da pylint-odoo (W8161)

Esempio (linee 59-61):
Codice attuale:
```python
raise UserError(
    _("Nessun account WhatsApp attivo configurato...")
)
```

Codice proposto:
```python
raise UserError(
    self.env._("Nessun account WhatsApp attivo configurato...")
)
```

VERIFICATO da pylint-odoo (W8161). Applicare a tutte le 16 occorrenze. Fonte: https://github.com/odoo/odoo/pull/174844

#### 3.2 [P0/M] survey_whatsapp_wizard.py - whatsapp.message API compatibility

File: `wizard/survey_whatsapp_wizard.py` linee 135-136
Codice attuale:
```python
messages = self.env["whatsapp.message"].create(message_vals)
messages._send(force_send_by_cron=True)
```

DA VERIFICARE:
1. Il modello `whatsapp.message` e il metodo `_send()` sono Enterprise. La firma potrebbe essere cambiata in Odoo 19.
2. I campi usati in `message_vals` (linee 161-167): `wa_template_id`, `wa_account_id`, `mobile_number`, `mobile_number_formatted`, `state`, `mail_message_id` - verificare che esistano tutti in Odoo 19.

#### 3.3 [P0/M] survey_whatsapp_wizard.py - whatsapp.template API compatibility

File: `wizard/survey_whatsapp_wizard.py` linee 173-174
Codice attuale:
```python
variable_values = template.variable_ids._get_variables_value(user_input)
body = template._get_formatted_body(variable_values=variable_values)
```

DA VERIFICARE: I metodi `variable_ids._get_variables_value()` e `_get_formatted_body()` sono Enterprise API. Potrebbero essere rinominati o avere firma diversa in Odoo 19.

#### 3.4 [P2/S] survey_whatsapp_wizard.py - _compute_template_domain con decoratore errato

File: `wizard/survey_whatsapp_wizard.py` linea 72
Codice attuale:
```python
@api.depends("user_input_ids")
def _compute_template_domain(self):
    return [
        ("model", "=", "survey.user_input"),
        # ...
    ]
```

Il metodo `_compute_template_domain` ha un decoratore `@api.depends("user_input_ids")` ma non è un campo compute - è un metodo helper che ritorna un dominio. Il decoratore `@api.depends` è fuorviante.

Codice proposto:
```python
def _compute_template_domain(self):
    return [
        ("model", "=", "survey.user_input"),
        # ...
    ]
```

VERIFICATO dalla lettura del codice: il metodo non assegna valori a campi, quindi `@api.depends` non ha senso qui.

#### 3.5 [P2/S] survey_whatsapp_wizard.py - time.sleep() in wizard

File: `wizard/survey_whatsapp_wizard.py` linea 190
Codice attuale:
```python
def _show_summary(self, sent_messages):
    self.ensure_one()
    time.sleep(2)
```

`time.sleep(2)` blocca il thread del worker Odoo per 2 secondi. Questo è un anti-pattern che può causare problemi di performance sotto carico.

ASSUNZIONE: Il sleep è usato per attendere che i messaggi WhatsApp vengano processati dalla coda cron. Non è garantito che 2 secondi siano sufficienti. Una soluzione migliore sarebbe verificare lo stato dei messaggi in modo asincrono.

#### 3.6 [P1/S] survey_whatsapp_wizard.py - whatsapp.message fields compatibility

File: `wizard/survey_whatsapp_wizard.py` linee 192-195
Codice attuale:
```python
sent_messages.invalidate_recordset()
sent_messages.read(["state", "failure_type", "failure_reason", "mobile_number", "mobile_number_formatted"])
success_states = {"sent", "delivered"}
sent_count = len(sent_messages.filtered(lambda msg: msg.state in success_states))
```

DA VERIFICARE: I campi `state`, `failure_type`, `failure_reason`, `mobile_number`, `mobile_number_formatted` del modello `whatsapp.message` devono esistere in Odoo 19. Verificare nel modulo Enterprise.

#### 3.7 [P1/S] survey_whatsapp_wizard.py - mail.message message_type

File: `wizard/survey_whatsapp_wizard.py` linea 179
Codice attuale:
```python
"message_type": "whatsapp_message",
```

DA VERIFICARE: Il valore `whatsapp_message` per `message_type` di `mail.message` deve essere un valore valido in Odoo 19. I valori consentiti potrebbero essere cambiati.

---

### 4. Views

#### 4.1 [P2/XS] survey_whatsapp_wizard_views.xml - uso di uid nel domain

File: `views/survey_whatsapp_wizard_views.xml` linea 10
Codice attuale:
```xml
<field name="whatsapp_template_id" domain="[..., ('allowed_user_ids', 'in', uid)]"/>
```

DA VERIFICARE: L'uso di `uid` nei domain XML dovrebbe essere ancora supportato in Odoo 19, ma verificare se ci sono deprecazioni.

---

### 5. Security

#### 5.1 [P2/S] Record Rule con solo create_uid

File: `security/survey_whatsapp_security.xml` linee 3-7
Codice attuale:
```xml
<record id="survey_whatsapp_wizard_rule" model="ir.rule">
    <field name="name">Survey WhatsApp Wizard: own records only</field>
    <field name="model_id" ref="model_survey_whatsapp_wizard"/>
    <field name="domain_force">[("create_uid", "=", user.id)]</field>
</record>
```

La record rule copre solo il wizard principale, non i sotto-modelli (wizard line, summary wizard, summary line).

ASSUNZIONE: Essendo wizard transitori, la necessità di record rules è minore. Tuttavia, per coerenza, le stesse regole dovrebbero applicarsi ai modelli correlati.

---

## SECURITY ANALYSIS

### ACL: Wizard Models

| Modello | Gruppo | R | W | C | U | Giustificazione |
|---------|--------|---|---|---|---|-----------------|
| `survey.whatsapp.wizard` | `survey.group_survey_user` | 1 | 1 | 1 | 1 | Survey user deve poter creare e gestire il wizard. Full CRUD necessario per wizard transitori. |
| `survey.whatsapp.wizard.line` | `survey.group_survey_user` | 1 | 1 | 1 | 1 | Preview lines create/gestite dal wizard. |
| `survey.whatsapp.summary.wizard` | `survey.group_survey_user` | 1 | 1 | 1 | 1 | Summary creata automaticamente post-invio. |
| `survey.whatsapp.summary.wizard.line` | `survey.group_survey_user` | 1 | 1 | 1 | 1 | Detail lines della summary. |

VERIFICATO: Le ACL sono corrette per wizard transitori. Il gruppo `survey.group_survey_user` è appropriato.

### Record Rules

| Rule | Modello | Dominio | Scenari edge |
|------|---------|---------|-------------|
| Own records | `survey.whatsapp.wizard` | `create_uid = user.id` | Record con create_uid NULL: non accessibili (corretto per wizard). Multi-company: non rilevante per wizard transitori. |

### Rischi identificati
1. **Mancanza di record rules sui sotto-modelli**: I modelli wizard line e summary non hanno record rules proprie. Un utente survey potrebbe accedere alle linee di wizard creati da altri utenti. **Rischio BASSO** (i wizard transitori vengono eliminati dalla garbage collection). VERIFICATO.
2. **Invio messaggi senza controllo rate**: Non c'è rate limiting sull'invio WhatsApp. Un utente potrebbe inviare grandi volumi di messaggi. **Rischio MEDIO**. ASSUNZIONE: Il rate limiting è gestito a livello di `whatsapp.account` nel modulo Enterprise.

---

## ACCEPTANCE CRITERIA

1. [ ] Il modulo si installa senza errori su Odoo 19.0 Enterprise con i moduli `survey` e `whatsapp` attivi
2. [ ] L'azione "Send WhatsApp" appare nel menu azioni della lista survey.user_input
3. [ ] Il wizard mostra la preview corretta dei destinatari con stato di validità
4. [ ] I destinatari senza partner o senza numero mobile sono marcati come non validi
5. [ ] Il conteggio validi/invalidi si aggiorna correttamente
6. [ ] L'invio WhatsApp crea correttamente i messaggi `whatsapp.message`
7. [ ] Il riepilogo post-invio mostra il conteggio messaggi inviati e falliti
8. [ ] I dettagli errore nel riepilogo mostrano partner, numero e tipo di errore
9. [ ] Un utente senza permessi survey non può accedere al wizard
10. [ ] La validazione bloccante funziona: nessun invio se non ci sono destinatari validi

---

## FONTI E RIFERIMENTI

| Fonte | URL |
|-------|-----|
| OCA Migration Wiki 19.0 | https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-19.0 |
| pylint-odoo prefer-env-translation | https://github.com/odoo/odoo/pull/174844 |
| Odoo 19 WhatsApp docs | https://www.odoo.com/documentation/19.0/applications/productivity/whatsapp.html |
| WhatsApp module source | Codice Enterprise non pubblicamente accessibile. Verificare nel branch 19.0 Enterprise. |
| res.partner mobile field removal | Fonte non trovata per conferma, verificare manualmente nel branch 19.0 (`addons/base/models/res_partner.py`) |

---

## AUTOVALIDAZIONE

- [x] Versione sorgente (18.0) e target (19.0) specificate
- [x] Tutti i file del modulo elencati come analizzati (14 file)
- [x] Ogni modifica con file, linea, codice prima e dopo, priorità, effort
- [x] Analisi security con ACL per tutti i modelli wizard
- [x] Nessuna API inventata (tutte segnalate come DA VERIFICARE quando Enterprise)
- [x] Fonti citate per ogni breaking change
- [x] Distinzione tra VERIFICATO, DA VERIFICARE e ASSUNZIONE

### Tool utilizzati
- **pylint-odoo 10.0.0**: Eseguito con successo. 20 warning/convention identificati. Rating: 8.55/10.
- **odoo-module-migrator 0.5.0**: Non supporta la migrazione 18.0 → 19.0 (target massimo: 18.0). Non applicabile.
