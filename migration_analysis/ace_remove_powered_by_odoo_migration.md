# Migration Issue: ace_remove_powered_by_odoo (18.0 → 19.0)

## SUMMARY

**Modulo:** ace_remove_powered_by_odoo (Remove Powered By Odoo)
**Versione sorgente:** 18.0.0.1 (formato non standard, manca segmento versione)
**Versione target:** 19.0
**Autore:** A Cloud ERP
**Licenza:** LGPL-3

### Panoramica funzionale
Il modulo rimuove il testo "Powered by Odoo" dalla pagina di login e dalla pagina di signup. Funzionalità principali:
- Override del template `web.login_layout` per rimuovere il footer con branding Odoo
- Sostituzione del div footer con un div vuoto
- Modulo minimale: un solo file XML di vista, nessun codice Python

### Livello di complessità della migrazione: **Bassa**
Il modulo è estremamente semplice: contiene solo un template XML che fa override di un template core. Il rischio principale è che la struttura del template `web.login_layout` sia cambiata in Odoo 19.

### File analizzati
| File | Tipo |
|------|------|
| `__manifest__.py` | Manifest |
| `__init__.py` | Init (vuoto) |
| `views/web_login.xml` | Template XML |
| `static/description/icon.png` | Icona |
| `static/description/index.html` | Descrizione HTML |
| `static/description/powered_by_odoo.png` | Screenshot |
| `static/description/images/*.png` | Screenshots |
| `static/description/icon/*.png` | Icone supporto |
| `static/description/suggest/*.png` | Suggerimenti |

---

## PREREQUISITES

### Dipendenze

| Dipendenza | Tipo | Stato 19.0 | Strategia |
|------------|------|-----------|-----------|
| `base` | Core Odoo | Sempre disponibile | Nessuna azione necessaria. VERIFICATO. |

### Librerie Python esterne
Nessuna.

---

## CHANGES REQUIRED

### 1. Manifest

#### 1.1 [P0/XS] Aggiornamento versione manifest

File: `__manifest__.py` linea 5
Codice attuale:
```python
'version' : '18.0.0.1',
```

Codice proposto:
```python
'version': '19.0.0.1.0',  # Formato standard: 19.0.{major}.{minor}.{patch}
```

VERIFICATO da pylint-odoo (C8106): formato versione non standard. Il formato `18.0.0.1` manca dell'ultimo segmento.

#### 1.2 [P3/XS] Rimozione chiave `description` deprecata

File: `__manifest__.py` linea 11
Codice attuale:
```python
'description': """
    Remove Powered by Odoo from login screen
""",
```

VERIFICATO da pylint-odoo (C8103).

#### 1.3 [P3/XS] Rimozione chiavi superflue

File: `__manifest__.py` linee 22-24
Codice attuale:
```python
'demo': [
],
# ...
'installable': True,
```

VERIFICATO da pylint-odoo (C8116): `demo: []` e `installable: True` sono valori di default.

#### 1.4 [P3/XS] Rimozione bundle assets vuoti

File: `__manifest__.py` linee 26-37
Codice attuale:
```python
'assets': {
    'web._assets_primary_variables': [
    ],
    'web.assets_backend': [

    ],
    'web.assets_frontend': [
    ],
    'web.assets_tests': [
    ],
    'web.qunit_suite_tests': [
    ],
},
```

Codice proposto:
```python
# Rimuovere completamente la chiave 'assets': tutti i bundle sono vuoti
```

VERIFICATO: Bundle vuoti non hanno effetto ma aggiungono rumore al manifest.

---

### 2. Views

#### 2.1 [P0/S] web_login.xml - Verifica xpath target per Odoo 19

File: `views/web_login.xml` linee 3-7
Codice attuale:
```xml
<template id="web_login_layout_inherit" inherit_id="web.login_layout" name="Web Login Layout">
    <xpath expr="//div[@class='card-body']//div[last()]" position="replace">
        <div class="text-center small mt-4 pt-3 login--footer" t-if="not disable_footer">
        </div>
    </xpath>
</template>
```

