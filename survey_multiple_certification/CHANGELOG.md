# Changelog - Survey Multiple Certification

## [1.0.2] - 2025-07-18

### 🐛 Bug Fix Critico
- **Risolto errore answer.can_retake**: Eliminato l'errore che compariva alla fine del sondaggio per campo inesistente
  - **Problema**: Il template faceva riferimento a `answer.can_retake` che non esiste nel modello `survey.user_input`
  - **Soluzione**: Implementata logica can_retake nel controller personalizzato e passata al template come variabile separata
  - **File modificati**: 
    - `controllers/main.py`: Aggiunta logica robusta per calcolo can_retake
    - `views/survey_templates.xml`: Sostituito `answer.can_retake` con `can_retake`

### ✨ Miglioramenti
- **Logica can_retake intelligente**: Il controller ora calcola se l'utente può rifare il test basandosi su:
  - Stato del sondaggio (deve essere 'done')
  - Numero di tentativi vs limite impostato nel survey
  - Configurazioni del survey per le ripetizioni (`users_can_go_back`, `users_login_required`)
- **Gestione casi edge**: La soluzione gestisce survey senza limiti di tentativi e diverse configurazioni
- **Documentazione**: Aggiunto `FIX_CAN_RETAKE.md` con spiegazione dettagliata della soluzione

### 🧪 Test
- Aggiunto script di test automatico (`test_can_retake_fix.py`) per verificare la corretta implementazione
- Test verifica:
  - Rimozione di `answer.can_retake` dai template
  - Presenza di `can_retake` nei template
  - Implementazione logica nel controller
  - Presenza commenti esplicativi

### 🔧 Dettagli Tecnici
La soluzione robusta implementa la logica di `can_retake` nel controller anziché affidarsi a un campo inesistente nel modello:

```python
# Calcola se l'utente può rifare il test (can_retake)
# Questa logica sostituisce il campo answer.can_retake che non esiste nel modello
can_retake = False
if answer.state == 'done':
    if hasattr(survey, 'attempts_limit') and survey.attempts_limit > 0:
        attempts_count = len(answer.history_ids) if hasattr(answer, 'history_ids') else 1
        can_retake = attempts_count < survey.attempts_limit
    else:
        can_retake = getattr(survey, 'users_can_go_back', False) or getattr(survey, 'users_login_required', False)

response.qcontext['can_retake'] = can_retake
```

---

## [1.0.1] - 2025-07-18

### 🐛 Bug Fix
- **Risolto problema wizard non accessibile**: Aggiunto pulsante "Configure Thresholds" nella vista survey
- **Risolto problema soglie non visibili**: Migliorata vista delle soglie nella form del survey con vista tree completa
- **Corretti bug nel wizard**: 
  - Aggiunto nome di default per le soglie create
  - Gestito correttamente il caso `badge_id = None`
  - Semplificato il loop di creazione soglie

### ✨ Miglioramenti
- **Vista migliorata**: Aggiunta vista tree per `threshold_ids` con tutti i campi necessari:
  - Sequence (con handle per riordinamento)
  - Name
  - Percentage Min (readonly)
  - Percentage Max
  - Badge ID
  - Active
- **Pulsante wizard**: Aggiunto pulsante "Configure Thresholds" visibile solo quando `certification_mode = 'multiple'`
- **Help text**: Aggiunto testo di aiuto per il campo `certification_mode`
- **Metodo wizard**: Aggiunto metodo `action_open_threshold_wizard()` nel modello Survey

### 🧪 Test
- Aggiunta suite di test completa (`tests/test_survey_multiple_certification.py`)
- Test per tutte le funzionalità principali:
  - Modalità certificazione
  - Creazione soglie
  - Funzionamento wizard
  - Validazioni
  - Selezione soglie

### 📚 Documentazione
- Aggiunto README.md completo con:
  - Descrizione problemi risolti
  - Guida utilizzo
  - Struttura tecnica
  - Istruzioni test
- Aggiunto script di verifica modulo (`check_module.py`)

### 🔧 File Modificati
- `views/survey_survey_views.xml`: Vista soglie e pulsante wizard
- `models/survey_survey.py`: Metodo apertura wizard e help text
- `wizard/survey_threshold_wizard.py`: Bug fix e miglioramenti
- `tests/`: Nuova directory con test completi
- `README.md`: Documentazione completa
- `CHANGELOG.md`: Questo file

### 🚀 Come Aggiornare
1. Fermare Odoo
2. Sostituire la cartella del modulo con la nuova versione
3. Riavviare Odoo
4. Aggiornare il modulo dal menu Apps o con `-u survey_multiple_certification`

### ✅ Verifiche Pre-Installazione
Tutti i controlli automatici passano:
- ✅ Struttura file completa
- ✅ Manifest corretto
- ✅ Sintassi Python valida
- ✅ Dipendenze corrette
- ✅ Permessi sicurezza configurati

---

## [1.0.0] - Versione Iniziale
- Implementazione modulo base Survey Multiple Certification
- Modelli: survey.certification.threshold, survey.threshold.wizard
- Viste base per configurazione soglie
- Sistema wizard per configurazione guidata
