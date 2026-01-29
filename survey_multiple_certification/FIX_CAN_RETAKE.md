# Fix per errore answer.can_retake

## Problema
Il template `survey_templates.xml` faceva riferimento al campo `answer.can_retake` che non esiste nel modello `survey.user_input`, causando un errore alla fine del sondaggio.

## Soluzione Implementata

### 1. Logica can_retake nel Controller
Nel file `controllers/main.py`, è stata aggiunta la logica per calcolare se l'utente può rifare il test:

```python
# Calcola se l'utente può rifare il test (can_retake)
# Questa logica sostituisce il campo answer.can_retake che non esiste nel modello
can_retake = False
if answer.state == 'done':
    # La logica di can_retake dipende dai tentativi del survey
    if hasattr(survey, 'attempts_limit') and survey.attempts_limit > 0:
        # Se c'è un limite di tentativi, controlla se ne ha ancora disponibili
        attempts_count = len(answer.history_ids) if hasattr(answer, 'history_ids') else 1
        can_retake = attempts_count < survey.attempts_limit
    else:
        # Se non c'è limite di tentativi, può sempre rifare il test
        # Ma solo se il survey consente ripetizioni (logica standard Odoo)
        can_retake = getattr(survey, 'users_can_go_back', False) or getattr(survey, 'users_login_required', False)

# Aggiungi can_retake al contesto per tutti i tipi di survey
response.qcontext['can_retake'] = can_retake
```

### 2. Aggiornamento Template
Nel file `views/survey_templates.xml`, è stato sostituito il riferimento:

**Prima:**
```xml
<a t-if="answer.can_retake" t-att-href="request.httprequest.path" class="btn btn-primary">
```

**Dopo:**
```xml
<a t-if="can_retake" t-att-href="request.httprequest.path" class="btn btn-primary">
```

## Come Funziona

1. **Controller**: Quando viene completato un sondaggio, il controller personalizzato calcola se l'utente può rifare il test basandosi su:
   - Lo stato del sondaggio (deve essere 'done')
   - Il numero di tentativi già fatti vs il limite impostato
   - Le impostazioni del survey per le ripetizioni

2. **Template**: Il template ora utilizza la variabile `can_retake` calcolata dal controller invece di cercare un campo inesistente nel modello.

3. **Robustezza**: La soluzione gestisce anche i casi edge:
   - Survey senza limite di tentativi
   - Survey senza cronologia tentativi
   - Survey con diverse configurazioni di accesso

## Vantaggi

- ✅ **Elimina l'errore**: Non ci sono più riferimenti a campi inesistenti
- ✅ **Logica centralizzata**: La logica di can_retake è nel controller, facile da modificare
- ✅ **Flessibile**: Si adatta a diverse configurazioni di survey
- ✅ **Retrocompatibile**: Funziona con la logica esistente del modulo

## Test

Per testare la soluzione:

1. Completare un sondaggio con certificazione multipla
2. Verificare che non ci siano più errori alla fine
3. Il pulsante "Ripeti il test" dovrebbe apparire solo se appropriato
4. Controllare i log per confermare che can_retake viene calcolato correttamente

## File Modificati

- `controllers/main.py` - Aggiunta logica can_retake
- `views/survey_templates.xml` - Sostituito answer.can_retake con can_retake