# Migration Analysis: survey_result_mail (Odoo 18 → 19)

## SUMMARY

### Panoramica del modulo
Il modulo **survey_result_mail** estende la funzionalità di Survey di Odoo per inviare automaticamente via email le risposte del sondaggio al partecipante al termine della compilazione.

**Funzionalità principali:**
- Aggiunge un toggle "Send survey answers" nella configurazione del sondaggio
- Permette la selezione di un template mail per l'invio
- Fornisce due template predefiniti: inline (risposte nel body email) e con report PDF allegato
- Trigger automatico dell'invio email al completamento del sondaggio

### Livello di complessità della migrazione
**Media** - Il modulo presenta alcune criticità relative a:
1. Utilizzo di `t-raw` deprecato nei template QWeb (reports)
2. Potenziali cambiamenti nelle view inherited del modulo survey core
3. Necessità di verificare la compatibilità con eventuali breaking changes nel modulo mail

### File analizzati
| File | Tipo | Stato |
|------|------|-------|
| `__manifest__.py` | Manifest | VERIFICATO |
| `__init__.py` | Init | VERIFICATO |
| `models/__init__.py` | Init | VERIFICATO |
| `models/survey_survey.py` | Model | VERIFICATO |
| `models/survey_user_input.py` | Model | VERIFICATO |
| `views/survey_survey_views.xml` | View | VERIFICATO |
| `views/survey_user_input_views.xml` | View | VERIFICATO |
| `templates/survey_answer_templates.xml` | QWeb Template | VERIFICATO |
| `reports/survey_answer_report.xml` | Report | VERIFICATO |
| `data/mail_template.xml` | Data | VERIFICATO |
| `tests/test_survey_result_mail.py` | Test | VERIFICATO |
| `migrations/17.0.1.0.0/post-migration.py` | Migration | VERIFICATO |
| `migrations/17.0.1.0.0/noupdate_changes.xml` | Migration Data | VERIFICATO |

---

## PREREQUISITES

### Dipendenze

| Modulo | Tipo | Stato v19 | Azione richiesta |
|--------|------|-----------|------------------|
| `survey` | Core Odoo | Disponibile | Verificare breaking changes |

**Analisi dipendenza `survey` (Core Odoo):**
- **Disponibilità:** Il modulo `survey` è un modulo core di Odoo, quindi sarà disponibile nella versione 19. VERIFICATO
- **Breaking changes:** DA VERIFICARE - Non è stata trovata documentazione specifica sui breaking changes del modulo survey in Odoo 19. Verificare nel changelog ufficiale di Odoo 19: https://www.odoo.com/documentation/19.0/developer/reference/backend/orm/changelog.html

**Dipendenze implicite (via survey):**
- `mail` - per la funzionalità di invio email
- `web` - per i template QWeb

### Librerie Python esterne
| Libreria | Utilizzo | Note |
|----------|----------|------|
| `markupsafe` | Markup HTML sicuro | Inclusa in Odoo, nessuna azione richiesta |

---

## CHANGES REQUIRED

### 1. Manifest

#### [P0/XS] Aggiornamento versione nel manifest
**File:** `__manifest__.py` linea 6

**Codice attuale:**
```python
"version": "18.0.1.0.0",
```

**Codice proposto:**
```python
"version": "19.0.1.0.0",  # Aggiornamento versione per Odoo 19
```

**Stato:** VERIFICATO - Modifica standard richiesta per ogni migrazione OCA.

**Fonte:** Standard OCA migration guidelines - https://github.com/OCA/maintainer-tools/blob/master/CONTRIBUTING.md

---

### 2. Models

#### [P3/XS] Aggiunta docstring alle classi (pylint-odoo)
**File:** `models/survey_survey.py` linea 6

**Codice attuale:**
```python
class SurveySurvey(models.Model):
    _inherit = "survey.survey"
```

**Codice proposto:**
```python
class SurveySurvey(models.Model):
    """Extension of survey.survey to add result mail functionality."""

    _inherit = "survey.survey"
```

**Stato:** VERIFICATO - Rilevato da pylint-odoo (missing-class-docstring).

---

#### [P3/XS] Aggiunta docstring alla classe SurveyUserInput
**File:** `models/survey_user_input.py` linea 9

