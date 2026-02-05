# Migration Analysis: survey_crm_generation (Odoo 18.0 → 19.0)

## SUMMARY

### Panoramica del Modulo

Il modulo `survey_crm_generation` permette di generare lead/opportunità CRM automaticamente quando un utente completa un sondaggio. Le funzionalità principali sono:

- Configurazione del sondaggio per abilitare la generazione lead
- Mappatura delle risposte ai campi del modello `crm.lead`
- Inclusione automatica delle risposte selezionate nella descrizione del lead
- Invio di messaggi interni con link al sondaggio completato

### Livello di Complessità della Migrazione

**ALTA** - Motivazioni:
1. [P0/L] Dipendenza critica `survey_result_mail` NON disponibile in OCA 18.0 né 19.0
2. [P1/S] Necessità di implementare/copiare il metodo `_build_answers_html` dalla dipendenza mancante
3. [P2/XS] Modifiche minori per logging best practices

### File Analizzati

| File | Linee | Stato |
|------|-------|-------|
| `__manifest__.py` | 27 | VERIFICATO |
| `__init__.py` | 1 | VERIFICATO |
| `models/__init__.py` | 4 | VERIFICATO |
| `models/crm_lead.py` | 10 | VERIFICATO |
| `models/survey_question.py` | 36 | VERIFICATO |
| `models/survey_survey.py` | 17 | VERIFICATO |
| `models/survey_user_input.py` | 94 | VERIFICATO |
| `views/survey_survey_views.xml` | 21 | VERIFICATO |
| `views/survey_question_views.xml` | 24 | VERIFICATO |
| `views/survey_user_input_views.xml` | 17 | VERIFICATO |
| `views/crm_lead_views.xml` | 17 | VERIFICATO |
| `demo/survey_crm_demo.xml` | 73 | VERIFICATO |
| `tests/test_survey_crm_sale_generation.py` | 51 | VERIFICATO |
| `static/tests/survey_crm_generation_tour.esm.js` | 60 | VERIFICATO |

---

## PREREQUISITES

### Dipendenze Core Odoo

| Modulo | Stato in 19.0 | Note |
|--------|---------------|------|
| `crm` | ✅ Disponibile | Verificato su https://github.com/odoo/odoo/tree/19.0/addons/crm |
| `survey` | ✅ Disponibile | Verificato su https://github.com/odoo/odoo/tree/19.0/addons/survey |

### Dipendenze OCA

| Modulo | Repository | Stato 18.0 | Stato 19.0 | Strategia |
|--------|------------|------------|------------|-----------|
| `survey_result_mail` | OCA/survey | ❌ Non portato | ❌ Non portato | CRITICO - vedi sezione dedicata |

**VERIFICATO**: Il modulo `survey_result_mail` è disponibile solo in OCA/survey branch 17.0.
- Fonte: https://github.com/OCA/survey/tree/18.0 (non contiene survey_result_mail)
- Fonte: https://github.com/OCA/survey/tree/17.0/survey_result_mail (ultima versione disponibile)

### Strategia per survey_result_mail [P0/L]

**ASSUNZIONE**: Si assume che la dipendenza sia necessaria principalmente per il metodo `_build_answers_html`.

**Opzioni:**

1. **Opzione A - Migrare survey_result_mail prima** (Raccomandato)
   - Effort: L (1-3 giorni)
   - PRO: Soluzione completa, mantiene funzionalità email risultati
   - CONTRO: Richiede migrazione di altro modulo

2. **Opzione B - Copiare solo il metodo necessario**
   - Effort: S (30 min - 2 ore)
   - PRO: Veloce, indipendente
   - CONTRO: Duplicazione codice, potenziale divergenza

3. **Opzione C - Rimuovere la dipendenza**
   - Funzionalità perse:
     - `_build_answers_html`: formattazione HTML delle risposte per descrizione lead
     - Invio automatico email con risposte al compilatore (se usato)
   - Effort: M (2-8 ore) - richiede reimplementazione `_build_answers_html`

**Raccomandazione**: Opzione B - copiare il metodo `_build_answers_html` da survey_result_mail v17.0, rimuovendo la dipendenza dal manifest.

### Librerie Python Esterne

Nessuna libreria Python esterna richiesta. **VERIFICATO**

---

## CHANGES REQUIRED

### 1. Manifest [P0/M]

**File:** `__manifest__.py` linea 6

