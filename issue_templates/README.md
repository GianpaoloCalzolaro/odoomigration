# Migration Issues - Template Guide

Questo directory contiene i template per creare le issue GitHub per ogni file di analisi di migrazione presente in `migration_analysis/`.

## Contenuto

- **ALL_ISSUES.md**: Panoramica completa di tutte le 6 issue da creare
- **issue_01_*.md** through **issue_06_*.md**: Template individuali per ogni issue

## Come Creare le Issue

### Metodo 1: Automatico con GitHub CLI (Raccomandato)

Se hai [GitHub CLI (`gh`)](https://cli.github.com/) installato e autenticato:

```bash
cd /home/runner/work/odoomigration/odoomigration
./create_issues.sh
```

Questo creerà automaticamente tutte le 6 issue con i titoli, le descrizioni e le label appropriate.

### Metodo 2: Manuale tramite GitHub Web Interface

1. Vai su https://github.com/GianpaoloCalzolaro/odoomigration/issues/new
2. Apri uno dei file template (es. `issue_01_ace_remove_powered_by_odoo_migration.md`)
3. Copia il **Title** (senza i backtick)
4. Copia il **Body** completo
5. Aggiungi le **Labels** indicate nel template
6. Clicca "Submit new issue"
7. Ripeti per tutti i 6 template

### Metodo 3: Tramite API GitHub

Puoi usare l'API REST di GitHub o qualsiasi client che preferisci. Ogni template contiene:
- **Title**: Titolo dell'issue
- **Body**: Descrizione completa
- **Labels**: Label da applicare (es. `migration`, `odoo-19`, `complexity: low/medium/high`)

## Issue da Creare

### 1. Migration: ace_remove_powered_by_odoo
- **Complessità**: Bassa
- **File**: `migration_analysis/ace_remove_powered_by_odoo_migration.md`
- **Labels**: `migration`, `odoo-19`, `complexity: low`

### 2. Migration: customer_notes_odoo
- **Complessità**: Media
- **File**: `migration_analysis/customer_notes_odoo_migration.md`
- **Labels**: `migration`, `odoo-19`, `complexity: medium`

### 3. Migration: mail_debrand
- **Complessità**: Media
- **File**: `migration_analysis/mail_debrand_migration.md`
- **Labels**: `migration`, `odoo-19`, `complexity: medium`

### 4. Migration: survey_file_upload_field
- **Complessità**: Alta
- **File**: `migration_analysis/survey_file_upload_field_migration.md`
- **Labels**: `migration`, `odoo-19`, `complexity: high`

### 5. Migration: survey_whatsapp
- **Complessità**: Alta
- **File**: `migration_analysis/survey_whatsapp_migration.md`
- **Labels**: `migration`, `odoo-19`, `complexity: high`

### 6. Migration: whatsapp_calendar
- **Complessità**: Media
- **File**: `migration_analysis/whatsapp_calendar_migration.md`
- **Labels**: `migration`, `odoo-19`, `complexity: medium`

## Struttura delle Issue

Ogni issue include:

- **Titolo**: Nome del modulo da migrare
- **Complessità**: Livello di difficoltà della migrazione
- **Descrizione**: Informazioni chiave dal file di analisi
- **File di Analisi**: Link al file completo di analisi
- **Tasks**: Checklist delle attività da completare
- **Labels**: Tag per organizzazione e prioritizzazione

## Rigenerare i Template

Se hai bisogno di rigenerare i template (ad esempio dopo modifiche ai file di analisi):

```bash
cd /home/runner/work/odoomigration/odoomigration
python3 create_migration_issues.py
```

Questo script:
1. Legge tutti i file `.md` in `migration_analysis/`
2. Estrae le informazioni chiave da ogni file
3. Genera i template delle issue in `issue_templates/`
4. Crea lo script shell `create_issues.sh` per la creazione automatica

## Note

- Le issue sono ordinate alfabeticamente per nome del modulo
- Le label di complessità aiutano a prioritizzare il lavoro:
  - `complexity: low`: Migrazioni semplici
  - `complexity: medium`: Migrazioni di media difficoltà
  - `complexity: high`: Migrazioni complesse che richiedono più attenzione
- Ogni issue include una checklist di task standard per tracciare il progresso della migrazione