**Codice attuale:**
```python
class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"
```

**Codice proposto:**
```python
class SurveyUserInput(models.Model):
    """Extension of survey.user_input to compute and send survey results."""

    _inherit = "survey.user_input"
```

**Stato:** VERIFICATO - Rilevato da pylint-odoo (missing-class-docstring).

---

#### [P2/S] Verifica metodo _mark_done per compatibilità Odoo 19
**File:** `models/survey_user_input.py` linee 109-121

**Codice attuale:**
```python
def _mark_done(self):
    """Send the answers when submitted on the so configured surveys"""
    res = super()._mark_done()
    for user_input in self.filtered(
        lambda x: x.survey_id.send_result_mail and (x.partner_id.email or x.email)
    ):
        template = self.survey_id.result_mail_template_id or self.env.ref(
            "survey_result_mail.mail_template_user_input_result_inline"
        )
        template.send_mail(
            user_input.id, email_layout_xmlid="mail.mail_notification_light"
        )
    return res
```

**Analisi:**
- Il metodo `_mark_done()` è un metodo interno del modulo survey che potrebbe essere modificato in Odoo 19
- L'uso di `template.send_mail()` con `email_layout_xmlid` dovrebbe rimanere compatibile secondo la documentazione Odoo 19

**Azione:** DA VERIFICARE - Controllare che il metodo `_mark_done()` esista ancora nel modulo survey di Odoo 19 con la stessa firma. Se modificato, adattare di conseguenza.

**Fonte:** Mixins and Useful Classes — Odoo 19.0 documentation: https://www.odoo.com/documentation/19.0/developer/reference/backend/mixins.html

---

#### [P2/XS] Bug fix: riferimento errato a self.survey_id nel loop
**File:** `models/survey_user_input.py` linea 115

**Codice attuale:**
```python
for user_input in self.filtered(
    lambda x: x.survey_id.send_result_mail and (x.partner_id.email or x.email)
):
    template = self.survey_id.result_mail_template_id or self.env.ref(
```

**Codice proposto:**
```python
for user_input in self.filtered(
    lambda x: x.survey_id.send_result_mail and (x.partner_id.email or x.email)
):
    template = user_input.survey_id.result_mail_template_id or self.env.ref(
```

**Stato:** VERIFICATO - Bug esistente nel codice. Nel loop si itera su `user_input` ma si accede a `self.survey_id` invece di `user_input.survey_id`. Questo potrebbe causare problemi quando si processano più `user_input` con survey diversi.

---

### 3. Views

#### [P1/M] Verifica xpath per group[@name='questions']
**File:** `views/survey_survey_views.xml` linea 7

**Codice attuale:**
```xml
<xpath expr="//group[@name='questions']" position="inside">
    <field name="send_result_mail" />
    <field
        name="result_mail_template_id"
        invisible="not send_result_mail"
    />
</xpath>
```

**Analisi:**
- L'xpath punta a `//group[@name='questions']` nella vista `survey.survey_survey_view_form`
- DA VERIFICARE se questo gruppo esiste ancora in Odoo 19 con lo stesso nome

**Azione:** Verificare nella versione 19 di Odoo che la vista `survey.survey_survey_view_form` contenga ancora il gruppo con `name='questions'`. Se rinominato o rimosso, aggiornare l'xpath.

**Stato:** DA VERIFICARE - Dipende dalla struttura della vista survey in Odoo 19.

---

#### [P3/XS] Miglioramento formattazione XML
**File:** `views/survey_user_input_views.xml` linee 7-13

**Codice attuale:**
```xml
<field name="user_input_line_ids" position="after">
        <field
        name="survey_result"
        widget="html"
        groups="base.group_no_one"
    />
</field>
```

**Codice proposto:**
```xml
<field name="user_input_line_ids" position="after">
    <field
        name="survey_result"
        widget="html"
        groups="base.group_no_one"
    />
</field>
```

**Stato:** VERIFICATO - Indentazione non corretta nel file originale.

---

### 4. Templates QWeb

#### [P1/M] Sostituzione t-raw con t-out nel report
**File:** `reports/survey_answer_report.xml` linea 17

**Codice attuale:**
```xml
<t
    t-raw="user_input.with_context(survey_result_mode='bootstrap').survey_result"
/>
```