**Codice attuale:**
```python
"version": "18.0.1.0.1",
```

**Codice proposto:**
```python
"version": "19.0.1.0.0",  # Reset patch version per nuova major release OCA standard
```

---

**File:** `__manifest__.py` linea 13

**Codice attuale:**
```python
"depends": ["survey_result_mail", "crm"],
```

**Codice proposto (Opzione B):**
```python
"depends": ["survey", "crm"],  # Rimossa dipendenza survey_result_mail, aggiunto survey diretto
```

**Stato:** ASSUNZIONE - Si assume che survey_result_mail non verrà portato in tempo. Verificare prima di procedere lo stato su https://github.com/OCA/survey/tree/19.0

---

### 2. Models

#### 2.1 survey_user_input.py - Implementare _build_answers_html [P0/M]

**File:** `models/survey_user_input.py` linea 73

**Codice attuale:**
```python
def _prepare_lead_description(self):
    """We can have surveys without partner. It's handy to have some relevant info
    in the description although the answers are linked themselves.

    :return str: description for the lead
    """
    return self._build_answers_html(
        self.user_input_line_ids.filtered("question_id.show_in_lead_description")
    )
```

**Problema:** Il metodo `_build_answers_html` proviene da `survey_result_mail` che non è disponibile.

**Codice proposto (aggiungere prima di `_prepare_lead_description`):**
```python
def _build_answers_html(self, given_answers=None):
    """Basic html formatted answers. Can be used in mail communications
    and other html fields without worrying about styles.

    Copiato da survey_result_mail v17.0 per rimuovere dipendenza non disponibile in 19.0
    Fonte: https://github.com/OCA/survey/blob/17.0/survey_result_mail/models/survey_user_input.py

    :param given_answers: recordset di survey.user_input.line, default self.user_input_line_ids
    :return: Markup HTML formattato delle risposte
    """
    from markupsafe import Markup

    if given_answers is None:
        given_answers = self.user_input_line_ids

    answers = given_answers.filtered(lambda x: not x.skipped)
    result_lines = []

    for answer in answers:
        question = answer.question_id
        title = question.title

        if answer.answer_type == "date":
            value = answer.value_date
        elif answer.answer_type == "datetime":
            value = answer.value_datetime
        elif answer.answer_type in ("text_box", "char_box"):
            value = answer.value_text_box or answer.value_char_box
        elif answer.answer_type == "numerical_box":
            value = answer.value_numerical_box
        elif answer.answer_type == "suggestion":
            if question.question_type == "simple_choice":
                value = answer.suggested_answer_id.value
            elif question.question_type == "multiple_choice":
                value = ", ".join(
                    answer.suggested_answer_id.mapped("value")
                )
            elif question.question_type == "matrix":
                value = f"{answer.matrix_row_id.value}: {answer.suggested_answer_id.value}"
            else:
                value = answer.suggested_answer_id.value
        else:
            value = ""

        if value:
            result_lines.append(f"<li><em>{title}</em>: <b>{value}</b></li>")

    return Markup("".join(result_lines))
```

**Stato:** DA VERIFICARE - Il codice è basato su survey_result_mail v17.0. Verificare che i nomi dei campi siano ancora validi in Odoo 19 survey module.

---

#### 2.2 survey_user_input.py - Logging f-string [P3/XS]

**File:** `models/survey_user_input.py` linee 47-50

**Codice attuale:**
```python
_logger.warning(
    f"Campo {field_name} non esiste in crm.lead, ignorato "
    f"(survey: {self.survey_id.title}, question: {line.question_id.title})"
)
```

**Codice proposto:**
```python
_logger.warning(
    "Campo %s non esiste in crm.lead, ignorato (survey: %s, question: %s)",
    field_name,
    self.survey_id.title,
    line.question_id.title,
)  # Lazy % formatting come da pylint W1203
```

**Stato:** VERIFICATO - Best practice Python logging, segnalato da pylint-odoo (W1203)

---

**File:** `models/survey_user_input.py` linee 61-64

**Codice attuale:**
```python
_logger.warning(
    f"Campo {field_name} non esiste in crm.lead, ignorato "
    f"(survey: {self.survey_id.title}, question: {line.question_id.title})"
)
```

**Codice proposto:**
```python
_logger.warning(
    "Campo %s non esiste in crm.lead, ignorato (survey: %s, question: %s)",
    field_name,
    self.survey_id.title,
    line.question_id.title,
)  # Lazy % formatting come da pylint W1203
```

