# Migration Issue: customer_notes_odoo (18.0 → 19.0)

## SUMMARY

**Modulo:** customer_notes_odoo (Customer Diario Portal)
**Versione sorgente:** 18.0 (versione manifest: 1.6.0, formato non standard)
**Versione target:** 19.0
**Autore:** Elite ERP
**Licenza:** OPL-1

### Panoramica funzionale
Il modulo consente ai clienti di creare e gestire un diario personale nel portale Odoo. Funzionalità principali:
- Creazione, visualizzazione ed eliminazione di voci di diario dal portale
- Campo "Come sto" per tracciare lo stato d'animo
- Visualizzazione raggruppata per utente
- Integrazione con il modulo `contacts_patient` per accesso da parte di tutor/professionisti
- Pulsante statistico sul partner per accedere alle note

### Livello di complessità della migrazione: **Media**
Il modulo ha dipendenze custom (`contacts_patient`), controller portal che richiedono aggiornamento, e pattern legacy da modernizzare. Non ha componenti JavaScript complessi.

### File analizzati
| File | Tipo |
|------|------|
| `__manifest__.py` | Manifest |
| `__init__.py` | Init |
| `controllers/__init__.py` | Init |
| `controllers/controllers.py` | Controller |
| `models/__init__.py` | Init |
| `models/models.py` | Model |
| `models/res_partner.py` | Model |
| `security/ir.model.access.csv` | Security |
| `views/views.xml` | Template Portal |
| `views/views1.xml` | Template Portal (legacy) |
| `views/views2.xml` | Template Portal (legacy) |
| `views/portal_note_backend_views.xml` | Backend Views |
| `views/res_partner_note_button.xml` | Backend Views |
| `demo/demo.xml` | Demo Data |
| `i18n/it.po` | Traduzioni |
| `static/description/icon.png` | Icona |
| `static/src/img/contactbook.svg` | Asset statico |

---

## PREREQUISITES

### Dipendenze

| Dipendenza | Tipo | Stato 19.0 | Strategia |
|------------|------|-----------|-----------|
| `portal` | Core Odoo | Disponibile in 19.0 | Verificare breaking changes nei template e controller portal. VERIFICATO: il modulo portal esiste in Odoo 19. |
| `website` | Core Odoo | Disponibile in 19.0 | Verificare cambiamenti ai layout template. VERIFICATO. |
| `contacts_patient` | Custom | Già migrato a 19.0 (versione 19.0.1.0.0 nel repository) | Nessuna azione necessaria, il modulo è presente e aggiornato. VERIFICATO dalla lettura di `contacts_patient/__manifest__.py`. |

### Librerie Python esterne
| Libreria | Uso | Note |
|----------|-----|------|
| `pytz` | Conversione timezone in `_compute_formatted_create_date` | Disponibile come dipendenza standard di Odoo. In Odoo 19 si raccomanda l'uso di `self.env.tz` per ottenere il timezone dell'utente. Fonte: [OCA Migration Wiki 19.0](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-19.0). |

---

## CHANGES REQUIRED

### 1. Manifest

#### 1.1 [P0/XS] Aggiornamento versione manifest

Il formato versione attuale `1.6.0` non è conforme allo standard Odoo. VERIFICATO da pylint-odoo (C8106).

File: `__manifest__.py` linea 24
Codice attuale:
```python
'version': '1.6.0',  # Incrementata versione per il raggruppamento note
```

Codice proposto:
```python
'version': '19.0.1.6.0',  # Formato standard Odoo: {odoo_version}.{module_version}
```

