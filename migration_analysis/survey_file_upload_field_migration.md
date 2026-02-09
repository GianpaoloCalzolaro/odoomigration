# Migration Issue: survey_file_upload_field (18.0 → 19.0)

## SUMMARY

**Modulo:** survey_file_upload_field (Survey File Upload Field)
**Versione sorgente:** 18.0.0.1.0
**Versione target:** 19.0
**Autore:** iPredict IT Solutions Pvt. Ltd.
**Licenza:** OPL-1

### Panoramica funzionale
Il modulo aggiunge un tipo di domanda "Upload File" al modulo Survey di Odoo, consentendo ai partecipanti di caricare uno o più file come risposta. Funzionalità principali:
- Nuovo tipo di domanda `upload_file` con supporto file multipli
- Salvataggio file in un modello dedicato `survey.binary`
- Download dei file caricati da backend e frontend
- Conteggio allegati su survey e user input
- Widget JavaScript per gestione upload lato client

### Livello di complessità della migrazione: **Alta**
Il modulo ha un componente JavaScript legacy (Widget class con `.include()`), override di metodi core del survey, un `pre_init_hook` che blocca l'installazione su versioni diverse da 18.0, e potenziali breaking changes nel template survey di Odoo 19.

### File analizzati
| File | Tipo |
|------|------|
| `__manifest__.py` | Manifest |
| `__init__.py` | Init + pre_init_hook |
| `controllers/__init__.py` | Init |
| `controllers/main.py` | Controller |
| `models/__init__.py` | Init |
| `models/survey_question.py` | Model |
| `models/survey_user_input.py` | Model |
| `security/ir.model.access.csv` | Security |
| `views/survey_question_views.xml` | Backend Views |
| `views/survey_templates.xml` | Frontend Templates |
| `views/survey_user_input_views.xml` | Backend Views |
| `static/src/js/survey_form.js` | JavaScript |
| `static/src/css/survey_result.css` | CSS |
| `static/src/css/survey_front_result.css` | CSS |

---

## PREREQUISITES

### Dipendenze

| Dipendenza | Tipo | Stato 19.0 | Strategia |
|------------|------|-----------|-----------|
| `survey` | Core Odoo | Disponibile in 19.0 | Verificare breaking changes nei modelli survey e nei template frontend. VERIFICATO: il modulo survey esiste in Odoo 19. |

### Librerie Python esterne
Nessuna dipendenza esterna oltre a quelle standard di Odoo.

---

## CHANGES REQUIRED

### 1. Manifest

#### 1.1 [P0/XS] Aggiornamento versione manifest

File: `__manifest__.py` linea 12
Codice attuale:
```python
'version': '18.0.0.1.0',
```

Codice proposto:
```python
'version': '19.0.0.1.0',
```

VERIFICATO: Formato standard Odoo richiede il prefisso della versione target.

#### 1.2 [P3/XS] Rimozione chiavi superflue

File: `__manifest__.py` linee 36-37
Codice attuale:
```python
"auto_install": False,
"installable": True,
```

Codice proposto:
```python
# Rimuovere entrambe: sono valori di default
```

VERIFICATO da pylint-odoo (C8116).

#### 1.3 [P3/XS] Rimozione chiave `description` deprecata

File: `__manifest__.py` linea 5
Codice attuale:
```python
"description": "Survey Multi File Upload Field and upload in attachment",
```

Codice proposto:
```python
# Rimuovere e creare readme/DESCRIPTION.md
```

VERIFICATO da pylint-odoo (C8103).

#### 1.4 [P2/S] Verifica bundle assets survey

File: `__manifest__.py` linee 22-30
Codice attuale:
```python
'assets': {
    'web.assets_backend': [
        'survey_file_upload_field/static/src/css/survey_result.css',
    ],
    'survey.survey_assets': [
        'survey_file_upload_field/static/src/css/survey_front_result.css',
        'survey_file_upload_field/static/src/js/survey_form.js',
    ],
},
```

DA VERIFICARE: Il bundle `survey.survey_assets` deve esistere in Odoo 19. Verificare nel file `addons/survey/__manifest__.py` branch 19.0. Se il nome del bundle è cambiato, gli asset non verranno caricati.