**Stato:** VERIFICATO - Identico al precedente

---

#### 2.3 survey_user_input.py - Import markupsafe [P1/XS]

**File:** `models/survey_user_input.py` linea 1-7 (header)

**Codice attuale:**
```python
# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)
```

**Codice proposto:**
```python
# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from markupsafe import Markup

from odoo import fields, models

_logger = logging.getLogger(__name__)
```

**Stato:** VERIFICATO - Necessario per il nuovo metodo `_build_answers_html`. Markup è già dipendenza di Odoo.

---

### 3. Views

#### 3.1 crm_lead_views.xml - Verifica xpath [P2/XS]

**File:** `views/crm_lead_views.xml` linea 7

**Codice attuale:**
```xml
<xpath expr="//group[@name='Misc']/field[@name='team_id']" position="after">
```

**Stato:** VERIFICATO - Il gruppo `Misc` e il campo `team_id` esistono in Odoo 19.0 crm_lead_views.xml
- Fonte: https://github.com/odoo/odoo/blob/19.0/addons/crm/views/crm_lead_views.xml

**Nessuna modifica necessaria.**

---

#### 3.2 survey_survey_views.xml - Verifica xpath [P2/XS]

**File:** `views/survey_survey_views.xml` linea 7

**Codice attuale:**
```xml
<group name="options" position="inside">
```

**Stato:** VERIFICATO - Il gruppo `options` esiste in Odoo 19.0 survey_survey_views.xml
- Fonte: https://github.com/odoo/odoo/blob/19.0/addons/survey/views/survey_survey_views.xml

**Nessuna modifica necessaria.**

---

#### 3.3 survey_question_views.xml - Verifica xpath [P2/XS]

**File:** `views/survey_question_views.xml` linea 7

**Codice attuale:**
```xml
<xpath expr="//field[@name='comments_allowed']/.." position="after">
```

**Stato:** VERIFICATO - Il campo `comments_allowed` esiste in Odoo 19.0 survey_question_views.xml
- Fonte: https://github.com/odoo/odoo/blob/19.0/addons/survey/views/survey_question_views.xml

**Nessuna modifica necessaria.**

---

#### 3.4 survey_user_input_views.xml - Verifica xpath [P2/XS]

**File:** `views/survey_user_input_views.xml` linee 7-8

**Codice attuale:**
```xml
<field name="partner_id" position="before">
```

**Stato:** VERIFICATO - Il campo `partner_id` esiste in `survey_user_input_view_form` in Odoo 19.0
- Fonte: https://github.com/odoo/odoo/blob/19.0/addons/survey/views/survey_user_views.xml

**Nessuna modifica necessaria.**

---

### 4. Security

**Stato:** VERIFICATO - Non esiste file `security/ir.model.access.csv`.

**Analisi:**
- Il modulo estende solo modelli esistenti (`crm.lead`, `survey.survey`, `survey.question`, `survey.user_input`)
- Non crea nuovi modelli, quindi non sono necessari ACL dedicati
- I permessi sono ereditati dai moduli base `crm` e `survey`

**Nessuna modifica necessaria.**

---

### 5. Assets

**File:** `__manifest__.py` linee 21-25

**Codice attuale:**
```python
"assets": {
    "web.assets_tests": [
        "survey_crm_generation/static/tests/survey_crm_generation_tour.esm.js",
    ],
},
```

**Stato:** VERIFICATO - Il bundle `web.assets_tests` e il formato ESM sono supportati in Odoo 19.0.

**Nessuna modifica necessaria.**

---

### 6. JavaScript Tour

**File:** `static/tests/survey_crm_generation_tour.esm.js`

**Analisi:**

| Elemento | Linea | Stato |
|----------|-------|-------|
| Import registry | 3 | ✅ VERIFICATO - `@web/core/registry` valido in 19.0 |
| Tour registration | 5 | ✅ VERIFICATO - Sintassi valida |
| CSS selectors | 11-57 | DA VERIFICARE - Selettori potrebbero cambiare |

**DA VERIFICARE**: I selettori CSS nel tour potrebbero richiedere aggiornamenti se l'HTML del survey è cambiato in Odoo 19. Eseguire il tour manualmente dopo la migrazione.