**Codice proposto:**
```xml
<t
    t-out="user_input.with_context(survey_result_mode='bootstrap').survey_result"
/>
```

**Stato:** VERIFICATO - `t-raw` è deprecato dalla versione 15.0. In Odoo 19 potrebbe essere rimosso completamente. Il campo `survey_result` restituisce già un oggetto `Markup` (vedi linea 107 di `survey_user_input.py`), quindi `t-out` gestirà correttamente l'HTML.

**Fonte:** QWeb Templates — Odoo 19.0 documentation: https://www.odoo.com/documentation/19.0/developer/reference/frontend/qweb.html

> "t-raw was deprecated because as the code producing the content evolves it can be hard to track that it's going to be used for markup"

---

#### [P2/M] Verifica xpath multipli nei template
**File:** `templates/survey_answer_templates.xml`

**Analisi problematica:**
Il file contiene xpath duplicati che potrebbero causare problemi:

Linee 15-20 e 21-26: xpath duplicato per `survey.question_text_box`
```xml
<xpath expr="//t[@t-call='survey.question_text_box']" position="replace">
    ...
</xpath>
<xpath expr="//t[@t-call='survey.question_text_box']" position="replace">
    ...
</xpath>
```

Linee 33-41, 42-50, 51-59: xpath triplicato per `survey.question_numerical_box`
```xml
<xpath expr="//t[@t-call='survey.question_numerical_box']" position="replace">
    ...
</xpath>
<!-- Ripetuto 3 volte -->
```

**Azione:** DA VERIFICARE - Questi xpath duplicati sembrano un errore nel codice sorgente. Verificare se sono intenzionali o se devono essere rimossi. Gli xpath duplicati con `position="replace"` potrebbero causare comportamenti imprevedibili.

**Stato:** VERIFICATO come presente nel codice - L'intento va chiarito con gli autori originali.

---

#### [P1/S] Verifica inherit_id survey.survey_page_print
**File:** `templates/survey_answer_templates.xml` linea 5

**Codice attuale:**
```xml
<record id="survey_page_print" model="ir.ui.view">
    <field name="name">Survey answers for print</field>
    <field name="inherit_id" ref="survey.survey_page_print" />
    <field name="mode">primary</field>
```

**Analisi:**
- Il template eredita da `survey.survey_page_print`
- DA VERIFICARE se questo template esiste ancora in Odoo 19 con la stessa struttura

**Azione:** Verificare nel codice sorgente di Odoo 19 che il template `survey.survey_page_print` esista e contenga gli elementi referenziati negli xpath.

**Stato:** DA VERIFICARE

---

### 5. Data (Mail Templates)

#### [P3/XS] Typo nel template mail
**File:** `data/mail_template.xml` linee 19 e 52

**Codice attuale:**
```xml
Thanks you for your participation.
```

**Codice proposto:**
```xml
Thank you for your participation.
```

**Stato:** VERIFICATO - Errore grammaticale "Thanks you" invece di "Thank you".

---

#### [P2/XS] Verifica riferimento a model_survey_user_input
**File:** `data/mail_template.xml` linee 5 e 32

**Codice attuale:**
```xml
<field name="model_id" ref="model_survey_user_input" />
```

**Analisi:**
- Il riferimento `model_survey_user_input` dovrebbe puntare al modello `survey.user_input`
- Questo è un riferimento standard Odoo generato automaticamente

**Stato:** VERIFICATO - Sintassi corretta per Odoo 18/19.

---

### 6. Reports

#### [P3/XS] Typo nel nome attachment
**File:** `reports/survey_answer_report.xml` linea 42

**Codice attuale:**
```xml
<field name="attachment">'surevey_results.pdf'</field>
```

**Codice proposto:**
```xml
<field name="attachment">'survey_results.pdf'</field>
```

**Stato:** VERIFICATO - Typo "surevey" invece di "survey".

---

### 7. Tests

#### [P2/S] Miglioramento test per robustezza
**File:** `tests/test_survey_result_mail.py`

**Analisi:**
- Il test `test_certification_auto_sending` è funzionale ma potrebbe essere migliorato
- Manca verifica del contenuto dell'email
- Manca test per il template con report PDF

**Stato:** VERIFICATO - Il test esistente copre il caso base. Miglioramenti sono raccomandati ma non bloccanti.