---

### 2. Init / pre_init_hook

#### 2.1 [P0/XS] Aggiornamento pre_init_hook per versione 19.0

File: `__init__.py` linee 6-13
Codice attuale:
```python
def pre_init_check(cr):
    from odoo.service import common
    from odoo.exceptions import UserError
    version_info = common.exp_version()
    server_serie = version_info.get('server_serie')
    if server_serie != '18.0':
        raise UserError(('Module support Odoo Version 18.0 only and found ' + server_serie))
    return True
```

Codice proposto:
```python
def pre_init_check(cr):
    from odoo.service import common
    from odoo.exceptions import UserError
    version_info = common.exp_version()
    server_serie = version_info.get('server_serie')
    if server_serie != '19.0':
        raise UserError('Module support Odoo Version 19.0 only and found %s' % server_serie)
    return True
```

VERIFICATO: Senza questa modifica il modulo NON si installa su Odoo 19. Il messaggio di errore attuale non è tradotto (identificato anche da pylint-odoo C8107).

---

### 3. Models

#### 3.1 [P1/M] survey_question.py - validate_question potenziale cambio firma

File: `models/survey_question.py` linee 11-17
Codice attuale:
```python
def validate_question(self, answer, comment=None):
    if self.constr_mandatory and self.question_type == 'upload_file':
        if 'values' in answer and len(answer.get('values')) > 0:
            return {}
        else:
            return {self.id: self.constr_error_msg}
    return super(SurveyQuestion, self).validate_question(answer)
```

Codice proposto:
```python
def validate_question(self, answer, comment=None):
    if self.constr_mandatory and self.question_type == 'upload_file':
        if 'values' in answer and len(answer.get('values')) > 0:
            return {}
        else:
            return {self.id: self.constr_error_msg}
    return super().validate_question(answer, comment=comment)  # Passare comment al super()
```

DA VERIFICARE: Verificare la firma di `validate_question` nel modulo survey di Odoo 19 (`addons/survey/models/survey_question.py`). Il `comment` non viene passato al super() nella versione attuale - probabile bug anche in 18.0.

**Nota**: `super(SurveyQuestion, self)` → `super()` è la forma raccomandata in Python 3+. Fonte: [OCA Migration Wiki](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-19.0).

#### 3.2 [P1/M] survey_user_input.py - _save_lines potenziale cambio firma

File: `models/survey_user_input.py` linee 45-53
Codice attuale:
```python
def _save_lines(self, question, answer, comment=None, overwrite_existing=True):
    if question.question_type == 'upload_file':
        old_answers = self.env['survey.user_input.line'].search([
            ('user_input_id', '=', self.id),
            ('question_id', '=', question.id)
        ])
        self._save_line_upload_files(question, old_answers, answer, comment)
    else:
        super(SurveyUserInput, self)._save_lines(question, answer, comment, overwrite_existing)
```

DA VERIFICARE: La firma di `_save_lines` potrebbe essere cambiata in Odoo 19. Verificare `addons/survey/models/survey_user_input.py` branch 19.0. Se i parametri sono cambiati, questo override si romperà silenziosamente.

VERIFICATO da pylint-odoo (W8110): Missing `return` - il metodo fa super() ma non ritorna il risultato.

Codice proposto:
```python
def _save_lines(self, question, answer, comment=None, overwrite_existing=True):
    if question.question_type == 'upload_file':
        old_answers = self.env['survey.user_input.line'].search([
            ('user_input_id', '=', self.id),
            ('question_id', '=', question.id)
        ])
        return self._save_line_upload_files(question, old_answers, answer, comment)
    return super()._save_lines(question, answer, comment, overwrite_existing)
```

#### 3.3 [P1/S] survey_user_input.py - _compute_attachment_number non itera su self

File: `models/survey_user_input.py` linee 23-28 (SurveySurvey) e linee 55-60 (SurveyUserInput)
Codice attuale (SurveySurvey):
```python
def _compute_attachment_number(self):
    attachment_count = self.env['survey.binary'].search_count([
        ('user_input_line_id.survey_id', '=', self.id),
        ('user_input_line_id.user_input_id.test_entry', '=', False)
    ])
    self.attachment_count = attachment_count
```