Selettori potenzialmente fragili:
- `div.js_question-wrapper` (linee 15, 24, 27, 35, 42, 47)
- `button.btn:contains()` (linee 12, 19, 29, 38)
- `div.o_survey_finished` (linea 56)

---

### 7. Tests

**File:** `tests/test_survey_crm_sale_generation.py`

**Codice attuale (linea 3):**
```python
from markupsafe import Markup
```

**Stato:** VERIFICATO - Import valido, Markup è dipendenza standard di Odoo.

**Analisi test:**
| Test | Descrizione | Stato |
|------|-------------|-------|
| `SurveyCrmGenerationCase.setUp` | Setup con tour execution | ✅ DA VERIFICARE runtime |
| `test_lead_generation` | Verifica generazione lead | ✅ Logica valida |

**Nessuna modifica di codice necessaria, ma i test devono essere eseguiti per verificare compatibilità runtime.**

---

### 8. Data & Migrations

#### 8.1 Demo Data

**File:** `demo/survey_crm_demo.xml`

**Stato:** VERIFICATO - Nessun xmlid in conflitto rilevato. Gli xmlid usano il prefisso del modulo.

**Nessuna modifica necessaria.**

---

#### 8.2 Script di Migrazione

**DA VERIFICARE**: Potrebbe essere necessario uno script di migrazione se:
1. Il metodo `_build_answers_html` era usato con signature diversa
2. Dati legacy nelle tabelle estese

**Raccomandazione:** Creare script di migrazione vuoto per futuri utilizzi:

```
migrations/
└── 19.0.1.0.0/
    └── pre-migrate.py
```

**File proposto:** `migrations/19.0.1.0.0/pre-migrate.py`
```python
# Copyright 2024 OCA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

def migrate(cr, version):
    """Pre-migration script for survey_crm_generation 19.0."""
    if not version:
        return
    # Placeholder per future migrazioni dati
    # Utilizzare openupgradelib se necessario
    pass
```

---

## SECURITY ANALYSIS

### Modelli Estesi

Il modulo estende i seguenti modelli senza creare ACL dedicati:

| Modello | Campi Aggiunti | Rischio | Mitigazione |
|---------|----------------|---------|-------------|
| `crm.lead` | `survey_user_input_id` (M2O) | BASSO | Campo readonly, link informativo |
| `survey.survey` | `generate_leads`, `crm_tag_ids`, `crm_team_id` | BASSO | Configurazione admin-only |
| `survey.question` | `show_in_lead_description`, `crm_lead_field` | BASSO | Configurazione admin-only |
| `survey.user_input` | `opportunity_id` (M2O) | MEDIO | Vedi analisi sotto |

### Analisi Dettagliata: survey.user_input.opportunity_id

**Scenario di uso legittimo:**
- Un utente compila un sondaggio pubblico
- Il sistema crea un lead CRM collegato
- Il campo `opportunity_id` collega la risposta al lead generato

**Rischi potenziali:**
1. Un utente con accesso a `survey.user_input` potrebbe vedere lead a cui non dovrebbe accedere tramite il campo `opportunity_id`
2. La creazione del lead usa `sudo()` (linea 91), bypassando i controlli di accesso

**Mitigazione implementata:**
- Il campo `opportunity_id` è `readonly="1"` nella vista (linea 11-12 di survey_user_input_views.xml)
- La vista mostra il campo solo se popolato (`invisible="not opportunity_id"`)

**Raccomandazione:** Nessuna modifica necessaria. I permessi CRM standard proteggono l'accesso ai lead.

### Uso di sudo()

**File:** `models/survey_user_input.py` linea 91

```python
self.opportunity_id = self.env["crm.lead"].sudo().create(vals)
```

**Giustificazione:** L'uso di `sudo()` è necessario perché l'utente che compila il sondaggio (es. utente pubblico o portale) non ha permessi di creazione su `crm.lead`. Il lead viene creato con `company_id=self.env.company.id` (linea 22), rispettando il contesto multi-company.

**Stato:** VERIFICATO - Uso corretto e giustificato di sudo().

---

## ACCEPTANCE CRITERIA

### Criteri di Accettazione per la Migrazione

- [ ] **AC1**: Il modulo si installa senza errori su Odoo 19.0 con database vuoto
- [ ] **AC2**: Il tour test `test_survey_crm_generation` passa completamente
- [ ] **AC3**: Compilando un sondaggio con `generate_leads=True`, viene creato un lead CRM con:
  - Nome uguale al titolo del sondaggio
  - Tags configurati nel sondaggio
  - Team CRM configurato nel sondaggio
  - Descrizione HTML contenente le risposte marcate con `show_in_lead_description`