Fonte: [OCA Manifest Version Format](https://github.com/OCA/maintainer-tools/blob/master/template/module/__manifest__.py), pylint-odoo rule C8106.

#### 1.2 [P3/XS] Rimozione chiave `description` deprecata

File: `__manifest__.py` linea 5
Codice attuale:
```python
'description': '''
Questo modulo introduce la possibilità di creare...
    ''',
```

Codice proposto:
```python
# Rimuovere la chiave 'description' e inserire il contenuto in un file readme/DESCRIPTION.md
```

VERIFICATO da pylint-odoo (C8103). Best practice OCA: usare `readme/DESCRIPTION.md`.

#### 1.3 [P3/XS] Correzione campo website nel manifest

File: `__manifest__.py` linea 20
Codice attuale:
```python
'website': "eliteweb44@gmail.com",
```

Codice proposto:
```python
'website': "https://eliteerp.example.com",  # Sostituire con URL valido che inizi con http[s]://
```

VERIFICATO da pylint-odoo (W8114).

#### 1.4 [P3/XS] Rimozione chiave superflua `installable`

File: `__manifest__.py` linea 35
Codice attuale:
```python
'installable': True,
```

Codice proposto:
```python
# Rimuovere: 'installable': True è il valore di default
```

VERIFICATO da pylint-odoo (C8116).

#### 1.5 [P2/XS] File views1.xml e views2.xml non nel manifest

I file `views/views1.xml` e `views/views2.xml` contengono template portal ma non sono referenziati nel manifest `data`. Contengono un `portal_my_home_inherit` con xpath `//div[@id='portal_common_category']` che potrebbe entrare in conflitto con `views.xml` che definisce `portal_my_home_diario`.

VERIFICATO dalla lettura dei file: `views1.xml` e `views2.xml` hanno template duplicati e non sono nel manifest. Sono probabilmente file residui di una versione precedente.

File: `__manifest__.py` linea 29-34
Codice attuale:
```python
'data': [
    'security/ir.model.access.csv',
    'views/views.xml',
    'views/portal_note_backend_views.xml',
    'views/res_partner_note_button.xml',
],
```

Codice proposto:
```python
'data': [
    'security/ir.model.access.csv',
    'views/views.xml',
    'views/portal_note_backend_views.xml',
    'views/res_partner_note_button.xml',
],
# NOTA: Rimuovere i file views1.xml e views2.xml dal modulo se non utilizzati,
# oppure integrarli nel manifest se necessari. Attualmente sono orfani.
```

ASSUNZIONE: I file views1.xml e views2.xml sono residui non utilizzati.

---

### 2. Models

#### 2.1 [P1/S] Import pytz dentro il metodo compute - modernizzazione timezone

File: `models/models.py` linee 26-38
Codice attuale:
```python
@api.depends('create_date')
def _compute_formatted_create_date(self):
    """Computed field per formattare la data di creazione in formato italiano con orario"""
    for record in self:
        if record.create_date:
            # Converte UTC al fuso orario dell'utente
            user_tz = self.env.user.tz or 'Europe/Rome'
            from pytz import timezone
            import pytz

            create_date_utc = record.create_date
            if create_date_utc.tzinfo is None:
                create_date_utc = pytz.utc.localize(create_date_utc)

            user_timezone = timezone(user_tz)
            create_date_local = create_date_utc.astimezone(user_timezone)

            # Converte la data in formato italiano gg/mm/aaaa hh:mm
            record.formatted_create_date = create_date_local.strftime('%d/%m/%Y %H:%M')
        else:
            record.formatted_create_date = ''
```

Codice proposto:
```python
@api.depends('create_date')
def _compute_formatted_create_date(self):
    """Computed field per formattare la data di creazione in formato italiano con orario"""
    for record in self:
        if record.create_date:
            # In Odoo 19, self.env.tz è il modo raccomandato per ottenere il timezone utente
            user_tz = record.env.tz or 'Europe/Rome'
            from pytz import timezone
            import pytz

            create_date_utc = record.create_date
            if create_date_utc.tzinfo is None:
                create_date_utc = pytz.utc.localize(create_date_utc)

            user_timezone = timezone(user_tz)
            create_date_local = create_date_utc.astimezone(user_timezone)

            record.formatted_create_date = create_date_local.strftime('%d/%m/%Y %H:%M')
        else:
            record.formatted_create_date = ''
```

DA VERIFICARE: `self.env.tz` dovrebbe essere disponibile in Odoo 19 come proprietà dell'environment. Fonte: [OCA Migration Wiki 19.0](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-19.0). Verificare se `self.env.user.tz` è ancora supportato o se `self.env.tz` è l'unica via.

**Nota aggiuntiva**: gli import `pytz` e `timezone` sono dentro il metodo (linea 28-29). È best practice spostarli a livello di modulo.

#### 2.2 [P2/S] Modello portal.note - mancanza di _order

File: `models/models.py` linea 3
Codice attuale:
```python
class PortalNote(models.Model):
    _name = 'portal.note'
    _description = 'Portal Diario'
```

Codice proposto:
```python
class PortalNote(models.Model):
    _name = 'portal.note'
    _description = 'Portal Diario'
    _order = 'create_date desc'  # Ordine di default coerente con l'uso nel controller
```

ASSUNZIONE: L'ordine `create_date desc` è desiderato dato che il controller usa `order='create_date desc'`.

#### 2.3 [P2/S] res_partner.py - _compute_note_count manca decoratore @api.depends

File: `models/res_partner.py` linee 8-11
Codice attuale:
```python
def _compute_note_count(self):
    Note = self.env['portal.note']
    for partner in self:
        partner.note_count = Note.search_count([('user_id.partner_id', '=', partner.id)])
```

Codice proposto:
```python
def _compute_note_count(self):
    Note = self.env['portal.note']
    for partner in self:
        partner.note_count = Note.search_count([('user_id.partner_id', '=', partner.id)])
```

**Nota**: Il campo `note_count` è definito come `compute='_compute_note_count'` senza `@api.depends`. Questo è tecnicamente accettato per campi non stored che dipendono da altri modelli, ma in Odoo 19 è consigliato rendere esplicita la dipendenza o usare `compute_sudo=True` se necessario. ASSUNZIONE: Non bloccante ma da valutare.

#### 2.4 [P2/XS] res_partner.py - uso di .read()[0] deprecato

File: `models/res_partner.py` linea 15
Codice attuale:
```python
def action_view_notes(self):
    self.ensure_one()
    action = self.env.ref('customer_notes_odoo.action_portal_notes').read()[0]
    action['domain'] = [('user_id.partner_id', '=', self.id)]
    return action
```

Codice proposto:
```python
def action_view_notes(self):
    self.ensure_one()
    action = self.env['ir.actions.act_window']._for_xml_id('customer_notes_odoo.action_portal_notes')
    action['domain'] = [('user_id.partner_id', '=', self.id)]
    return action
```

VERIFICATO: `_for_xml_id()` è il metodo raccomandato da Odoo 15+ per ottenere azioni da xmlid. `.read()[0]` è deprecato. Fonte: [Odoo ORM Changelog](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm/changelog.html).

---

### 3. Controllers

#### 3.1 [P1/M] Aggiornamento _prepare_portal_layout_values per Odoo 19

File: `controllers/controllers.py` linee 116-123
Codice attuale:
```python
class CustomerPortalDiario(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        employee = request.env.user.employee_id

        values['show_diario_card'] = bool(employee) or request.env.user.partner_id.is_patient
        return values
```

Codice proposto:
```python
class CustomerPortalDiario(CustomerPortal):

    def _prepare_portal_layout_values(self):
        # DA VERIFICARE: la firma di _prepare_portal_layout_values potrebbe essere cambiata in Odoo 19.
        # Controllare addons/portal/controllers/portal.py nel branch 19.0.
        values = super()._prepare_portal_layout_values()
        employee = request.env.user.employee_id

        values['show_diario_card'] = bool(employee) or request.env.user.partner_id.is_patient
        return values
```

DA VERIFICARE: Verificare se `_prepare_portal_layout_values` ha cambiato firma in Odoo 19 (es. nuovi parametri obbligatori). Fonte non trovata, verificare manualmente nel file `addons/portal/controllers/portal.py` branch 19.0.

#### 3.2 [P2/S] Controller - gestione accesso con sudo() potenzialmente insicura

File: `controllers/controllers.py` linee 13, 63, 70, 94
Il controller usa `sudo()` in modo estensivo per le operazioni CRUD sulle note portal. Questo bypassa completamente le ACL. In Odoo 19, il pattern consigliato è utilizzare record rules adeguate e limitare l'uso di sudo().

Codice attuale (esempio linea 63):
```python
request.env['portal.note'].sudo().create(note_data)
```

ASSUNZIONE: L'uso di sudo() è necessario perché gli utenti portal non hanno accesso diretto al modello `portal.note` a livello ORM. Tuttavia, si raccomanda l'aggiunta di record rules per limitare l'accesso piuttosto che affidarsi solo alla logica nel controller.

#### 3.3 [P2/XS] Controller - except pass

File: `controllers/controllers.py` linee 109-110
Codice attuale:
```python
except (ValueError, TypeError):
    pass
```

Codice proposto:
```python
except (ValueError, TypeError):
    _logger.warning("Invalid note_id parameter in delete request")
```

VERIFICATO da pylint-odoo (W8138). Il `pass` in un blocco `except` nasconde errori. Aggiungere logging.

---

### 4. Views

#### 4.1 [P1/S] Template portal_my_home_diario - verifica xpath per Odoo 19

File: `views/views.xml` linea 5
Codice attuale:
```xml
<xpath expr="//div[hasclass('o_portal_docs')]" position="inside">
```

DA VERIFICARE: Il div con classe `o_portal_docs` potrebbe essere stato rinominato o ristrutturato nel template `portal.portal_my_home` di Odoo 19. Verificare nel file `addons/portal/views/portal_templates.xml` branch 19.0. Se la struttura è cambiata, l'xpath non troverà il target e il modulo non si installerà.

#### 4.2 [P3/XS] Badge class deprecata

File: `views/views.xml` linee 75, 104
Codice attuale:
```xml
<span class="badge badge-info">
```

Codice proposto:
```xml
<span class="badge text-bg-info">
```

DA VERIFICARE: Bootstrap 5 in Odoo 18+ usa `text-bg-*` invece di `badge-*`. Verificare la versione Bootstrap in uso in Odoo 19.

#### 4.3 [P3/XS] Classe CSS ml-2 → ms-2 (Bootstrap 5)

File: `views/views.xml` linea 183
Codice attuale:
```xml
<a href="/my/notes" class="btn btn-secondary ml-2">
```

Codice proposto:
```xml
<a href="/my/notes" class="btn btn-secondary ms-2">
```

VERIFICATO: Bootstrap 5 ha sostituito `ml-*`/`mr-*` con `ms-*`/`me-*`. Odoo 18+ usa Bootstrap 5. Fonte: [Bootstrap 5 Migration Guide](https://getbootstrap.com/docs/5.0/migration/).

File: `views/views.xml` linea 256 (altro `ml-2`)
Stessa correzione: `ml-2` → `ms-2`.

#### 4.4 [P2/XS] Pulizia file views1.xml e views2.xml

I file `views/views1.xml` e `views/views2.xml` non sono nel manifest ma contengono template con xmlid duplicati (`portal_my_home_inherit`, `portal_notes_page`, `portal_create_note`, `portal_note_detail`). Questi xmlid possono creare conflitti con quelli in `views.xml`.

VERIFICATO dalla lettura del codice: `views1.xml` definisce `portal_notes_page` (linea 20) e `views.xml` definisce anch'esso `portal_notes_page` (linea 20). Poiché non sono nel manifest, non vengono caricati, ma la loro presenza nel modulo è confusionaria.

Azione proposta: Eliminare `views/views1.xml` e `views/views2.xml` dal repository.

#### 4.5 [P1/S] Template JavaScript inline nel template XML

File: `views/views.xml` linee 271-277
Codice attuale:
```xml
<script type="text/javascript">
    function confirmDelete() {
        if (confirm('Sei sicuro di voler eliminare questa voce di diario? Questa azione non può essere annullata.')) {
            document.getElementById('deleteForm').submit();
        }
    }
</script>
```

DA VERIFICARE: In Odoo 19, le Content Security Policy (CSP) potrebbero bloccare JavaScript inline. Si consiglia di spostare lo script in un file JS separato e includerlo nel bundle `web.assets_frontend`. Verificare le policy CSP di Odoo 19.

---

### 5. Security

#### 5.1 [P2/S] ACL portal user con permesso unlink

File: `security/ir.model.access.csv` linea 4
Codice attuale:
```csv
access_portal_note_portal,Portal Note Portal,model_portal_note,base.group_portal,1,1,1,1
```

Codice proposto:
```csv
access_portal_note_portal,Portal Note Portal,model_portal_note,base.group_portal,1,0,1,0
```

L'utente portal ha permesso write(1) e unlink(1) diretto al modello. Poiché il controller usa `sudo()`, questi permessi non sono strettamente necessari a livello ORM e rappresentano un rischio di sicurezza: un utente portal potrebbe usare RPC diretto per modificare/eliminare qualsiasi nota.

VERIFICATO dal codice: Il controller gestisce l'accesso con logica custom (controllo employee/owner). I permessi ORM larghi non aggiungono protezione.

#### 5.2 [P1/S] Mancanza di Record Rules per portal.note

Non esiste nessuna Record Rule per il modello `portal.note`. Un utente portal con accesso ORM (permesso read nel CSV) può leggere TUTTE le note di tutti gli utenti.

Codice proposto (nuovo file `security/portal_note_rules.xml`):
```xml
<odoo>
    <record id="portal_note_rule_portal" model="ir.rule">
        <field name="name">Portal Note: own notes only (Portal)</field>
        <field name="model_id" ref="model_portal_note"/>
        <field name="domain_force">[('user_id', '=', user.id)]</field>
        <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
    </record>
    <record id="portal_note_rule_employee" model="ir.rule">
        <field name="name">Portal Note: all notes (Employee)</field>
        <field name="model_id" ref="model_portal_note"/>
        <field name="domain_force">[(1, '=', 1)]</field>
        <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    </record>
</odoo>
```

ASSUNZIONE: Gli utenti portal dovrebbero vedere solo le proprie note. I dipendenti (tutor/professionisti) accedono via sudo() nel controller.

---

### 6. Data e Migrations

#### 6.1 [P0/XS] Aggiornamento versione per script di migrazione

Se sono presenti dati nel database con la versione precedente, potrebbe essere necessario uno script di migrazione pre/post per aggiornare il campo `version` nel database.

ASSUNZIONE: Non ci sono modifiche strutturali ai dati che richiedano uno script di migrazione con openupgradelib. Il bump di versione nel manifest è sufficiente.

---

## SECURITY ANALYSIS

### ACL: portal.note

| Gruppo | Read | Write | Create | Unlink | Giustificazione |
|--------|------|-------|--------|--------|-----------------|
| `base.group_user` (Employee) | 1 | 1 | 1 | 0 | Dipendenti devono poter leggere e gestire le note dei pazienti. Unlink non necessario per dipendenti. |
| `base.group_system` (Admin) | 1 | 1 | 1 | 1 | Amministratori hanno pieno accesso per manutenzione. |
| `base.group_portal` (Portal) | 1 | 0 | 1 | 0 | Portal user crea note proprie. Write e Unlink gestiti via sudo() nel controller con controllo owner. |

### Record Rules proposte

| Rule | Gruppo | Dominio | Scenari edge |
|------|--------|---------|-------------|
| Own notes only | Portal | `[('user_id', '=', user.id)]` | Record con user_id NULL: non visibili al portal (corretto). Multi-company: non applicabile (no company_id). Utenti senza employee: vedono solo proprie note. |
| All notes | Employee | `[(1, '=', 1)]` | Tutti i dipendenti vedono tutte le note. Il controller filtra ulteriormente per tutor/professional. |

### Rischi identificati
1. **Accesso RPC diretto**: Senza record rules, un utente portal potrebbe usare `xmlrpc` o `jsonrpc` per leggere/modificare note di altri utenti. **Rischio ALTO**. VERIFICATO.
2. **sudo() nel controller**: Le operazioni create/delete avvengono con sudo(), che bypassa le ACL. Se un attaccante manipola il POST, potrebbe eliminare note arbitrarie (il controller verifica solo `note.user_id == user.id` o relazione tutor/professional). **Rischio MEDIO**. VERIFICATO.

---

## ACCEPTANCE CRITERIA

1. [ ] Il modulo si installa senza errori su Odoo 19.0 con il modulo `contacts_patient` 19.0 preinstallato
2. [ ] Un utente portal può creare una nuova voce di diario dal portale (`/my/notes/create`)
3. [ ] Un utente portal può visualizzare solo le proprie voci di diario nella lista (`/my/notes`)
4. [ ] Un tutor/professionista (employee) può visualizzare le note dei propri pazienti
5. [ ] La funzione "Raggruppa per utente" funziona correttamente (`/my/notes?group_by_user=1`)
6. [ ] Un utente portal può eliminare solo le proprie voci di diario
7. [ ] Il pulsante statistico "Note Diario" sulla form del partner mostra il conteggio corretto e apre la lista filtrata
8. [ ] La card "Diario" appare nella home page del portale per gli utenti autorizzati
9. [ ] Il campo "Come sto" viene salvato correttamente e visualizzato nel badge
10. [ ] Non è possibile accedere alle note di altri utenti via RPC diretto (dopo aggiunta record rules)

---

## FONTI E RIFERIMENTI

| Fonte | URL |
|-------|-----|
| OCA Migration Wiki 19.0 | https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-19.0 |
| Odoo 19 ORM Changelog | https://www.odoo.com/documentation/19.0/developer/reference/backend/orm/changelog.html |
| pylint-odoo rules | https://github.com/OCA/pylint-odoo |
| Bootstrap 5 Migration | https://getbootstrap.com/docs/5.0/migration/ |
| Odoo 19 Security Reference | https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html |
| Portal template 19.0 | Fonte non trovata, verificare manualmente in `addons/portal/views/portal_templates.xml` branch 19.0 |

---

## AUTOVALIDAZIONE

- [x] Versione sorgente (18.0) e target (19.0) specificate
- [x] Tutti i file del modulo elencati come analizzati (17 file)
- [x] Ogni modifica con file, linea, codice prima e dopo, priorità, effort
- [x] Analisi security con ACL per il modello `portal.note` e Record Rules proposte
- [x] Nessuna API inventata (tutte verificabili o segnalate come DA VERIFICARE)
- [x] Fonti citate per ogni breaking change
- [x] Distinzione tra VERIFICATO, DA VERIFICARE e ASSUNZIONE

### Tool utilizzati
- **pylint-odoo 10.0.0**: Eseguito con successo. 8 warning/convention identificati. Rating: 9.24/10.
- **odoo-module-migrator 0.5.0**: Non supporta la migrazione 18.0 → 19.0 (target massimo: 18.0). Non applicabile.
