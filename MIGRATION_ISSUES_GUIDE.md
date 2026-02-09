# Creazione Automatica Issue per Migrazione Odoo

Questo repository contiene strumenti per generare automaticamente le GitHub issue per i file di analisi di migrazione presenti nella cartella `migration_analysis/`.

## Panoramica

Sono stati identificati **6 file di analisi di migrazione** nella cartella `migration_analysis/`:

1. `ace_remove_powered_by_odoo_migration.md` - Complessità: Bassa
2. `customer_notes_odoo_migration.md` - Complessità: Media
3. `mail_debrand_migration.md` - Complessità: Media
4. `survey_file_upload_field_migration.md` - Complessità: Alta
5. `survey_whatsapp_migration.md` - Complessità: Alta
6. `whatsapp_calendar_migration.md` - Complessità: Media

Per ognuno di questi file è stata generata una issue template completa.

## File Generati

### Script Python: `create_migration_issues.py`

Script Python che:
- Legge tutti i file `.md` dalla cartella `migration_analysis/`
- Estrae le informazioni chiave da ogni file (nome modulo, complessità, summary)
- Genera i template delle issue in formato markdown
- Crea uno script shell per l'automazione

**Esecuzione:**
```bash
python3 create_migration_issues.py
```

### Directory: `issue_templates/`

Contiene i template generati per ogni issue:

- **issue_01_*.md** through **issue_06_*.md**: Template individuali per ogni modulo
- **ALL_ISSUES.md**: Panoramica completa di tutte le issue
- **README.md**: Guida dettagliata per la creazione delle issue

### Script Shell: `create_issues.sh`

Script bash eseguibile che utilizza GitHub CLI (`gh`) per creare automaticamente tutte le issue.

**Prerequisiti:**
- [GitHub CLI](https://cli.github.com/) installato
- Autenticazione GitHub configurata (`gh auth login`)

**Esecuzione:**
```bash
chmod +x create_issues.sh  # Se necessario
./create_issues.sh
```

## Come Utilizzare

### Opzione 1: Creazione Automatica (Raccomandato)

Se hai GitHub CLI installato:

```bash
cd /home/runner/work/odoomigration/odoomigration
./create_issues.sh
```

Questo creerà automaticamente tutte e 6 le issue con:
- Titoli appropriati
- Descrizioni dettagliate
- Label corrette (`migration`, `odoo-19`, `complexity: low/medium/high`)
- Checklist di task da completare

### Opzione 2: Creazione Manuale

1. Apri il file `issue_templates/ALL_ISSUES.md` per vedere tutte le issue
2. Per ogni issue:
   - Vai su https://github.com/GianpaoloCalzolaro/odoomigration/issues/new
   - Copia il titolo dal template
   - Copia il body dal template
   - Aggiungi le label indicate
   - Clicca "Submit new issue"

### Opzione 3: Tramite API GitHub

Usa il client API che preferisci con i dati dai file template.

## Struttura delle Issue

Ogni issue include:

```markdown
# Migrazione: [nome_modulo] (18.0 → 19.0)

## Complessità
[Bassa/Media/Alta]

## Descrizione
[Informazioni chiave dal file di analisi]

## File di Analisi
Vedi `migration_analysis/[nome_file].md` per l'analisi completa

## Tasks
- [ ] Verificare e aggiornare dipendenze
- [ ] Applicare modifiche richieste al manifest
- [ ] Aggiornare codice Python se necessario
- [ ] Aggiornare template XML/views
- [ ] Testare il modulo migrato
- [ ] Aggiornare documentazione
```

## Label Utilizzate

- `migration`: Indica che è una issue di migrazione
- `odoo-19`: Specifica la versione target di Odoo
- `complexity: low`: Per migrazioni semplici (1 modulo)
- `complexity: medium`: Per migrazioni di media difficoltà (3 moduli)
- `complexity: high`: Per migrazioni complesse (2 moduli)

## Rigenerare i Template

Se i file di analisi vengono modificati, puoi rigenerare i template:

```bash
python3 create_migration_issues.py
```

## Dettagli delle Issue

### Issue 1: ace_remove_powered_by_odoo
- **Complessità**: Bassa
- **Descrizione**: Rimuove il testo "Powered by Odoo" dalla pagina di login
- **Label**: `migration`, `odoo-19`, `complexity: low`

### Issue 2: customer_notes_odoo
- **Complessità**: Media
- **Descrizione**: Customer Diario Portal - gestione diario personale nel portale
- **Label**: `migration`, `odoo-19`, `complexity: medium`

### Issue 3: mail_debrand
- **Complessità**: Media
- **Descrizione**: Rimozione del branding Odoo dalle email
- **Label**: `migration`, `odoo-19`, `complexity: medium`

### Issue 4: survey_file_upload_field
- **Complessità**: Alta
- **Descrizione**: Aggiunge campo di upload file ai survey
- **Label**: `migration`, `odoo-19`, `complexity: high`

### Issue 5: survey_whatsapp
- **Complessità**: Alta
- **Descrizione**: Integrazione WhatsApp per i survey
- **Label**: `migration`, `odoo-19`, `complexity: high`

### Issue 6: whatsapp_calendar
- **Complessità**: Media
- **Descrizione**: Integrazione WhatsApp per il calendario
- **Label**: `migration`, `odoo-19`, `complexity: medium`

## Note

- Tutte le issue fanno riferimento al file di analisi completo in `migration_analysis/`
- Le checklist di task sono standardizzate ma possono essere personalizzate per ogni modulo
- Le label di complessità aiutano a prioritizzare il lavoro di migrazione

## Supporto

Per domande o problemi:
1. Verifica la documentazione in `issue_templates/README.md`
2. Controlla i file di analisi originali in `migration_analysis/`
3. Apri una issue nel repository
