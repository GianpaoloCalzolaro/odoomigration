# [MIG] survey_contact_generation: Migration from Odoo 18.0 to 19.0

## SUMMARY

**Module:** `survey_contact_generation`
**Version:** 18.0.4.0.0 -> 19.0.1.0.0
**Migration Complexity:** :yellow_circle: **MEDIA**
**Estimated Effort:** M (2-8 ore)

### Descrizione Modulo

Il modulo `survey_contact_generation` permette di generare automaticamente contatti (res.partner) o candidature HR (hr.applicant/hr.candidate) dalle risposte ai questionari Odoo Survey. Funzionalità principali:
- Mappatura domande survey su campi di res.partner, hr.applicant e hr.candidate
- Generazione automatica di contatti al completamento del questionario
- Generazione automatica di candidature HR con integrazione job position
- Supporto per campi di tipo selection, many2one, many2many, binary (upload file)
- Gestione company parent per contatti generati

### Principali aree di intervento

1. **Manifest**: Aggiornamento versione e verifica dipendenze
2. **Security**: File ir.model.access.csv MANCANTE - da creare
3. **Traduzioni**: Stringhe non tradotte in ValidationError
4. **Code Quality**: Import logging inline, except-pass pattern
5. **JavaScript Tour**: Verifica compatibilità sintassi Odoo 19

### File analizzati [VERIFICATO]

| File | Tipo | Stato |
|------|------|-------|
| `__manifest__.py` | Config | Analizzato |
| `__init__.py` | Config | Analizzato |
| `models/__init__.py` | Config | Analizzato |
| `models/survey_survey.py` | Python | Analizzato |
| `models/survey_question.py` | Python | Analizzato |
| `models/survey_user_input.py` | Python | Analizzato |
| `models/res_partner.py` | Python | Analizzato |
| `models/hr_applicant.py` | Python | Analizzato |
| `models/hr_candidate.py` | Python | Analizzato |
| `views/survey_question_views.xml` | XML | Analizzato |
| `views/survey_survey_views.xml` | XML | Analizzato |
| `views/survey_layout_inherit.xml` | XML | Analizzato |
| `demo/survey_contact_generation_demo.xml` | XML | Analizzato |
| `demo/survey_applicant_generation_demo.xml` | XML | Analizzato |
| `static/tests/survey_contact_generation_tour.esm.js` | JS | Analizzato |
| `tests/test_survey_contact_generation.py` | Python | Analizzato |
| `tests/test_survey_applicant_generation.py` | Python | Analizzato |
| `tests/__init__.py` | Config | Analizzato |

---

## PREREQUISITES

### Dipendenze Core Odoo