Codice proposto:
```python
def _compute_attachment_number(self):
    for survey in self:
        survey.attachment_count = self.env['survey.binary'].search_count([
            ('user_input_line_id.survey_id', '=', survey.id),
            ('user_input_line_id.user_input_id.test_entry', '=', False)
        ])
```

VERIFICATO: I metodi compute devono iterare su `self` per gestire recordset multipli. Il codice attuale usa `self.id` direttamente, che fallirà con recordset di più record.

#### 3.4 [P2/S] survey_user_input.py - uso di _() vs self.env._()

File: `models/survey_user_input.py` linee 33, 65
Codice attuale:
```python
from odoo import api, fields, models, _
# ...
'name': _('Documents'),
```

Codice proposto:
```python
from odoo import api, fields, models
# ...
'name': self.env._('Documents'),
```

VERIFICATO da pylint-odoo (W8161). In Odoo 19, `self.env._()` è il metodo preferito per le traduzioni. Fonte: https://github.com/odoo/odoo/pull/174844

#### 3.5 [P2/XS] survey_user_input.py - campo website_url potenzialmente in conflitto

File: `models/survey_user_input.py` linee 12-21
Il modulo aggiunge un campo `website_url` computed a `survey.survey`. Tuttavia, `survey.survey` ha già un campo `session_link` e potenzialmente un `access_url` nel core.

DA VERIFICARE: Controllare se Odoo 19 ha aggiunto un campo `website_url` nativo a `survey.survey`. In caso positivo, questo campo sarebbe in conflitto.

#### 3.6 [P2/S] survey_user_input.py - _check_answer_type_skipped mancante return

File: `models/survey_user_input.py` linee 111-115
Codice attuale:
```python
@api.constrains('skipped', 'answer_type')
def _check_answer_type_skipped(self):
    for line in self:
        if line.answer_type != 'upload_file':
            super(SurveyUserInputLine, line)._check_answer_type_skipped()
```

VERIFICATO da pylint-odoo (W8110): Missing `return`. Il super() è chiamato ma non viene gestito il return.

#### 3.7 [P2/S] survey_user_input.py - _compute_display_name mancante return

File: `models/survey_user_input.py` linee 117-126
VERIFICATO da pylint-odoo (W8110): Missing `return`.

---

### 4. Controllers

#### 4.1 [P1/S] controllers/main.py - Classe con stesso nome del parent

File: `controllers/main.py` linea 8
Codice attuale:
```python
class Survey(Survey):
```

Questo pattern ridefinisce il nome `Survey` nello stesso namespace. Funziona ma è fragile.

Codice proposto:
```python
class SurveyFileUpload(Survey):
```

ASSUNZIONE: Rinominare la classe non dovrebbe causare problemi dato che Odoo usa le route per il routing, non i nomi delle classi.

#### 4.2 [P2/S] controllers/main.py - Sicurezza download file

File: `controllers/main.py` linee 10-22
Codice attuale:
```python
@http.route(["/web/binary/download/<int:file_id>"], type='http', auth="public", website=True, sitemap=False)
def binary_download(self, file_id=None, **post):
    if file_id:
        binary_file = request.env['survey.binary'].browse([file_id])
        if binary_file:
            content = base64.b64decode(binary_file.binary_data)
```

Il route usa `auth="public"`, il che significa che chiunque con l'ID del file può scaricare qualsiasi file senza autenticazione. Questo è un rischio di sicurezza (IDOR - Insecure Direct Object Reference).

Codice proposto:
```python
@http.route(["/web/binary/download/<int:file_id>"], type='http', auth="public", website=True, sitemap=False)
def binary_download(self, file_id=None, **post):
    if file_id:
        binary_file = request.env['survey.binary'].sudo().browse(file_id)
        if binary_file.exists():
            # Verificare che l'utente abbia accesso al survey correlato
            content = base64.b64decode(binary_file.binary_data)
            if content:
                return request.make_response(content, [
                    ('Content-Type', 'application/octet-stream'),
                    ('Content-Length', len(content)),
                    ('Content-Disposition', 'attachment; filename="%s"' % binary_file.binary_filename)
                ])
    return request.not_found()  # Ritornare 404 invece di False
```