- [ ] **AC4**: Il lead creato contiene un messaggio interno con link al sondaggio completato
- [ ] **AC5**: I campi mappati (`crm_lead_field`) vengono correttamente popolati nel lead dalle risposte
- [ ] **AC6**: La vista form del lead mostra il link alla risposta del sondaggio
- [ ] **AC7**: La vista form della risposta sondaggio mostra il link al lead generato
- [ ] **AC8**: Il test unitario `test_lead_generation` passa
- [ ] **AC9**: pylint-odoo non riporta errori (warning accettabili)
- [ ] **AC10**: Il modulo funziona in ambiente multi-company (lead creato nella company corretta)

---

## FONTI E RIFERIMENTI

### Documentazione Ufficiale Odoo

| Risorsa | URL |
|---------|-----|
| Odoo 19 Upgrade Guide | https://www.odoo.com/documentation/19.0/administration/upgrade.html |
| ORM Changelog Odoo 19 | https://www.odoo.com/documentation/19.0/developer/reference/backend/orm/changelog.html |

### Repository GitHub

| Repository | Branch | URL |
|------------|--------|-----|
| Odoo Core | 19.0 | https://github.com/odoo/odoo/tree/19.0 |
| OCA/survey | 19.0 | https://github.com/OCA/survey/tree/19.0 |
| OCA/survey | 18.0 | https://github.com/OCA/survey/tree/18.0 |
| OCA/survey | 17.0 (survey_result_mail) | https://github.com/OCA/survey/tree/17.0/survey_result_mail |

### File Verificati in Odoo 19.0

| File | URL |
|------|-----|
| crm_lead.py | https://github.com/odoo/odoo/blob/19.0/addons/crm/models/crm_lead.py |
| crm_lead_views.xml | https://github.com/odoo/odoo/blob/19.0/addons/crm/views/crm_lead_views.xml |
| survey_question.py | https://github.com/odoo/odoo/blob/19.0/addons/survey/models/survey_question.py |
| survey_question_views.xml | https://github.com/odoo/odoo/blob/19.0/addons/survey/views/survey_question_views.xml |
| survey_survey_views.xml | https://github.com/odoo/odoo/blob/19.0/addons/survey/views/survey_survey_views.xml |
| survey_user_views.xml | https://github.com/odoo/odoo/blob/19.0/addons/survey/views/survey_user_views.xml |
| survey_user_input.py | https://github.com/odoo/odoo/blob/19.0/addons/survey/models/survey_user_input.py |

### Breaking Changes Odoo 19 (DA VERIFICARE se applicabili)

| Cambiamento | Impatto su questo modulo |
|-------------|--------------------------|
| `group_operator` → `aggregator` | Nessuno (non usato) |
| `inselect` rimosso | Nessuno (non usato) |
| JSON → JSONRPC controllers | Nessuno (nessun controller) |
| Registry import changes | Nessuno (non usato direttamente) |

---

## RIEPILOGO EFFORT

| Priorità | Descrizione | Effort | File |
|----------|-------------|--------|------|
| P0 | Rimuovere dipendenza survey_result_mail | XS | __manifest__.py |
| P0 | Implementare _build_answers_html | M | survey_user_input.py |
| P0 | Aggiornare versione manifest | XS | __manifest__.py |
| P1 | Aggiungere import Markup | XS | survey_user_input.py |
| P3 | Correggere logging f-string (x2) | XS | survey_user_input.py |

**Effort Totale Stimato: M (2-8 ore)**

- Modifiche codice: 2-4 ore
- Testing manuale: 2-3 ore
- Fix eventuali problemi: 1-2 ore

---

## AUTOVALIDAZIONE

- [x] Versione sorgente (18.0) e target (19.0) specificate
- [x] Tutti i 14 file del modulo elencati come analizzati
- [x] Ogni modifica con file, linea, codice prima e dopo, priorità, effort
- [x] Analisi security con verifica ACL e uso sudo()
- [x] Nessuna API inventata - tutte verificate o segnalate come DA VERIFICARE
- [x] Fonti citate per ogni breaking change menzionato
- [x] Chiara distinzione tra VERIFICATO, DA VERIFICARE e ASSUNZIONE