DA VERIFICARE:
1. Il template `web.login_layout` deve ancora esistere in Odoo 19 con `inherit_id="web.login_layout"` valido.
2. L'xpath `//div[@class='card-body']//div[last()]` deve trovare l'elemento corretto. Se la struttura HTML della pagina di login è cambiata in Odoo 19, l'xpath potrebbe:
   - Non trovare nessun elemento (errore di installazione)
   - Trovare un elemento diverso (rimozione di contenuto non previsto)
3. La classe `card-body` potrebbe essere stata rinominata se Odoo 19 ha aggiornato il layout login.
4. La variabile `disable_footer` deve essere ancora disponibile nel contesto del template.

**Strategia di verifica**: Confrontare il template `web.login_layout` tra Odoo 18.0 e 19.0 nel file `addons/web/views/webclient_templates.xml` o equivalente.

#### 2.2 [P2/XS] web_login.xml - xpath ambiguo

L'xpath `//div[@class='card-body']//div[last()]` potrebbe matchare elementi diversi se la struttura del DOM cambia. Un xpath più specifico ridurrebbe il rischio.

ASSUNZIONE: L'xpath attuale funziona in Odoo 18.0 perché l'ultimo `div` dentro `card-body` è il footer "Powered by Odoo". Se in Odoo 19 viene aggiunto un altro `div` dopo il footer, l'xpath matcherà quello nuovo invece del footer.

Codice proposto (più robusto):
```xml
<xpath expr="//div[hasclass('login--footer')]" position="replace">
    <div class="text-center small mt-4 pt-3 login--footer" t-if="not disable_footer">
    </div>
</xpath>
```

DA VERIFICARE: Verificare se il div footer originale ha una classe specifica (come `login--footer`) che possa essere usata come target più preciso.

---

### 3. Security

Il modulo non definisce modelli e non modifica ACL o Record Rules.

---

## SECURITY ANALYSIS

Il modulo non introduce rischi di sicurezza. Modifica solo l'aspetto visivo della pagina di login rimuovendo il testo "Powered by Odoo".

### Rischi identificati
Nessun rischio di sicurezza identificato. Il modulo opera esclusivamente a livello di template HTML frontend senza accesso a dati o logica server.

---

## ACCEPTANCE CRITERIA

1. [ ] Il modulo si installa senza errori su Odoo 19.0
2. [ ] La pagina di login (`/web/login`) non mostra "Powered by Odoo" nel footer
3. [ ] La pagina di signup (`/web/signup`) non mostra "Powered by Odoo" nel footer
4. [ ] La pagina di reset password (`/web/reset_password`) non mostra "Powered by Odoo"
5. [ ] Il footer vuoto è visibile (div presente ma senza contenuto) quando `disable_footer` è False
6. [ ] Il footer è completamente nascosto quando `disable_footer` è True
7. [ ] Nessun errore nel log durante il rendering della pagina di login

---

## FONTI E RIFERIMENTI

| Fonte | URL |
|-------|-----|
| OCA Migration Wiki 19.0 | https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-19.0 |
| pylint-odoo rules | https://github.com/OCA/pylint-odoo |
| Odoo web.login_layout template | Fonte non trovata, verificare manualmente in `addons/web/views/webclient_templates.xml` branch 19.0 |
| Odoo 19 Technical Changes | https://www.cybrosys.com/blog/overview-of-what-developers-need-to-know-in-odoo-19-technical-changes |

---

## AUTOVALIDAZIONE

- [x] Versione sorgente (18.0) e target (19.0) specificate
- [x] Tutti i file del modulo elencati come analizzati (19 file)
- [x] Ogni modifica con file, linea, codice prima e dopo, priorità, effort
- [x] Analisi security (nessun modello, nessuna ACL)
- [x] Nessuna API inventata
- [x] Fonti citate
- [x] Distinzione tra VERIFICATO, DA VERIFICARE e ASSUNZIONE

### Tool utilizzati
- **pylint-odoo 10.0.0**: Eseguito con successo. 6 warning/convention identificati. Rating: 0.00/10 (penalizzato per assenza di codice Python analizzabile).
- **odoo-module-migrator 0.5.0**: Non supporta la migrazione 18.0 → 19.0 (target massimo: 18.0). Non applicabile.