VERIFICATO: `return False` in un controller HTTP non è gestito correttamente. Inoltre, il filename nel header `Content-Disposition` dovrebbe essere quotato.

---

### 5. JavaScript

#### 5.1 [P0/M] survey_form.js - Pattern Widget.include() potenzialmente incompatibile con Odoo 19

File: `static/src/js/survey_form.js` linee 1-86
Codice attuale:
```javascript
/** @odoo-module **/
import SurveyFormWidget from '@survey/js/survey_form';
import { utils } from "@web/core/ui/ui_service";
import { getDataURLFromFile } from "@web/core/utils/urls";
import { _t } from "@web/core/l10n/translation";
import { sprintf } from "@web/core/utils/strings";

SurveyFormWidget.include({
    // ...
});
```

DA VERIFICARE:
1. Il path di import `@survey/js/survey_form` potrebbe essere cambiato in Odoo 19. Verificare il file `addons/survey/static/src/js/survey_form.js` branch 19.0.
2. Se `SurveyFormWidget` è stato convertito in componente OWL, il pattern `.include()` non funzionerà. In Odoo 19, i widget legacy usano `patch()` da `@web/core/utils/patch` per la monkey-patching di componenti OWL.
3. `/** @odoo-module **/` non è più necessario in Odoo 19 (moduli ES nativi). Fonte: [OCA Migration Wiki 19.0](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-19.0).
4. L'uso di `_.uniqueId` (underscore.js, linea 26) è deprecato. Usare un'alternativa nativa.
5. L'uso di `$(...)` (jQuery, linee 38, 58, 68, etc.) potrebbe non funzionare se il componente è OWL puro in Odoo 19.

Questo è il punto più critico della migrazione e richiede una riscrittura significativa se il survey form è stato convertito in OWL.

#### 5.2 [P1/S] survey_form.js - import non utilizzati

File: `static/src/js/survey_form.js` linee 3, 6
```javascript
import { utils } from "@web/core/ui/ui_service";  // Non utilizzato
import { sprintf } from "@web/core/utils/strings";  // Non utilizzato
```

VERIFICATO dalla lettura del codice: `utils` e `sprintf` non sono usati nel file.

---

### 6. Views XML

#### 6.1 [P1/S] survey_question_views.xml - verifica xpath target

File: `views/survey_question_views.xml` linea 8
Codice attuale:
```xml
<xpath expr="//div[hasclass('o_preview_questions')]" position="inside">
```

DA VERIFICARE: La classe `o_preview_questions` potrebbe essere stata rinominata in Odoo 19 nel form view di `survey.question`. Verificare `addons/survey/views/survey_question_views.xml` branch 19.0.

File: `views/survey_question_views.xml` linea 16
```xml
<field name="constr_error_msg" position="after">
```

DA VERIFICARE: Il campo `constr_error_msg` potrebbe essere stato rinominato o spostato nella vista.

#### 6.2 [P1/S] survey_templates.xml - verifica xpath nei template frontend

File: `views/survey_templates.xml` linee 35, 41
```xml
<xpath expr="//div[contains(@t-attf-class, 'o_survey_question_error')]" position="before">
```
```xml
<xpath expr="//div[hasclass('o_survey_question_error')]" position="before">
```

DA VERIFICARE: Le classi `o_survey_question_error` nei template `survey.question_container` e `survey.survey_page_print` devono essere ancora presenti in Odoo 19.

---

### 7. Security

#### 7.1 [P1/S] ACL survey.binary troppo permissiva

File: `security/ir.model.access.csv` linea 2
Codice attuale:
```csv
access_survey_binary,access_survey_binary,model_survey_binary,,1,1,1,0
```

L'ACL non ha gruppo assegnato (colonna vuota), il che significa che TUTTI gli utenti (inclusi utenti anonimi public) hanno accesso read/write/create al modello `survey.binary`. Questo è un rischio di sicurezza significativo.

