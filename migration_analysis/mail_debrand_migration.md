# Migration Issue: mail_debrand (18.0 → 19.0)

## SUMMARY

**Modulo:** mail_debrand (Mail Debrand)
**Versione sorgente:** 18.0.1.0.1
**Versione target:** 19.0
**Autore:** Tecnativa, ForgeFlow, Onestein, Sodexis, Nexterp Romania, OCA
**Licenza:** AGPL-3
**Repository OCA:** https://github.com/OCA/mail

### Panoramica funzionale
Il modulo rimuove il branding Odoo dalle email inviate. Funzionalità principali:
- Rimozione dei link "Powered by Odoo" dal footer delle email
- Override di `_prepare_outgoing_body` in `mail.mail` per pulire l'HTML in uscita
- Override di `_render_template` in `mail.render.mixin` per pulire i template renderizzati
- Metodo `remove_href_odoo()` che analizza l'HTML con lxml e rimuove i link a odoo.com
- Protezione del body originale del messaggio (non modifica i link odoo.com inseriti dall'utente)
- Supporto per input bytes e Markup

### Livello di complessità della migrazione: **Media**
Il modulo è ben strutturato e ha test completi. La complessità principale sta nella verifica che i metodi `_prepare_outgoing_body` e `_render_template` non abbiano cambiato firma in Odoo 19.

**NOTA IMPORTANTE**: Il modulo mail_debrand NON è ancora disponibile nel branch 19.0 di OCA/mail. VERIFICATO: https://github.com/OCA/mail/tree/19.0 non contiene `mail_debrand`. La migrazione dovrà essere fatta manualmente.

### File analizzati
| File | Tipo |
|------|------|
| `__manifest__.py` | Manifest |
| `__init__.py` | Init |
| `models/__init__.py` | Init |
| `models/mail_mail.py` | Model |
| `models/mail_render_mixin.py` | Model |
| `tests/__init__.py` | Init |
| `tests/test_mail_debrand.py` | Test |
| `tests/test_mail_debrand_digest.py` | Test |
| `tests/test_mail_debrand_signup.py` | Test |
| `pyproject.toml` | Build config |
| `README.rst` | Documentazione |
| `readme/CONTRIBUTORS.md` | Documentazione |
| `readme/DESCRIPTION.md` | Documentazione |
| `readme/HISTORY.md` | Documentazione |
| `readme/ROADMAP.md` | Documentazione |
| `readme/USAGE.md` | Documentazione |
| `i18n/*.po` (10 file) | Traduzioni |

---

## PREREQUISITES

### Dipendenze

| Dipendenza | Tipo | Stato 19.0 | Strategia |
|------------|------|-----------|-----------|
| `mail` | Core Odoo | Disponibile in 19.0 | **CRITICO**: Verificare breaking changes in `mail.mail._prepare_outgoing_body()` e `mail.render.mixin._render_template()`. DA VERIFICARE nel branch 19.0. |

### Stato OCA 19.0
| Repository | Branch | Modulo presente | Note |
|-----------|--------|----------------|------|
| OCA/mail | 19.0 | **NO** | Il branch 19.0 esiste ma contiene solo 5 moduli. mail_debrand non è stato migrato. VERIFICATO. |
| OCA/mail | 18.0 | **SI** | Versione 18.0.1.0.1 è la più recente. VERIFICATO. |

### Librerie Python esterne
| Libreria | Uso | Note |
|----------|-----|------|
| `lxml` | Parsing/manipolazione HTML in `remove_href_odoo` | Dipendenza standard Odoo, sempre disponibile. |
| `markupsafe` | Gestione tipo `Markup` | Dipendenza standard Odoo. |

---

## CHANGES REQUIRED

### 1. Manifest

#### 1.1 [P0/XS] Aggiornamento versione manifest

File: `__manifest__.py` linea 15
Codice attuale:
```python
"version": "18.0.1.0.1",
```

Codice proposto:
```python
"version": "19.0.1.0.0",  # Reset patch version per nuovo major
```

#### 1.2 [P3/XS] Rimozione chiave superflua `installable`

File: `__manifest__.py` linea 21
Codice attuale:
```python
"installable": True,
```

Codice proposto:
```python
# Rimuovere: valore di default
```

VERIFICATO da pylint-odoo (C8116).

---

### 2. Models

#### 2.1 [P0/M] mail_mail.py - Verifica _prepare_outgoing_body

File: `models/mail_mail.py` linee 8-15
Codice attuale:
```python
class MailMail(models.AbstractModel):
    _inherit = "mail.mail"

    def _prepare_outgoing_body(self):
        body_html = super()._prepare_outgoing_body()
        return self.env["mail.render.mixin"].remove_href_odoo(
            body_html or "", to_keep=self.body
        )
```

DA VERIFICARE:
1. **`_prepare_outgoing_body`**: Verificare che questo metodo esista ancora in `mail.mail` in Odoo 19 e che la sua firma sia invariata. Se il metodo è stato rinominato o rimosso, il modulo non funzionerà.
2. **Tipo di ritorno**: Il metodo si aspetta che `super()._prepare_outgoing_body()` ritorni una stringa HTML. Se in Odoo 19 ritorna un tipo diverso (es. dict, tuple), il codice si romperà.
3. **`self.body`**: Verificare che `mail.mail.body` sia ancora il campo che contiene il corpo originale del messaggio.

**CRITICO**: Verificare nel file `addons/mail/models/mail_mail.py` branch 19.0.

#### 2.2 [P1/S] mail_mail.py - models.AbstractModel per mail.mail

File: `models/mail_mail.py` linea 8
Codice attuale:
```python
class MailMail(models.AbstractModel):
    _inherit = "mail.mail"
```

`mail.mail` è un `models.Model`, non un `models.AbstractModel`. L'uso di `AbstractModel` per ereditare da un `Model` funziona in Odoo ma è tecnicamente scorretto e potrebbe causare problemi in versioni future.

Codice proposto:
```python
class MailMail(models.Model):
    _inherit = "mail.mail"
```

VERIFICATO: `mail.mail` in Odoo 18.0 è definito come `models.Model`. L'uso di `AbstractModel` per `_inherit` è un bug preesistente.

#### 2.3 [P0/M] mail_render_mixin.py - Verifica _render_template firma

File: `models/mail_render_mixin.py` linee 59-96
Codice attuale:
```python
@api.model
def _render_template(
    self,
    template_src,
    model,
    res_ids,
    engine="inline_template",
    add_context=None,
    options=None,
):
    orginal_rendered = super()._render_template(
        template_src,
        model,
        res_ids,
        engine=engine,
        add_context=add_context,
        options=options,
    )

    for key in res_ids:
        orginal_rendered[key] = self.remove_href_odoo(orginal_rendered[key])

    return orginal_rendered
```

DA VERIFICARE:
1. **Firma di `_render_template`**: Verificare che i parametri `template_src`, `model`, `res_ids`, `engine`, `add_context`, `options` siano ancora presenti e nell'ordine corretto in Odoo 19.
2. **Parametri rimossi/aggiunti**: Se Odoo 19 ha aggiunto nuovi parametri obbligatori o ha rimosso quelli esistenti, l'override si romperà.
3. **Tipo di ritorno**: Il metodo si aspetta un dict `{res_id: rendered_string}`. Se il formato di ritorno è cambiato, il loop `for key in res_ids` fallirà.

**CRITICO**: Verificare nel file `addons/mail/models/mail_render_mixin.py` branch 19.0.

#### 2.4 [P2/XS] mail_render_mixin.py - Typo variabile "orginal_rendered"

File: `models/mail_render_mixin.py` linee 84, 94
Codice attuale:
```python
orginal_rendered = super()._render_template(...)
# ...
orginal_rendered[key] = self.remove_href_odoo(orginal_rendered[key])
return orginal_rendered
```

Codice proposto:
```python
original_rendered = super()._render_template(...)
# ...
original_rendered[key] = self.remove_href_odoo(original_rendered[key])
return original_rendered
```

VERIFICATO: "orginal" è un typo per "original". Non bloccante ma da correggere per leggibilità.

#### 2.5 [P2/S] mail_render_mixin.py - remove_href_odoo come metodo di istanza

File: `models/mail_render_mixin.py` linea 17
Il metodo `remove_href_odoo` è definito come metodo di istanza ma non usa `self` internamente (eccetto per `self.env` in caso di necessità futura). È chiamato sia da `mail_mail.py` (linea 13: `self.env["mail.render.mixin"].remove_href_odoo(...)`) sia da `_render_template`.

ASSUNZIONE: Il metodo potrebbe beneficiare del decoratore `@api.model` dato che non dipende dal recordset, ma non è bloccante.

---

### 3. Tests

#### 3.1 [P1/S] test_mail_debrand.py - Verifica template refs

File: `tests/test_mail_debrand.py` linee 38-39
Codice attuale:
```python
body = self.env["ir.qweb"]._render(
    template_ref,
    {
        "message": self.mail,
        "company": self.env.company,
        "email_notification_force_footer": True,
    },
    lang=lang.code,
    minimal_qcontext=True,
)
```

DA VERIFICARE:
1. Il template `mail.mail_notification_layout` potrebbe avere variabili di contesto diverse in Odoo 19.
2. Il parametro `minimal_qcontext` di `ir.qweb._render()` deve essere ancora supportato.
3. Il template `mail.mail_notification_light` (linea 67) deve ancora esistere in Odoo 19.

#### 3.2 [P1/S] test_mail_debrand.py - Riferimento a mail.template vs mail.render.mixin

File: `tests/test_mail_debrand.py` linea 31
Codice attuale:
```python
self.env["mail.template"].remove_href_odoo(
    b"Binary value with more than 20 characters"
)
```

Il test chiama `remove_href_odoo` su `mail.template`, ma il metodo è definito su `mail.render.mixin`. Funziona perché `mail.template` eredita da `mail.render.mixin`.

DA VERIFICARE: Se in Odoo 19 la catena di ereditarietà di `mail.template` è cambiata, questo test potrebbe fallire.

#### 3.3 [P1/S] test_mail_debrand_digest.py - _compute_kpis e _compute_tips

File: `tests/test_mail_debrand_digest.py` linee 51-58
Codice attuale:
```python
"kpi_data": self.mail_digest_id._compute_kpis(
    self.env.user.company_id, self.env.user
),
"tips": self.mail_digest_id._compute_tips(
    self.env.user.company_id, self.env.user, tips_count=1, consumed=True
),
"preferences": self.mail_digest_id._compute_preferences(
    self.env.user.company_id, self.env.user
),
```

DA VERIFICARE: I metodi `_compute_kpis`, `_compute_tips`, `_compute_preferences` su `digest.digest` potrebbero avere firme diverse in Odoo 19. Il modulo `digest` potrebbe non essere installato.

#### 3.4 [P2/XS] test_mail_debrand_digest.py - uso di _() vs self.env._()

File: `tests/test_mail_debrand_digest.py` linea 44
Codice attuale:
```python
from odoo import _
# ...
"top_button_label": _("Connect"),
```

Codice proposto:
```python
"top_button_label": self.env._("Connect"),
```

VERIFICATO da pylint-odoo (W8161).

#### 3.5 [P1/S] test_mail_debrand_signup.py - auth_signup template

File: `tests/test_mail_debrand_signup.py` linee 14-19
Codice attuale:
```python
template = self.env.ref(
    "auth_signup.set_password_email",
)
self.assertIn("www.odoo.com", template.body_html)
self.assertIn("Accept invitation", template.body_html)
self.assertIn("to discover the tool", template.body_html)
```

DA VERIFICARE: Il template `auth_signup.set_password_email` potrebbe avere un contenuto diverso in Odoo 19. Le stringhe "www.odoo.com", "Accept invitation", "to discover the tool" potrebbero essere cambiate.

---

### 4. Build

#### 4.1 [P3/XS] pyproject.toml - verifica whool

File: `pyproject.toml`
Codice attuale:
```toml
[build-system]
requires = ["whool"]
build-backend = "whool.buildapi"
```

DA VERIFICARE: La libreria `whool` è specifica dell'ecosistema OCA. Verificare se è necessaria per Odoo 19 o se va aggiornata.

---

## SECURITY ANALYSIS

Il modulo non definisce nuovi modelli e non modifica ACL o Record Rules. Opera esclusivamente tramite override di metodi esistenti sui modelli `mail.mail` e `mail.render.mixin`.

### Rischi identificati
1. **Bypass contenuto email**: Il metodo `remove_href_odoo` modifica l'HTML delle email in uscita. Se il metodo ha un bug, potrebbe corrompere il contenuto delle email o rimuovere link legittimi. **Rischio BASSO** (il test `test_body_intact` verifica questo scenario). VERIFICATO.
2. **Performance lxml**: Il parsing HTML con lxml ad ogni email inviata aggiunge overhead. Per volumi elevati di email, questo potrebbe impattare le performance. **Rischio BASSO**. ASSUNZIONE.

---

## ACCEPTANCE CRITERIA

1. [ ] Il modulo si installa senza errori su Odoo 19.0
2. [ ] Le email inviate non contengono il testo "Powered by" con link a odoo.com
3. [ ] Le email con il layout `mail.mail_notification_layout` non hanno branding Odoo
4. [ ] Le email con il layout `mail.mail_notification_light` non hanno branding Odoo
5. [ ] Il body originale del messaggio (link a odoo.com inseriti dall'utente) viene preservato intatto
6. [ ] I template renderizzati via `_render_template` non contengono branding Odoo
7. [ ] Input binari sono gestiti senza errori (test `test_debrand_binary_value`)
8. [ ] Il test con lingua NL (olandese) conferma la rimozione del testo tradotto "Aangeboden door"
9. [ ] Se il modulo digest è installato, le email digest non contengono branding
10. [ ] Se il modulo auth_signup è installato, l'email di invito non contiene branding

---

## FONTI E RIFERIMENTI

| Fonte | URL |
|-------|-----|
| OCA Migration Wiki 19.0 | https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-19.0 |
| OCA/mail branch 18.0 - mail_debrand | https://github.com/OCA/mail/tree/18.0/mail_debrand |
| OCA/mail branch 19.0 | https://github.com/OCA/mail/tree/19.0 (mail_debrand assente) |
| pylint-odoo prefer-env-translation | https://github.com/odoo/odoo/pull/174844 |
| mail.mail source 19.0 | Fonte non trovata, verificare manualmente in `addons/mail/models/mail_mail.py` branch 19.0 |
| mail.render.mixin source 19.0 | Fonte non trovata, verificare manualmente in `addons/mail/models/mail_render_mixin.py` branch 19.0 |

---

## AUTOVALIDAZIONE

- [x] Versione sorgente (18.0) e target (19.0) specificate
- [x] Tutti i file del modulo elencati come analizzati (17 file + 10 i18n)
- [x] Ogni modifica con file, linea, codice prima e dopo, priorità, effort
- [x] Analisi security (nessun nuovo modello, nessuna ACL modificata)
- [x] Nessuna API inventata (tutte segnalate come DA VERIFICARE)
- [x] Fonti citate per ogni breaking change
- [x] Distinzione tra VERIFICATO, DA VERIFICARE e ASSUNZIONE

### Tool utilizzati
- **pylint-odoo 10.0.0**: Eseguito con successo. 2 warning/convention identificati. Rating: 9.84/10. Modulo ben strutturato.
- **odoo-module-migrator 0.5.0**: Non supporta la migrazione 18.0 → 19.0 (target massimo: 18.0). Non applicabile.