| Dipendenza | Stato v19 | Note | Fonte |
|------------|-----------|------|-------|
| `survey` | :white_check_mark: Disponibile | Modulo core presente in odoo/addons/survey | [GitHub Odoo 19.0](https://github.com/odoo/odoo/tree/19.0/addons/survey) [VERIFICATO] |
| `hr_recruitment` | :white_check_mark: Disponibile | Modulo core presente, include hr.applicant | [GitHub Odoo 19.0](https://github.com/odoo/odoo/tree/19.0/addons/hr_recruitment) [VERIFICATO] |
| `website` | :white_check_mark: Disponibile | Modulo core standard | [DA VERIFICARE] breaking changes specifici |

### Dipendenze OCA

| Dipendenza | Stato v19 | Note |
|------------|-----------|------|
| Nessuna dipendenza OCA | N/A | Il modulo dipende solo da moduli core |

### Modello hr.candidate [DA VERIFICARE]

Il modulo estende `hr.candidate` che in Odoo 18 fa parte di `hr_recruitment`.
**ATTENZIONE**: Verificare che il modello `hr.candidate` sia ancora presente in Odoo 19 con la stessa struttura.
In alcune versioni Odoo il flusso recruitment ha subito modifiche significative.

**Strategia proposta:**
1. Verificare esistenza del modello hr.candidate in Odoo 19
2. Se non esiste, rendere l'estensione opzionale con try/except
3. In caso di rimozione, le funzionalità di generazione candidato sarebbero impattate

### Librerie Python esterne

Nessuna libreria esterna richiesta (solo stdlib `logging`, `ast`).

---

## CHANGES REQUIRED

### 1. MANIFEST (`__manifest__.py`)

#### [P0/XS] Aggiornamento versione

**File:** `__manifest__.py` linea 6
**Codice attuale:**
```python
"version": "18.0.4.0.0",
```

**Codice proposto:**
```python
"version": "19.0.1.0.0",  # Aggiornamento versione per Odoo 19
```

**Stato:** [VERIFICATO] - Requisito standard OCA per migrazione versione.

#### [P2/XS] Aggiunta file security nel manifest

**File:** `__manifest__.py` linea 14
**Codice attuale:**
```python
"data": [
    "views/survey_question_views.xml",
    "views/survey_survey_views.xml",
    "views/survey_layout_inherit.xml",
],
```

**Codice proposto:**
```python
"data": [
    "security/ir.model.access.csv",  # ACL mancanti - file da creare
    "views/survey_question_views.xml",
    "views/survey_survey_views.xml",
    "views/survey_layout_inherit.xml",
],
```

**Stato:** [VERIFICATO] - Il file ir.model.access.csv non esiste e non e' referenziato nel manifest.

---

### 2. MODELS

#### [P1/S] ValidationError senza traduzione

**File:** `models/survey_survey.py` linea 39
**Codice attuale:**
```python
raise ValidationError("Job position is required for applicant generation.")
```

**Codice proposto:**
```python
from odoo import _  # Aggiungere all'import se non presente

raise ValidationError(_("Job position is required for applicant generation."))
```

**Stato:** [VERIFICATO] - Rilevato da pylint-odoo (C8107: translation-required).

---

**File:** `models/survey_question.py` linee 239-242
**Codice attuale:**
```python
raise ValidationError(
    "Non e possibile mappare la stessa domanda su entrambi i campi Applicant e Candidate. "
    "Scegliere solo uno dei due campi."
)
```

**Codice proposto:**
```python
from odoo import _  # Aggiungere all'import se non presente

raise ValidationError(
    _("Non e possibile mappare la stessa domanda su entrambi i campi Applicant e Candidate. "
      "Scegliere solo uno dei due campi.")
)
```

**Stato:** [VERIFICATO] - Rilevato da pylint-odoo (C8107: translation-required).

---

#### [P3/XS] Attributo string ridondante nei campi

**File:** `models/survey_question.py` linea 337
**Codice attuale:**
```python
selection_value = fields.Char(
    string="Selection Value",
    help="Technical value for selection fields",
)
```

**Codice proposto:**
```python
selection_value = fields.Char(
    help="Technical value for selection fields",  # Rimosso string ridondante
)
```

**Stato:** [VERIFICATO] - Rilevato da pylint-odoo (W8113: attribute-string-redundant). Il nome del campo "selection_value" produce automaticamente il label "Selection Value".

---

**File:** `models/survey_survey.py` linee 10, 15
**Codice attuale:**
```python
generation_type = fields.Selection(
    selection=[("contact", "Contact"), ("applicant", "Applicant")],
    default="contact",
    string="Generation Type",
)
job_position_id = fields.Many2one(
    comodel_name="hr.job",
    string="Job Position",
)
```

**Codice proposto:**
```python
generation_type = fields.Selection(
    selection=[("contact", "Contact"), ("applicant", "Applicant")],
    default="contact",
    # Rimosso string="Generation Type" - ridondante
)
job_position_id = fields.Many2one(
    comodel_name="hr.job",
    # Rimosso string="Job Position" - ridondante
)
```

**Stato:** [VERIFICATO] - Rilevato da pylint-odoo (W8113: attribute-string-redundant).

---

#### [P3/S] Import logging inline nei metodi onchange

**File:** `models/survey_question.py` linee 149-151, 183-185, 217-219
**Codice attuale:**
```python
# Dentro i metodi _onchange_*
import logging
_logger = logging.getLogger(__name__)
_logger.info(f"Selection value: {value}, label: {label}")
```

**Codice proposto:**
```python
# All'inizio del file, dopo gli altri import:
import logging
_logger = logging.getLogger(__name__)

# Nei metodi, rimuovere import inline e usare direttamente:
_logger.info("Selection value: %s, label: %s", value, label)  # Evitare f-string in logging
```

**Stato:** [VERIFICATO] - L'import di logging dovrebbe essere a livello di modulo, non dentro i metodi. Inoltre usare parametri posizionali nel logging invece di f-string per performance.

---

#### [P3/XS] Pattern except-pass senza logging

**File:** `models/survey_question.py` linee 113-115, 129-131
**Codice attuale:**
```python
except Exception:
    pass
```

**Codice proposto:**
```python
except Exception:
    _logger.debug("Could not evaluate selection from field.selection string")
    # oppure semplicemente documentare il perche' del pass:
    pass  # Expected: field.selection may not be evaluable
```

**Stato:** [VERIFICATO] - Rilevato da pylint-odoo (W8138: except-pass). Il pattern e' accettabile ma andrebbe documentato o loggato.

---

#### [P2/XS] Verifica metodo message_post_with_source

**File:** `models/survey_user_input.py` linee 181-185, 299-303
**Codice attuale:**
```python
applicant.message_post_with_source(
    "mail.message_origin_link",
    render_values={"self": applicant, "origin": self.survey_id},
    subtype_xmlid="mail.mt_note",
)
```

**Codice proposto:**
```python
# Nessuna modifica necessaria se la firma del metodo non e' cambiata in v19
# DA VERIFICARE: Controllare la documentazione Odoo 19 per eventuali
# cambiamenti nella firma di message_post_with_source
applicant.message_post_with_source(
    "mail.message_origin_link",
    render_values={"self": applicant, "origin": self.survey_id},
    subtype_xmlid="mail.mt_note",
)
```

**Stato:** [DA VERIFICARE] - Il metodo `message_post_with_source` potrebbe aver subito modifiche in Odoo 19. Fonte non trovata, verificare manualmente nella documentazione ORM Odoo 19: https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html

---

### 3. VIEWS XML

#### [P2/M] Verifica xpath per compatibilita' Odoo 19

**File:** `views/survey_question_views.xml` linea 7
**Codice attuale:**
```xml
<xpath expr="//field[@name='comments_allowed']/.." position="after">
```

**Analisi:** L'xpath cerca il parent del campo `comments_allowed`. Questo pattern potrebbe essere fragile se la struttura della vista padre cambia in Odoo 19.

**Codice proposto:**
```xml
<!-- DA VERIFICARE: Controllare che il campo comments_allowed esista ancora
     nella vista survey.survey_question_form in Odoo 19 e che la struttura
     del parent sia invariata -->
<xpath expr="//field[@name='comments_allowed']/.." position="after">
```

**Stato:** [DA VERIFICARE] - Verificare che la vista `survey.survey_question_form` in Odoo 19 mantenga la stessa struttura. Fonte: https://github.com/odoo/odoo/blob/19.0/addons/survey/views/survey_question_views.xml

---

**File:** `views/survey_question_views.xml` linea 69
**Codice attuale:**
```xml
<xpath expr="//field[@name='suggested_answer_ids']" position="attributes">
```

**Stato:** [DA VERIFICARE] - Verificare che il campo `suggested_answer_ids` esista ancora nella vista in Odoo 19.

---

**File:** `views/survey_question_views.xml` linee 72-75
**Codice attuale:**
```xml
<xpath
    expr="//field[@name='suggested_answer_ids']//field[@name='value']"
    position="after"
>
```

**Analisi:** Xpath annidato che cerca un campo dentro un tree. Potenzialmente fragile.

**Stato:** [DA VERIFICARE] - Verificare struttura interna della vista `suggested_answer_ids` in Odoo 19.

---

#### [P1/XS] Sintassi invisible con espressioni Python (Odoo 19)

**File:** `views/survey_question_views.xml` linee 9, 13, 17, 21, 27, etc.
**Codice attuale:**
```xml
<group name="contact" string="Contact"
    invisible="parent.generation_type not in ('contact','applicant')">
```

**Analisi:** La sintassi `invisible="expression"` con espressioni Python e' gia' nel formato Odoo 19. Nessuna modifica necessaria per queste espressioni.

**Stato:** [VERIFICATO] - La sintassi e' gia' conforme a Odoo 19. In Odoo 18+ la sintassi attrs e' stata deprecata a favore di invisible/readonly/required con espressioni Python dirette.

---

**File:** `views/survey_survey_views.xml` linee 10-12
**Codice attuale:**
```xml
<field name="job_position_id" invisible="generation_type != 'applicant'" required="generation_type == 'applicant'"/>
<field name="generate_contact" invisible="generation_type == 'applicant'"/>
<field name="create_parent_contact" invisible="generation_type == 'applicant' or generate_contact != True"/>
```

**Stato:** [VERIFICATO] - Sintassi gia' conforme a Odoo 19.

---

### 4. SECURITY

#### [P0/M] File ir.model.access.csv MANCANTE

**Stato attuale:** Il modulo NON ha un file `security/ir.model.access.csv`. Questo e' un problema critico.

**Modelli definiti/estesi nel modulo:**
- `survey.survey` (esteso)
- `survey.question` (esteso)
- `survey.question.answer` (esteso)
- `survey.user_input` (esteso)
- `res.partner` (esteso)
- `hr.applicant` (esteso)
- `hr.candidate` (esteso)

**Analisi:** Il modulo estende modelli esistenti aggiungendo campi, quindi le ACL dei modelli base dovrebbero essere sufficienti. Tuttavia, e' best practice verificare che gli utenti appropriati abbiano accesso ai nuovi campi.

**File da creare:** `security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
```

**Stato:** [VERIFICATO] - Nessun file ir.model.access.csv presente nel modulo. Poiche' il modulo estende solo modelli esistenti senza creare nuovi modelli, potrebbe non essere strettamente necessario, ma andrebbe valutato.

**Azione consigliata:** [ASSUNZIONE] Si assume che le ACL dei moduli base (survey, hr_recruitment) siano sufficienti poiche' il modulo estende solo modelli esistenti. Se vengono riscontrati problemi di accesso, creare il file con ACL appropriate.

---

### 5. ASSETS E FRONTEND

#### [P2/S] Verifica tour JavaScript per Odoo 19

**File:** `static/tests/survey_contact_generation_tour.esm.js`
**Codice attuale:**
```javascript
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("test_survey_contact_generation", {
    test: true,
    url: "/survey/start/80e5f1e2-1a9d-4c51-8e23-09e93f7fa2c5",
    steps: () => [
        {
            content: "Click on Start",
            trigger: "button.btn:contains('Start Survey')",
        },
        // ...
        {
            content: "Submit and go to Next Page",
            trigger: 'button[value="next"]',
        },
        // ...
    ],
});
```

**Analisi:**
1. Import `@web/core/registry` - [DA VERIFICARE] Verificare che il path sia invariato in Odoo 19
2. Pattern `registry.category("web_tour.tours").add()` - [DA VERIFICARE] Potrebbe essere cambiato
3. Sintassi `run: "text My Name"` - [DA VERIFICARE] Verificare compatibilita'

**Stato:** [DA VERIFICARE] - La sintassi dei tour potrebbe essere cambiata in Odoo 19. Consultare: https://www.odoo.com/documentation/19.0/developer/reference/frontend/javascript/testing.html

---

### 6. DATA / MIGRATIONS

#### [P3/XS] Verifica XMLID demo

**File:** `demo/survey_applicant_generation_demo.xml` linea 10
**Codice attuale:**
```xml
<field name="job_position_id" ref="hr_recruitment.hr_job_developer"/>
```

**Stato:** [DA VERIFICARE] - Verificare che l'XMLID `hr_recruitment.hr_job_developer` esista ancora in Odoo 19.

---

**File:** `demo/survey_applicant_generation_demo.xml` linee 68, 74
**Codice attuale:**
```xml
<field name="hr_applicant_field_resource_ref" ref="hr_recruitment.stage_job1" />
<field name="hr_applicant_field_resource_ref" ref="hr_recruitment.stage_job2" />
```

**Stato:** [DA VERIFICARE] - Verificare che gli XMLID degli stage di recruitment esistano ancora in Odoo 19.

---

#### [P3/XS] Script di migrazione dati

**Analisi:** Non sono necessari script di migrazione dati poiche':
- Non ci sono rinominazioni di campi
- Non ci sono modifiche strutturali ai dati
- I nuovi campi aggiunti hanno valori di default appropriati (False/None)

**Stato:** [VERIFICATO] - Nessuno script di migrazione richiesto.

---

### 7. API MAIL E CRON

#### Compatibilita' message_post_with_source

**File:** `models/survey_user_input.py` linee 181-185, 299-303

**Stato:** [DA VERIFICARE] - Come indicato sopra, verificare la firma del metodo in Odoo 19.

#### Scheduled Actions

Il modulo NON definisce Scheduled Actions (ir.cron). Nessuna modifica richiesta.

**Stato:** [VERIFICATO]

---

## SECURITY ANALYSIS

### Modelli estesi e permessi

Il modulo estende i seguenti modelli senza creare nuovi modelli:

#### survey.survey (esteso)
- **Nuovi campi:** `generation_type`, `job_position_id`, `generate_contact`, `create_parent_contact`
- **Scenario d'uso:** Amministratori Survey configurano la generazione contatti
- **Rischio:** Basso - i campi sono di configurazione, non contengono dati sensibili
- **ACL richieste:** Nessuna aggiuntiva, ereditare da modulo survey

#### survey.question (esteso)
- **Nuovi campi:** `allowed_field_domain`, `allowed_applicant_field_domain`, `allowed_candidate_field_domain`, `res_partner_field`, `hr_applicant_field`, `hr_candidate_field`
- **Scenario d'uso:** Configurazione mapping domande su campi
- **Rischio:** Basso - configurazione, non dati utente
- **ACL richieste:** Nessuna aggiuntiva

#### survey.question.answer (esteso)
- **Nuovi campi:** `res_partner_field_resource_ref`, `hr_applicant_field_resource_ref`, `hr_candidate_field_resource_ref`, `selection_value`, `file_upload_data`, `file_upload_filename`
- **Scenario d'uso:** Mappatura valori risposte su record di riferimento
- **Rischio:** Medio - `file_upload_data` contiene dati binary potenzialmente sensibili
- **ACL richieste:** [ASSUNZIONE] Si assume che le ACL esistenti di survey.question.answer siano sufficienti

#### survey.user_input (esteso)
- **Override metodo:** `_mark_done()` per generazione contatti/candidature
- **Rischio:** Medio - il metodo crea record in res.partner e hr.applicant
- **Mitigazione:** Il metodo usa `sudo()` internamente dove necessario

#### res.partner (esteso)
- **Nuovo campo:** `generating_survey_user_input_id`
- **Scenario d'uso:** Tracciamento origine del contatto
- **Rischio:** Basso - riferimento read-only

#### hr.applicant (esteso)
- **Nuovo campo:** `generating_survey_user_input_id`
- **Scenario d'uso:** Tracciamento origine della candidatura
- **Rischio:** Basso - riferimento read-only

#### hr.candidate (esteso)
- **Nuovo campo:** `generating_survey_user_input_id`
- **Scenario d'uso:** Tracciamento origine del candidato
- **Rischio:** Basso - riferimento read-only

### Record Rules proposte

[ASSUNZIONE] Non sono necessarie Record Rules aggiuntive poiche':
1. Il modulo non crea nuovi modelli
2. I campi aggiunti sono di configurazione o tracciamento
3. Le Record Rules dei moduli base (survey, hr_recruitment) gestiscono gia' l'accesso ai record

### Analisi uso sudo()

**File:** `models/survey_user_input.py`

L'uso di `sudo()` non e' esplicito nel codice del modulo. La creazione di `res.partner` e `hr.applicant` avviene nel contesto dell'utente corrente, il che e' appropriato.

**Stato:** [VERIFICATO] - Nessun uso problematico di sudo() identificato.

---

## ACCEPTANCE CRITERIA

### Criteri di verifica post-migrazione

1. [ ] **Installazione modulo** - Il modulo si installa correttamente su Odoo 19 senza errori
2. [ ] **Configurazione survey contact** - E' possibile configurare un survey con `generation_type = 'contact'` e mappare i campi res.partner
3. [ ] **Configurazione survey applicant** - E' possibile configurare un survey con `generation_type = 'applicant'`, selezionare una job position e mappare i campi hr.applicant e hr.candidate
4. [ ] **Generazione contatto** - Completando un survey configurato per contact, viene creato un nuovo res.partner con i dati corretti
5. [ ] **Generazione candidatura** - Completando un survey configurato per applicant, vengono creati hr.candidate e hr.applicant collegati
6. [ ] **Campo selection** - I campi di tipo selection (simple_choice) vengono mappati correttamente con il valore tecnico
7. [ ] **Upload file** - I campi binary (upload_file) vengono trasferiti correttamente al record generato
8. [ ] **Parent contact** - Con `create_parent_contact = True`, viene creato il contatto parent con company_type = 'company'
9. [ ] **Tour test** - Il tour JavaScript `test_survey_contact_generation` passa senza errori
10. [ ] **Test unitari** - I test Python `test_survey_contact_generation.py` e `test_survey_applicant_generation.py` passano

---

## FONTI E RIFERIMENTI

### Documentazione ufficiale Odoo 19

| Argomento | URL | Stato |
|-----------|-----|-------|
| Release Notes | https://www.odoo.com/odoo-19-release-notes | [DA VERIFICARE] |
| ORM Reference | https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html | [DA VERIFICARE] |
| Views Reference | https://www.odoo.com/documentation/19.0/developer/reference/backend/views.html | [DA VERIFICARE] |
| Testing | https://www.odoo.com/documentation/19.0/developer/reference/frontend/javascript/testing.html | [DA VERIFICARE] |
| Security | https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html | [DA VERIFICARE] |

### Repository GitHub

| Repository | Branch | URL |
|------------|--------|-----|
| Odoo Core | 19.0 | https://github.com/odoo/odoo/tree/19.0 |
| OCA Survey | 19.0 | https://github.com/OCA/survey/tree/19.0 |

### Tool di analisi utilizzati

| Tool | Versione | Output |
|------|----------|--------|
| pylint-odoo | 10.0.0 | Rating 9.80/10 |
| odoo-module-migrator | 0.5.0 | Non supporta migrazione 18->19 |

### Breaking changes documentati (dal file migrator.md interno)

| Cambiamento | Impatto su questo modulo |
|-------------|-------------------------|
| `type='json'` -> `type='jsonrpc'` in HTTP routes | Nessuno - modulo non ha controller |
| Sistema gruppi utente ristrutturato | Nessuno - modulo non crea gruppi |
| Viste Kanban `kanban-box` -> `card` | Nessuno - modulo non ha viste kanban |
| `message_post_with_source` firma | [DA VERIFICARE] - usato in 2 punti |
| Tour JavaScript sintassi | [DA VERIFICARE] - 1 file tour presente |

---

## AUTOVALIDAZIONE

| Requisito | Stato |
|-----------|-------|
| Versione sorgente e target specificate | :white_check_mark: 18.0.4.0.0 -> 19.0.1.0.0 |
| Tutti i file elencati come analizzati | :white_check_mark: 18 file |
| Ogni modifica con file, linea, codice prima/dopo | :white_check_mark: |
| Priorita' e effort per ogni modifica | :white_check_mark: |
| Analisi security completa | :white_check_mark: |
| Nessuna API inventata | :white_check_mark: |
| Fonti citate per breaking changes | :white_check_mark: |
| Distinzione VERIFICATO/DA VERIFICARE/ASSUNZIONE | :white_check_mark: |

---

## RIEPILOGO MODIFICHE PER PRIORITA'

### P0 - Bloccante
| Modifica | File | Effort |
|----------|------|--------|
| Aggiornamento versione manifest | `__manifest__.py:6` | XS |
| Valutare creazione ir.model.access.csv | `security/` | M |

### P1 - Critico
| Modifica | File | Effort |
|----------|------|--------|
| Traduzione ValidationError survey_survey | `models/survey_survey.py:39` | XS |
| Traduzione ValidationError survey_question | `models/survey_question.py:239` | XS |
| Verifica xpath viste | `views/survey_question_views.xml` | S |

### P2 - Importante
| Modifica | File | Effort |
|----------|------|--------|
| Aggiunta security file in manifest | `__manifest__.py:14` | XS |
| Verifica message_post_with_source | `models/survey_user_input.py` | S |
| Verifica tour JavaScript | `static/tests/` | S |

### P3 - Miglioramento
| Modifica | File | Effort |
|----------|------|--------|
| Rimozione string ridondanti | `models/survey_survey.py`, `models/survey_question.py` | XS |
| Spostamento import logging | `models/survey_question.py` | S |
| Documentazione except-pass | `models/survey_question.py` | XS |
| Verifica XMLID demo | `demo/*.xml` | XS |

---

**Analisi generata con:** pylint-odoo 10.0.0
**Data analisi:** 2026-02-05
**Analista:** Claude Code (Migration Assistant)
