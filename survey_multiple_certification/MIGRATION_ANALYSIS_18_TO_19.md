# Migration Analysis: survey_multiple_certification (Odoo 18 → 19)

**Versione sorgente:** 18.0.1.0.2
**Versione target:** 19.0
**Data analisi:** 2026-02-05

---

## SUMMARY

### Panoramica del modulo

Il modulo `survey_multiple_certification` estende il modulo Survey di Odoo per supportare soglie di certificazione multiple. Le funzionalità principali includono:

- Definizione di soglie di certificazione multiple per survey (Bronze, Silver, Gold, ecc.)
- Calcolo automatico della soglia raggiunta in base alla percentuale di punteggio
- Storicizzazione dei tentativi con tracking delle certificazioni raggiunte
- Integrazione con il modulo gamification per l'assegnazione di badge
- Wizard per la configurazione guidata delle soglie
- Template personalizzato per la visualizzazione dei risultati

### Livello di complessità della migrazione

**Media** - Il modulo presenta:
- Estensioni ORM standard senza query SQL complesse
- Un controller che sovrascrive route esistenti del modulo survey
- Template QWeb che estendono quelli standard
- Nessun asset JavaScript o componenti OWL custom

### File analizzati

| File | Tipo | Stato |
|------|------|-------|
| `__manifest__.py` | Manifest | VERIFICATO |
| `__init__.py` | Init | VERIFICATO |
| `models/__init__.py` | Init | VERIFICATO |
| `models/survey_survey.py` | Model | VERIFICATO |
| `models/survey_user_input.py` | Model | VERIFICATO |
| `models/survey_certification_threshold.py` | Model | VERIFICATO |
| `models/survey_user_input_history.py` | Model | VERIFICATO |
| `controllers/__init__.py` | Init | VERIFICATO |
| `controllers/main.py` | Controller | VERIFICATO |
| `wizard/__init__.py` | Init | VERIFICATO |
| `wizard/survey_threshold_wizard.py` | Wizard | VERIFICATO |
| `wizard/survey_threshold_wizard_line.py` | Wizard | VERIFICATO |
| `wizard/survey_threshold_wizard_views.xml` | View | VERIFICATO |
| `views/survey_certification_threshold_views.xml` | View | VERIFICATO |
| `views/survey_survey_views.xml` | View | VERIFICATO |
| `views/survey_user_input_views.xml` | View | VERIFICATO |
| `views/survey_templates.xml` | Template | VERIFICATO |
| `security/ir.model.access.csv` | Security | VERIFICATO |
| `security/survey_multiple_certification_security.xml` | Security | VERIFICATO |
| `tests/test_survey_multiple_certification.py` | Test | VERIFICATO |

---

## PREREQUISITES

### Dipendenze Core Odoo