---

### 8. Migrations

#### [P0/S] Creazione script di migrazione 19.0.1.0.0
**Azione richiesta:** Creare la cartella `migrations/19.0.1.0.0/` con:

**File da creare:** `migrations/19.0.1.0.0/pre-migration.py`
```python
# Copyright 2025 OCA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Pre-migration script for Odoo 19
    # Add any necessary pre-migration logic here
    pass
```

**File da creare:** `migrations/19.0.1.0.0/post-migration.py`
```python
# Copyright 2025 OCA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Post-migration: update noupdate records if needed
    openupgrade.load_data(
        env, "survey_result_mail", "migrations/19.0.1.0.0/noupdate_changes.xml"
    )
```

**Stato:** ASSUNZIONE - Lo script di migrazione è consigliato per gestire eventuali aggiornamenti ai record noupdate (mail templates).

---

## SECURITY ANALYSIS

### Modelli definiti/estesi

Il modulo estende due modelli esistenti senza creare nuovi modelli:

| Modello | Tipo | ACL necessarie |
|---------|------|----------------|
| `survey.survey` | Estensione (inherit) | No - usa ACL esistenti |
| `survey.user_input` | Estensione (inherit) | No - usa ACL esistenti |

### Analisi campi aggiunti

#### Campo `send_result_mail` (survey.survey)
- **Tipo:** Boolean
- **Permessi:** Segue le ACL di `survey.survey`
- **Rischio:** Basso - Un utente con permesso di modifica survey può abilitare/disabilitare l'invio automatico
- **Scenario legittimo:** Amministratore survey configura l'invio risultati
- **Valutazione:** OK - Il campo è protetto dalle ACL esistenti del modulo survey

#### Campo `result_mail_template_id` (survey.survey)
- **Tipo:** Many2one a `mail.template`
- **Domain:** `[('model', '=', 'survey.user_input')]`
- **Permessi:** Segue le ACL di `survey.survey` per la selezione, ma richiede accesso read a `mail.template`
- **Rischio:** Basso - Il domain limita ai template per survey.user_input
- **Scenario legittimo:** Amministratore seleziona quale template usare per le email
- **Valutazione:** OK - Il domain è appropriato e le ACL esistenti sono sufficienti

#### Campo `survey_result` (survey.user_input)
- **Tipo:** Html (computed)
- **Groups:** `base.group_no_one` nella vista (solo modalità sviluppatore)
- **Rischio:** Medio - Contiene le risposte del sondaggio
- **Scenario legittimo:** Debug/sviluppo per verificare il rendering
- **Valutazione:** OK - Correttamente limitato al gruppo sviluppatore

### Analisi metodi sensibili

#### Metodo `_mark_done` override
- **Rischio:** Il metodo invia email automaticamente
- **Mitigazione esistente:** Verifica che `send_result_mail` sia True e che esista un'email
- **Valutazione:** OK - L'email viene inviata solo al partecipante stesso

#### Metodo `_build_answers_html`
- **Rischio:** Genera HTML con le risposte del sondaggio
- **Mitigazione esistente:** Usa `Markup` per escaping sicuro
- **Valutazione:** OK - Nessun rischio XSS grazie a Markup

### Record Rules
Non sono necessarie nuove Record Rules poiché:
1. Il modulo non crea nuovi modelli
2. I campi aggiunti sono protetti dalle ACL esistenti di survey
3. L'invio email è automatico e non richiede permessi aggiuntivi

### Verifica casi edge

| Caso | Gestione | Stato |
|------|----------|-------|
| Partner senza email | Filtrato in `_mark_done` | OK |
| Survey senza template | Usa template default | OK |
| User input senza partner | Usa campo `email` direttamente | OK |
| Multi-company | Non applicabile (survey è cross-company) | OK |

---

## ACCEPTANCE CRITERIA

### Criteri di verifica per la migrazione

1. **[CRITICO] Installazione modulo**
   - [ ] Il modulo si installa senza errori su Odoo 19
   - [ ] Tutte le dipendenze sono soddisfatte
   - [ ] Le viste XML vengono caricate correttamente