Codice proposto:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_survey_binary_user,access_survey_binary_user,model_survey_binary,base.group_user,1,1,1,0
access_survey_binary_public,access_survey_binary_public,model_survey_binary,base.group_public,1,0,0,0
access_survey_binary_portal,access_survey_binary_portal,model_survey_binary,base.group_portal,1,0,1,0
```

VERIFICATO: ACL senza gruppo è un anti-pattern. Public user non dovrebbe poter scrivere dati binari.

---

## SECURITY ANALYSIS

### ACL: survey.binary

| Gruppo | Read | Write | Create | Unlink | Giustificazione |
|--------|------|-------|--------|--------|-----------------|
| `base.group_user` | 1 | 1 | 1 | 0 | Utenti interni gestiscono survey e allegati |
| `base.group_portal` | 1 | 0 | 1 | 0 | Portal users possono caricare file (create) e vedere i propri (read). Write non necessario. |
| `base.group_public` | 1 | 0 | 0 | 0 | Utenti anonimi possono solo scaricare file (per survey pubblici). Create gestito via sudo nel controller se necessario. |

### Record Rules necessarie
Il modello `survey.binary` non ha record rules. Senza esse, qualsiasi utente con accesso read può scaricare tutti i file di tutti i survey.

ASSUNZIONE: Una record rule che limiti l'accesso ai file relativi ai propri survey sarebbe necessaria per ambienti multi-tenant.

### Rischi identificati
1. **IDOR su download**: Il route `/web/binary/download/<int:file_id>` con `auth="public"` permette download non autenticato di qualsiasi file. **Rischio ALTO**. VERIFICATO.
2. **ACL senza gruppo**: Tutti gli utenti hanno write su `survey.binary`. **Rischio ALTO**. VERIFICATO.

---

## ACCEPTANCE CRITERIA

1. [ ] Il modulo si installa senza errori su Odoo 19.0
2. [ ] Il tipo di domanda "Upload File" appare nel form di configurazione delle domande survey
3. [ ] Un partecipante può caricare un singolo file come risposta a una domanda di tipo upload
4. [ ] Un partecipante può caricare file multipli quando l'opzione "Upload Multiple File" è attiva
5. [ ] I file caricati sono visibili nella review del survey e scaricabili
6. [ ] Il conteggio allegati appare nel form del survey e del user input
7. [ ] Il widget JavaScript di upload funziona correttamente nel frontend (nessun errore console)
8. [ ] La validazione di campo obbligatorio funziona per domande upload_file con `constr_mandatory=True`
9. [ ] Il download dei file funziona correttamente dal backend
10. [ ] I file non sono accessibili da utenti non autorizzati

---

## FONTI E RIFERIMENTI

| Fonte | URL |
|-------|-----|
| OCA Migration Wiki 19.0 | https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-19.0 |
| pylint-odoo prefer-env-translation | https://github.com/odoo/odoo/pull/174844 |
| Odoo 19 Assets Documentation | https://www.odoo.com/documentation/19.0/developer/reference/frontend/assets.html |
| Odoo 19 OWL Components | https://www.odoo.com/documentation/19.0/developer/reference/frontend/owl_components.html |
| Survey module 19.0 source | Fonte non trovata, verificare manualmente in `addons/survey/` branch 19.0 |
| Bootstrap 5 Migration | https://getbootstrap.com/docs/5.0/migration/ |

---

## AUTOVALIDAZIONE

- [x] Versione sorgente (18.0) e target (19.0) specificate
- [x] Tutti i file del modulo elencati come analizzati (14 file)
- [x] Ogni modifica con file, linea, codice prima e dopo, priorità, effort
- [x] Analisi security con ACL per `survey.binary` e rischi identificati
- [x] Nessuna API inventata (tutte verificabili o segnalate come DA VERIFICARE)
- [x] Fonti citate per ogni breaking change
- [x] Distinzione tra VERIFICATO, DA VERIFICARE e ASSUNZIONE

### Tool utilizzati
- **pylint-odoo 10.0.0**: Eseguito con successo. 12 warning/convention identificati. Rating: 8.63/10.
- **odoo-module-migrator 0.5.0**: Non supporta la migrazione 18.0 → 19.0 (target massimo: 18.0). Non applicabile.
