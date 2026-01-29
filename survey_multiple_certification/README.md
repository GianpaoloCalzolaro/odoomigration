# Survey Multiple Certification

## Descrizione

Questo modulo estende la funzionalità di certificazione di Odoo Survey permettendo di definire multiple soglie di certificazione per un singolo sondaggio.

## Problemi Risolti

### 1. Wizard non accessibile
- **Problema**: Mancava il pulsante per aprire il wizard di configurazione delle soglie
- **Soluzione**: Aggiunto il pulsante "Configure Thresholds" nella vista del survey quando `certification_mode = 'multiple'`

### 2. Soglie non visualizzate
- **Problema**: Le soglie create non erano visibili nella form del survey
- **Soluzione**: Aggiunta una vista tree completa per il campo `threshold_ids` con tutti i campi necessari

### 3. Errori nel wizard
- **Problema**: Il wizard aveva alcuni bug nella creazione delle soglie
- **Soluzione**: 
  - Aggiunto nome di default per le soglie (`Level 1`, `Level 2`, ecc.)
  - Gestito il caso in cui `badge_id` sia `None`
  - Semplificato il loop nel metodo `action_next`

## Funzionalità

### Modalità di Certificazione
- **Single**: Utilizza la certificazione standard di Odoo
- **Multiple**: Utilizza le soglie multiple personalizzate

### Wizard di Configurazione
1. **Step 1 - Select**: Selezione del numero di soglie (2-15)
2. **Step 2 - Config**: Configurazione dettagliata di ogni soglia:
   - Nome della soglia
   - Percentuale massima
   - Badge associato (opzionale)
   - Descrizione HTML (opzionale)

### Calcolo Automatico
- Il campo `percentage_min` viene calcolato automaticamente in base alla sequenza delle soglie
- La prima soglia inizia da 0%
- Ogni soglia successiva inizia dal valore `percentage_max` della soglia precedente

## Utilizzo

1. **Creare un Survey**
   - Andare in Survey > Configuration > Surveys
   - Creare un nuovo survey o modificarne uno esistente

2. **Configurare la Certificazione Multipla**
   - Impostare `Certification Mode` su "Multiple"
   - Cliccare sul pulsante "Configure Thresholds"

3. **Usare il Wizard**
   - Selezionare il numero di soglie desiderate (2-15)
   - Cliccare "Next"
   - Configurare ogni soglia con nome, percentuale e badge
   - Cliccare "Apply"

4. **Visualizzare le Soglie**
   - Le soglie create saranno visibili nella sezione "Certification Thresholds"
   - È possibile modificarle direttamente dalla vista tree

## Struttura Tecnica

### Modelli
- `survey.survey`: Esteso con `certification_mode` e `threshold_ids`
- `survey.certification.threshold`: Modello per le soglie di certificazione
- `survey.threshold.wizard`: Wizard per la configurazione delle soglie
- `survey.threshold.wizard.line`: Linee del wizard per ogni soglia

### Viste
- Vista form estesa per survey con configurazione soglie
- Vista form per soglie individuali
- Vista wizard per configurazione guidata

### Sicurezza
- Tutti i modelli hanno accessi configurati per `base.group_user`
- Permessi completi di lettura, scrittura, creazione e cancellazione

## File Modificati

1. `views/survey_survey_views.xml`: Aggiunta vista per soglie e pulsante wizard
2. `models/survey_survey.py`: Aggiunto metodo `action_open_threshold_wizard`
3. `wizard/survey_threshold_wizard.py`: Correzioni bug e miglioramenti
4. `tests/`: Aggiunta suite di test completa

## Test

È stata aggiunta una suite di test completa che verifica:
- Configurazione modalità certificazione
- Creazione e calcolo soglie
- Funzionamento wizard
- Validazioni e constraints
- Selezione soglie in base alla percentuale

Per eseguire i test:
```bash
odoo-bin -c odoo.conf -d test_db -i survey_multiple_certification --test-enable --stop-after-init
```

## Compatibilità

- Odoo 18.0
- Dipendenze: `survey`, `gamification`, `web`

## Autore

Gian Paolo Calzolaro - info@infologis.biz