2. **[CRITICO] Funzionalità invio email**
   - [ ] Completando un survey con `send_result_mail=True`, viene inviata l'email
   - [ ] L'email contiene le risposte formattate correttamente
   - [ ] Il template inline funziona correttamente
   - [ ] Il template con report PDF funziona e genera l'allegato

3. **[IMPORTANTE] Configurazione survey**
   - [ ] Il campo "Send survey answers" è visibile nella form del survey
   - [ ] Il campo "Mail template" appare quando si abilita l'invio
   - [ ] Il domain del template mostra solo template per survey.user_input

4. **[IMPORTANTE] Report PDF**
   - [ ] Il report `survey_result_report` si genera senza errori
   - [ ] Il contenuto del PDF mostra tutte le risposte
   - [ ] Le date sono formattate correttamente nella lingua del partner

5. **[STANDARD] Test automatici**
   - [ ] Il test `test_certification_auto_sending` passa
   - [ ] Nessun errore nei log durante l'esecuzione dei test

6. **[STANDARD] Migrazione dati**
   - [ ] I survey esistenti con `send_result_mail=True` mantengono la configurazione
   - [ ] I template mail personalizzati sono preservati
   - [ ] Lo storico delle email inviate è consultabile

---

## FONTI E RIFERIMENTI

### Documentazione ufficiale Odoo 19
- Changelog ORM: https://www.odoo.com/documentation/19.0/developer/reference/backend/orm/changelog.html
- QWeb Templates: https://www.odoo.com/documentation/19.0/developer/reference/frontend/qweb.html
- Mixins and Useful Classes: https://www.odoo.com/documentation/19.0/developer/reference/backend/mixins.html
- Email templates: https://www.odoo.com/documentation/19.0/applications/general/companies/email_template.html

### Repository OCA
- Survey repository (branch 19.0): https://github.com/OCA/survey/tree/19.0
- OCA Migration guidelines: https://github.com/OCA/maintainer-tools/blob/master/CONTRIBUTING.md
- odoo-module-migrator: https://github.com/OCA/odoo-module-migrator

### Breaking changes noti Odoo 19
- `t-raw` deprecato dalla v15, verificare rimozione in v19: https://www.odoo.com/documentation/19.0/developer/reference/frontend/qweb.html
- `group_operator` rinominato in `aggregator`: DA VERIFICARE nella documentazione ORM
- `type='json'` HTTP routes cambiato in `type='jsonrpc'`: Non applicabile a questo modulo

### Note aggiuntive
- Il modulo **survey_result_mail** non è presente nel repository OCA survey branch 18.0. Si tratta di un modulo sviluppato da Tecnativa.
- Il branch 19.0 del repository OCA survey esiste ma non contiene ancora moduli migrati (al momento della stesura).

---

## RIEPILOGO MODIFICHE PER PRIORITA'

| Priorità | Effort | Descrizione | File |
|----------|--------|-------------|------|
| P0 | XS | Aggiornamento versione manifest | `__manifest__.py` |
| P0 | S | Creazione script migrazione 19.0 | `migrations/19.0.1.0.0/` |
| P1 | M | Sostituzione t-raw con t-out | `reports/survey_answer_report.xml` |
| P1 | M | Verifica xpath group questions | `views/survey_survey_views.xml` |
| P1 | S | Verifica inherit survey_page_print | `templates/survey_answer_templates.xml` |
| P2 | XS | Bug fix self.survey_id nel loop | `models/survey_user_input.py` |
| P2 | S | Verifica metodo _mark_done | `models/survey_user_input.py` |
| P2 | M | Verifica xpath duplicati | `templates/survey_answer_templates.xml` |
| P2 | XS | Verifica model_id ref | `data/mail_template.xml` |
| P3 | XS | Aggiunta docstring classi | `models/*.py` |
| P3 | XS | Fix indentazione XML | `views/survey_user_input_views.xml` |
| P3 | XS | Typo "Thanks you" | `data/mail_template.xml` |
| P3 | XS | Typo "surevey" | `reports/survey_answer_report.xml` |

**Effort totale stimato:** 4-8 ore (M)

---

*Documento generato il 2026-02-05*
*Versione sorgente: 18.0.1.0.0*
*Versione target: 19.0.1.0.0*
*Analisi eseguita con: pylint-odoo 10.0.0, odoo-module-migrator 0.5.0 (logiche applicate manualmente)*