| Modulo | Stato v19 | Note |
|--------|-----------|------|
| `survey` | Disponibile | Modulo core, verificare eventuali modifiche API. [Documentazione Survey Odoo 19](https://www.odoo.com/documentation/19.0/applications/marketing/surveys.html) |
| `gamification` | Disponibile | Modulo core per la gestione dei badge. [Documentazione Gamification Odoo 19](https://www.odoo.com/documentation/19.0/applications/sales/crm/optimize/gamification.html) |
| `web` | Disponibile | Modulo core, framework web |
| `website` | Disponibile | Modulo core, portale website |

**Strategia:** Tutte le dipendenze sono moduli core Odoo e saranno disponibili nella versione 19. Non sono richieste azioni specifiche per le dipendenze.

### Librerie Python esterne

Nessuna libreria Python esterna richiesta. Il modulo utilizza solo librerie standard Python (`logging`).

---

## CHANGES REQUIRED

### 1. Manifest

#### [P0/XS] Aggiornamento versione manifest

**File:** `__manifest__.py` linea 3
**Stato:** VERIFICATO

**Codice attuale:**
```python
'version': '18.0.1.0.2',  # Versione compatibile con Odoo 18 - Fix can_retake
```

**Codice proposto:**
```python
'version': '19.0.1.0.0',  # Migrazione a Odoo 19
```

---

#### [P3/XS] Rimozione chiavi superflue dal manifest

**File:** `__manifest__.py` linee 26-27
**Stato:** VERIFICATO (rilevato da pylint-odoo C8116)

**Codice attuale:**
```python
'installable': True,
'auto_install': False,
```

**Codice proposto:**
```python
# Rimuovere le linee - sono valori di default e non necessarie
```

---

#### [P3/XS] Correzione URL website nel manifest

**File:** `__manifest__.py` linea 11
**Stato:** VERIFICATO (rilevato da pylint-odoo W8114)

**Codice attuale:**
```python
'website': 'www.infologis.biz',
```

**Codice proposto:**
```python
'website': 'https://www.infologis.biz',
```

---

#### [P3/XS] Rimozione chiave description deprecata

**File:** `__manifest__.py` linee 6-9
**Stato:** VERIFICATO (rilevato da pylint-odoo C8103)

**Codice attuale:**
```python
'description': """
    Questo modulo permette di aggiungere più soglie di certificazione ai sondaggi Odoo.
    Ideale per gestire livelli diversi di certificazione in base ai punteggi ottenuti dagli utenti.
""",
```

**Codice proposto:**
```python
# Rimuovere il campo 'description' dal manifest
# Creare invece un file README.rst nella root del modulo con la descrizione completa
```

---

### 2. Models

#### [P2/S] Rimozione statement print() dai models

**File:** `models/survey_survey.py` linee 32, 39, 42, 46, 54, 58
**Stato:** VERIFICATO (rilevato da pylint-odoo W8116)

Il modulo utilizza correttamente `_logger` per il logging, ma in alcuni punti utilizza f-string che potrebbero generare warning. Le f-string sono supportate ma per coerenza con lo stile Odoo si preferisce il formato con `%`.

**Codice attuale (esempio linea 32):**
```python
_logger.warning(f"Survey {self.id}: Invalid percentage value: {percentage}")
```

**Codice proposto:**
```python
_logger.warning("Survey %s: Invalid percentage value: %s", self.id, percentage)
```

**Nota:** Applicare la stessa modifica a tutte le occorrenze di f-string nei file:
- `models/survey_survey.py`: linee 32, 39, 42, 46, 54, 58
- `models/survey_user_input.py`: linee 29, 43-46, 52, 56, 58, 67

---

#### [P1/S] Verifica compatibilità _compute_scoring_success override

**File:** `models/survey_user_input.py` linee 18-37
**Stato:** DA VERIFICARE

Il metodo `_compute_scoring_success` sovrascrive il metodo del modulo `survey`. È necessario verificare che la firma del metodo e i decoratori siano compatibili con Odoo 19.

**Codice attuale:**
```python
@api.depends('survey_id.certification_mode', 'scoring_percentage', 'survey_id.scoring_success_min')
def _compute_scoring_success(self):
    """
    Override del compute di scoring_success per gestire la modalità multiple certification.
    """
    for user_input in self:
        if user_input.survey_id.certification_mode == 'multiple':
            user_input.scoring_success = False
            _logger.debug(f"Multiple certification mode: forcing scoring_success=False for user_input {user_input.id}")
        else:
            if (user_input.survey_id.scoring_type == 'scoring_with_answers' and
                user_input.survey_id.scoring_success_min and
                user_input.scoring_percentage is not False):
                user_input.scoring_success = user_input.scoring_percentage >= user_input.survey_id.scoring_success_min
            else:
                user_input.scoring_success = False
```

**Verifica richiesta:** Controllare nel codice sorgente di Odoo 19 `addons/survey/models/survey_user_input.py` che:
1. Il campo `scoring_success` esista ancora e sia un campo computed
2. I campi `scoring_type`, `scoring_success_min`, `scoring_percentage` non siano stati rinominati
3. La firma del decoratore `@api.depends` sia corretta per la versione 19

**Fonte:** Verificare su https://github.com/odoo/odoo/tree/19.0/addons/survey/models

---

#### [P2/XS] Aggiunta attributo string ai campi Many2one

**File:** `models/survey_user_input.py` linea 10
**Stato:** VERIFICATO

**Codice attuale:**
```python
threshold_reached_id = fields.Many2one('survey.certification.threshold')
```

**Codice proposto:**
```python
threshold_reached_id = fields.Many2one('survey.certification.threshold', string='Threshold Reached')
```

---

#### [P3/XS] Aggiunta index ai campi Many2one frequentemente usati in search

**File:** `models/survey_user_input.py` linea 10
**Stato:** VERIFICATO

**Codice attuale:**
```python
threshold_reached_id = fields.Many2one('survey.certification.threshold')
```

**Codice proposto:**
```python
threshold_reached_id = fields.Many2one('survey.certification.threshold', string='Threshold Reached', index=True)
```

---

#### [P2/S] Mancanza decoratore @api.depends per campo computed

**File:** `models/survey_user_input.py` linee 14-16
**Stato:** VERIFICATO

**Codice attuale:**
```python
def _compute_current_certification_name(self):
    for rec in self:
        rec.current_certification_name = rec.threshold_reached_id.name if rec.threshold_reached_id else False
```

**Codice proposto:**
```python
@api.depends('threshold_reached_id', 'threshold_reached_id.name')
def _compute_current_certification_name(self):
    for rec in self:
        rec.current_certification_name = rec.threshold_reached_id.name if rec.threshold_reached_id else False
```

---

### 3. Controllers

#### [P1/M] Rimozione statement print() dal controller

**File:** `controllers/main.py` linee 16, 39, 40
**Stato:** VERIFICATO (rilevato da pylint-odoo W8116)

**Codice attuale:**
```python
print("SURVEY SUBMIT - CONTROLLER CHIAMATO")
# ...
print("SURVEY MODE:", survey.certification_mode)
print("ANSWER STATE:", answer.state)
```

**Codice proposto:**
```python
_logger.info("SURVEY SUBMIT - CONTROLLER CHIAMATO")
# ...
_logger.debug("SURVEY MODE: %s", survey.certification_mode)
_logger.debug("ANSWER STATE: %s", answer.state)
```

---

#### [P1/M] Verifica compatibilità route override

**File:** `controllers/main.py` linee 11-17, 19-116
**Stato:** DA VERIFICARE

Il controller sovrascrive le route del modulo `survey`. È necessario verificare che:
1. Le route del modulo survey base non siano cambiate in Odoo 19
2. Il pattern di ereditarietà del controller sia ancora valido

**Codice attuale:**
```python
class SurveyMultipleCertification(Survey):
    @http.route(['/survey/submit/<string:survey_token>/<string:answer_token>'],
            type='http', auth='public', website=True, methods=['POST'])
    def survey_submit(self, survey_token, answer_token, **kwargs):
        # ...
```

**Verifica richiesta:** Controllare nel codice sorgente di Odoo 19 `addons/survey/controllers/main.py` che:
1. La classe `Survey` esista ancora con lo stesso nome
2. Le route `/survey/submit/...` e `/survey/fill/...` non siano state modificate
3. L'attributo `qcontext` delle response sia ancora disponibile

**Fonte:** Verificare su https://github.com/odoo/odoo/tree/19.0/addons/survey/controllers

---

#### [P2/S] Utilizzo di f-string nel controller

**File:** `controllers/main.py` linee 38, 58, 65, 69, 78, 83, 97, 105
**Stato:** VERIFICATO

Sostituire le f-string con il formato standard di logging:

**Codice attuale (esempio linea 38):**
```python
_logger.info(f"Survey {survey.id} - certification_mode: {survey.certification_mode}, answer_state: {answer.state}")
```

**Codice proposto:**
```python
_logger.info("Survey %s - certification_mode: %s, answer_state: %s", survey.id, survey.certification_mode, answer.state)
```

---

#### [P2/S] Hardcoded URL construction

**File:** `controllers/main.py` linee 64-65
**Stato:** VERIFICATO

**Codice attuale:**
```python
base_url = request.httprequest.url_root.rstrip('/')
survey_url = f"{base_url}/survey/start/{survey.access_token}"
```

**Codice proposto:**
```python
# Utilizzare il metodo get_base_url() di Odoo
base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
survey_url = "%s/survey/start/%s" % (base_url, survey.access_token)
```

**Nota:** Verificare che in Odoo 19 `survey.survey` non abbia un metodo dedicato per generare l'URL di avvio. DA VERIFICARE nella documentazione ufficiale.

---

### 4. Views

#### [P1/S] Verifica xpath su vista survey form

**File:** `views/survey_survey_views.xml` linea 8
**Stato:** DA VERIFICARE

**Codice attuale:**
```xml
<xpath expr="//field[@name='scoring_success_min']/ancestor::group[1]" position="after">
```

**Verifica richiesta:** L'xpath cerca il campo `scoring_success_min` nella vista form del survey. È necessario verificare che:
1. Il campo `scoring_success_min` esista ancora nella vista form di Odoo 19
2. La struttura della vista (group ancestor) non sia cambiata

**Fonte:** Verificare su https://github.com/odoo/odoo/tree/19.0/addons/survey/views per la struttura della vista `survey.survey_survey_view_form`

---

#### [P1/S] Verifica xpath su vista survey_user_input form

**File:** `views/survey_user_input_views.xml` linea 8
**Stato:** DA VERIFICARE

**Codice attuale:**
```xml
<xpath expr="//field[@name='scoring_percentage']" position="after">
```

**Verifica richiesta:** Verificare che il campo `scoring_percentage` esista ancora nella vista form di `survey.user_input` in Odoo 19.

---

#### [P1/S] Verifica template QWeb survey_fill_form_done

**File:** `views/survey_templates.xml` linea 3
**Stato:** DA VERIFICARE

**Codice attuale:**
```xml
<template id="survey_multiple_certification_done" inherit_id="survey.survey_fill_form_done">
    <xpath expr="//h1[@class='fs-2']" position="replace">
```

**Verifica richiesta:**
1. Verificare che il template `survey.survey_fill_form_done` esista ancora in Odoo 19
2. Verificare che contenga un elemento `<h1 class="fs-2">`

**Fonte:** Verificare su https://github.com/odoo/odoo/tree/19.0/addons/survey/views

---

### 5. Security

#### [P2/M] ACL troppo permissive per survey.certification.threshold

**File:** `security/ir.model.access.csv` linea 2
**Stato:** VERIFICATO

**Codice attuale:**
```csv
access_survey_certification_threshold,survey.certification.threshold,model_survey_certification_threshold,base.group_user,1,1,1,1
```

**Analisi:**
- **Scenario legittimo:** Gli utenti devono poter vedere le soglie di certificazione e i manager devono poterle configurare
- **Rischio:** Qualsiasi utente base può creare, modificare ed eliminare soglie di certificazione di qualsiasi survey
- **Principio del minimo privilegio violato:** Write, Create e Unlink dovrebbero essere limitati ai manager dei survey

**Codice proposto:**
```csv
access_survey_certification_threshold_user,survey.certification.threshold user,model_survey_certification_threshold,base.group_user,1,0,0,0
access_survey_certification_threshold_manager,survey.certification.threshold manager,model_survey_certification_threshold,survey.group_survey_manager,1,1,1,1
```

---

#### [P2/M] Record Rules mancanti

**File:** `security/survey_multiple_certification_security.xml`
**Stato:** VERIFICATO

Il file contiene solo un placeholder e non definisce record rules. È necessario aggiungere regole per:

1. **survey.certification.threshold** - Gli utenti dovrebbero vedere solo le soglie dei survey a cui hanno accesso
2. **survey.user_input.history** - Gli utenti dovrebbero vedere solo la propria cronologia

**Codice proposto:**
```xml
<?xml version="1.0"?>
<odoo>
    <!-- Record Rule: Threshold visibili solo per survey accessibili -->
    <record id="survey_certification_threshold_rule" model="ir.rule">
        <field name="name">Certification Threshold: visible if survey is accessible</field>
        <field name="model_id" ref="model_survey_certification_threshold"/>
        <field name="domain_force">[
            '|',
            ('survey_id.user_id', '=', user.id),
            ('survey_id.user_id', '=', False)
        ]</field>
        <field name="groups" eval="[(4, ref('base.group_user'))]"/>
        <field name="perm_read" eval="True"/>
        <field name="perm_write" eval="False"/>
        <field name="perm_create" eval="False"/>
        <field name="perm_unlink" eval="False"/>
    </record>

    <!-- Record Rule: History visibile solo per i propri tentativi -->
    <record id="survey_user_input_history_rule" model="ir.rule">
        <field name="name">User Input History: own attempts only</field>
        <field name="model_id" ref="model_survey_user_input_history"/>
        <field name="domain_force">[('user_input_id.partner_id', '=', user.partner_id.id)]</field>
        <field name="groups" eval="[(4, ref('base.group_user'))]"/>
        <field name="perm_read" eval="True"/>
        <field name="perm_write" eval="False"/>
        <field name="perm_create" eval="False"/>
        <field name="perm_unlink" eval="False"/>
    </record>

    <!-- Manager può vedere tutto -->
    <record id="survey_certification_threshold_manager_rule" model="ir.rule">
        <field name="name">Certification Threshold: manager sees all</field>
        <field name="model_id" ref="model_survey_certification_threshold"/>
        <field name="domain_force">[(1, '=', 1)]</field>
        <field name="groups" eval="[(4, ref('survey.group_survey_manager'))]"/>
    </record>

    <record id="survey_user_input_history_manager_rule" model="ir.rule">
        <field name="name">User Input History: manager sees all</field>
        <field name="model_id" ref="model_survey_user_input_history"/>
        <field name="domain_force">[(1, '=', 1)]</field>
        <field name="groups" eval="[(4, ref('survey.group_survey_manager'))]"/>
    </record>
</odoo>
```

**Nota:** Le record rules proposte sono un esempio e devono essere adattate in base ai requisiti di business specifici. ASSUNZIONE: si assume che il campo `user_id` esista su `survey.survey` in Odoo 19.

---

### 6. Assets

Nessun asset JavaScript o CSS custom presente nel modulo. Non sono richieste modifiche per questa sezione.

---

### 7. Data e Migrations

#### [P3/S] Nessuno script di migrazione necessario

Il modulo non presenta:
- Rinomina di campi o tabelle
- Cambiamenti di tipo di campo
- Rimozione di dati

Non sono necessari script di migrazione openupgradelib.

**Nota:** Se esistono dati di produzione con survey configurati in modalità `multiple`, verificare che i dati vengano preservati durante l'upgrade.

---

### 8. Test

#### [P2/S] Rimozione file di test duplicati dalla root

**File:** `test_can_retake_fix.py`, `test_fix.py`, `test_multiple_certification.py` (nella root del modulo)
**Stato:** VERIFICATO (rilevato da pylint-odoo R0801 duplicate-code)

I file di test sono duplicati sia nella root del modulo che nella cartella `tests/`. Rimuovere i duplicati dalla root.

**Azione:** Eliminare i file dalla root e mantenere solo quelli in `tests/`.

---

#### [P2/S] Test non importati correttamente

**File:** `tests/__init__.py`
**Stato:** VERIFICATO

**Codice attuale:**
```python
# Test module initialization
```

**Codice proposto:**
```python
from . import test_survey_multiple_certification
```

---

#### [P3/S] Modernizzazione dei test

**File:** `tests/test_survey_multiple_certification.py`
**Stato:** VERIFICATO

Il test utilizza `setUp` invece del più moderno `setUpClass` con `@classmethod`. Per Odoo 19 si raccomanda di seguire le nuove convenzioni di testing.

**Codice attuale:**
```python
def setUp(self):
    super().setUp()
    self.Survey = self.env['survey.survey']
    # ...
```

**Codice proposto:**
```python
@classmethod
def setUpClass(cls):
    super().setUpClass()
    cls.Survey = cls.env['survey.survey']
    # ...
```

**Nota:** DA VERIFICARE se Odoo 19 introduce nuove convenzioni per i test. Verificare la documentazione ufficiale su https://www.odoo.com/documentation/19.0/developer/reference/backend/testing.html

---

## SECURITY ANALYSIS

### Modello: survey.certification.threshold

**ACL attuale:**
| Gruppo | Read | Write | Create | Unlink |
|--------|------|-------|--------|--------|
| base.group_user | 1 | 1 | 1 | 1 |

**Scenario di uso legittimo:**
- Un Survey Manager crea un survey con certificazione e configura le soglie
- Gli utenti completano il survey e vedono la soglia raggiunta

**Rischi identificati:**
1. Qualsiasi utente autenticato può modificare le soglie di certificazione, invalidando potenzialmente certificazioni già assegnate
2. Nessun controllo multi-company se il modulo viene usato in ambiente multi-azienda
3. Nessuna verifica che l'utente abbia accesso al survey collegato

**ACL proposta:**
| Gruppo | Read | Write | Create | Unlink |
|--------|------|-------|--------|--------|
| base.group_user | 1 | 0 | 0 | 0 |
| survey.group_survey_manager | 1 | 1 | 1 | 1 |

**Giustificazione permessi:**
- **Read per tutti:** Necessario per visualizzare le soglie di certificazione
- **Write/Create/Unlink per manager:** Solo chi gestisce i survey dovrebbe poter configurare le soglie

---

### Modello: survey.user_input.history

**ACL attuale:**
| Gruppo | Read | Write | Create | Unlink |
|--------|------|-------|--------|--------|
| base.group_user | 1 | 0 | 0 | 0 |

**Analisi:** L'ACL è corretta. Gli utenti possono solo leggere ma non modificare la cronologia.

**Record Rule necessaria:** Aggiungere una regola per limitare la visibilità alla propria cronologia (vedi sezione Security sopra).

---

### Modelli Wizard: survey.threshold.wizard e survey.threshold.wizard.line

**ACL attuale:**
| Gruppo | Read | Write | Create | Unlink |
|--------|------|-------|--------|--------|
| base.group_user | 1 | 1 | 1 | 1 |

**Analisi:** Per i modelli TransientModel (wizard), permessi pieni sono generalmente accettabili perché i record sono temporanei. Tuttavia, si raccomanda di limitare l'accesso ai Survey Manager.

**ACL proposta:**
| Gruppo | Read | Write | Create | Unlink |
|--------|------|-------|--------|--------|
| survey.group_survey_manager | 1 | 1 | 1 | 1 |

---

### Casi Edge verificati

| Caso | Copertura | Note |
|------|-----------|------|
| Record con relazioni NULL | NO | Aggiungere controllo su threshold_reached_id=False |
| Contesto multi-company | NO | Il modulo non gestisce company_id |
| Utenti senza employee | OK | Non applicabile per questo modulo |
| Record creati da altri utenti | NO | Mancano record rules |

---

## ACCEPTANCE CRITERIA

### Criteri di accettazione per la migrazione

- [ ] **AC1:** Il modulo si installa correttamente su un database Odoo 19 pulito senza errori
- [ ] **AC2:** Creare un survey con `certification_mode='multiple'` e configurare almeno 3 soglie (es. 0-60%, 60-80%, 80-100%)
- [ ] **AC3:** Completare il survey con un punteggio del 75% e verificare che venga assegnata la soglia corretta (60-80%)
- [ ] **AC4:** Verificare che la pagina di completamento mostri il messaggio personalizzato con il nome della soglia raggiunta
- [ ] **AC5:** Verificare che la cronologia dei tentativi venga registrata correttamente nel record `survey.user_input`
- [ ] **AC6:** Verificare che il wizard di configurazione soglie funzioni correttamente creando le soglie sul survey
- [ ] **AC7:** Verificare che un utente non manager non possa modificare le soglie di certificazione (dopo applicazione delle ACL proposte)
- [ ] **AC8:** Eseguire la test suite con `./odoo-bin -d test_db --test-enable -i survey_multiple_certification --stop-after-init` senza errori
- [ ] **AC9:** Verificare che i survey esistenti con `certification_mode='single'` continuino a funzionare normalmente

---

## FONTI E RIFERIMENTI

### Documentazione ufficiale Odoo 19

- [Surveys - Odoo 19.0 Documentation](https://www.odoo.com/documentation/19.0/applications/marketing/surveys.html) - Documentazione funzionale del modulo Survey
- [CRM Gamification - Odoo 19.0 Documentation](https://www.odoo.com/documentation/19.0/applications/sales/crm/optimize/gamification.html) - Documentazione del modulo Gamification
- [Web Controllers - Odoo 19.0 Documentation](https://www.odoo.com/documentation/19.0/developer/reference/backend/http.html) - Riferimento per i controller HTTP
- [Odoo 19 Release Notes](https://www.odoo.com/odoo-19-release-notes) - Note di rilascio ufficiali

### Guide di migrazione

- [How to Migrate from Odoo 18 to Odoo 19 - Ksolves](https://www.ksolves.com/blog/odoo/how-to-migrate-from-odoo-18-to-odoo-19-step-by-step-guide) - Guida step-by-step per la migrazione
- [OCA OpenUpgrade - GitHub](https://github.com/OCA/OpenUpgrade) - Progetto OCA per la migrazione open source

### Breaking Changes documentati

| Cambiamento | Fonte | Verifica |
|-------------|-------|----------|
| `type='json'` → `type='jsonrpc'` per controller | [Ksolves Migration Guide](https://www.ksolves.com/blog/odoo/how-to-migrate-from-odoo-18-to-odoo-19-step-by-step-guide) | Non applicabile - il modulo usa solo `type='http'` |
| `from odoo import registry` → `from odoo.modules.registry import Registry` | [Ksolves Migration Guide](https://www.ksolves.com/blog/odoo/how-to-migrate-from-odoo-18-to-odoo-19-step-by-step-guide) | Non applicabile - il modulo non importa registry |

### Tool di analisi utilizzati

| Tool | Versione | Output |
|------|----------|--------|
| pylint-odoo | 10.0.0 | Rating 2.38/10 - 157 issues rilevati |
| odoo-module-migrator | 0.5.0 | Non supporta target v19 (max v18) |

---

## RIEPILOGO MODIFICHE PER PRIORITÀ

### P0 - Bloccanti (1)
1. Aggiornamento versione manifest

### P1 - Critici (5)
1. Verifica compatibilità _compute_scoring_success override
2. Rimozione print() dal controller
3. Verifica compatibilità route override
4. Verifica xpath vista survey form
5. Verifica template QWeb survey_fill_form_done

### P2 - Importanti (8)
1. Rimozione f-string per logging nei models
2. Aggiunta @api.depends mancante
3. Utilizzo f-string nel controller
4. Hardcoded URL construction
5. ACL troppo permissive
6. Record Rules mancanti
7. Rimozione file test duplicati
8. Test non importati correttamente

### P3 - Miglioramenti (5)
1. Rimozione chiavi superflue dal manifest
2. Correzione URL website
3. Rimozione description deprecata
4. Modernizzazione test con setUpClass
5. Aggiunta index ai campi Many2one

---

## EFFORT TOTALE STIMATO

| Priorità | Count | Effort stimato |
|----------|-------|----------------|
| P0 | 1 | XS (< 30 min) |
| P1 | 5 | M (2-8 ore) - principalmente per le verifiche |
| P2 | 8 | S-M (2-4 ore) |
| P3 | 5 | XS-S (1-2 ore) |

**Totale:** 1-2 giorni lavorativi (size **M**), di cui circa il 50% dedicato a verifiche di compatibilità con il codice sorgente Odoo 19.

---

*Documento generato automaticamente - Revisione manuale raccomandata prima dell'implementazione*
