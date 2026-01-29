# Modulo Appointment No Duplicates

## Descrizione

Il modulo `appointment_no_duplicates` estende il sistema di gestione appuntamenti di Odoo per prevenire la creazione di contatti duplicati quando gli utenti pubblici prenotano appuntamenti.

## Problema Risolto

Il sistema standard di Odoo crea sempre un nuovo contatto quando un utente pubblico prenota un appuntamento, anche se esiste già un contatto con la stessa email o telefono. Questo comporta la creazione di contatti duplicati nel database.

## Soluzione Implementata

Il modulo implementa una ricerca sequenziale intelligente che:

1. **Ricerca per Email**: Prima cerca contatti esistenti usando l'email normalizzata
2. **Ricerca per Telefono**: Se non trova risultati per email, cerca usando il telefono formattato  
3. **Aggiornamento Intelligente**: Se trova un contatto esistente, aggiorna solo i campi vuoti
4. **Creazione Sicura**: Solo se non trova nessun contatto, ne crea uno nuovo

## Caratteristiche

- ✅ **Prevenzione Duplicati**: Evita la creazione di contatti duplicati
- ✅ **Ricerca Intelligente**: Utilizza email normalizzata e telefono formattato per le ricerche
- ✅ **Aggiornamento Conservativo**: Aggiorna solo i campi vuoti dei contatti esistenti
- ✅ **Compatibilità Completa**: Mantiene il comportamento originale per utenti autenticati
- ✅ **Gestione Errori**: Gestisce gracefully gli errori senza interrompere il flusso
- ✅ **Performance Ottimizzata**: Utilizza ricerche efficienti con limit e ordinamento

## Struttura del Modulo

```
appointment_no_duplicates/
├── __manifest__.py                 # Manifest del modulo
├── __init__.py                     # Inizializzazione principale
└── controllers/
    ├── __init__.py                 # Inizializzazione controllers
    └── appointment.py              # Controller esteso
```

## Installazione

1. Copiare la cartella `appointment_no_duplicates` nella directory degli addons di Odoo
2. Aggiornare la lista dei moduli in Odoo
3. Installare il modulo dalla lista delle applicazioni

## Dipendenze

- `base`: Modulo base di Odoo
- `appointment`: Modulo appuntamenti di Odoo

## Versione

- **Versione Modulo**: 1.0.0  
- **Versione Odoo**: 18.0
- **Autore**: Gian Paolo Calzolaro
- **Website**: www.infologis.biz

## Logica di Funzionamento

### Per Utenti Autenticati
Il comportamento rimane invariato: viene utilizzato il partner dell'utente autenticato.

### Per Utenti Pubblici

#### Fase 1 - Ricerca per Email
```python
# Normalizza l'email e cerca contatti esistenti
normalized_email = email_normalize(email)
existing_partners = env['res.partner'].search([
    ('email_normalized', '=', normalized_email)
], order='create_date desc', limit=1)
```

#### Fase 2 - Ricerca per Telefono (se Fase 1 fallisce)
```python
# Formatta il telefono e cerca contatti esistenti  
formatted_phone = phone_format(phone, country_code, ...)
existing_partners = env['res.partner'].search([
    ('phone', '=', formatted_phone)
], order='create_date desc', limit=1)
```

#### Fase 3 - Aggiornamento Partner Esistente
```python
# Aggiorna solo i campi vuoti
update_vals = {}
if not partner.name and name:
    update_vals['name'] = name
if not partner.phone and phone:
    update_vals['phone'] = formatted_phone
if not partner.email and email:
    update_vals['email'] = normalized_email
```

#### Fase 4 - Creazione Nuovo Partner (solo se necessario)
```python
# Crea nuovo partner con dati normalizzati
new_partner = env['res.partner'].create({
    'name': name,
    'email': normalized_email,
    'phone': formatted_phone,
    'lang': request.lang.code,
})
```

## Considerazioni Tecniche

### Sicurezza
- Mantiene tutti i controlli di sicurezza originali
- Utilizza `sudo()` solo quando necessario per le ricerche
- Non bypassa validazioni esistenti

### Performance  
- Utilizza `limit=1` per limitare i risultati delle ricerche
- Sfrutta gli indici esistenti sui campi `email_normalized` e `phone`
- Ordina per `create_date desc` per ottenere il partner più recente

### Compatibilità
- Non modifica la signature del metodo originale
- Mantiene tutti i parametri e return statement originali  
- Assicura che il comportamento per utenti autenticati rimanga invariato

### Gestione Errori
- Se `email_normalize()` fallisce, utilizza l'email originale
- Se `phone_format()` fallisce, utilizza il telefono originale
- Se le ricerche database falliscono, procede con la creazione di un nuovo partner
- Non interrompe mai il flusso principale di creazione appuntamento

## Testing

Il modulo è stato progettato per essere testato nei seguenti scenari:

1. **Nuovo contatto**: Primo appuntamento con email/telefono nuovi
2. **Duplicato email**: Appuntamento con email già esistente
3. **Duplicato telefono**: Appuntamento con telefono già esistente  
4. **Aggiornamento campi**: Contatto esistente con campi vuoti da aggiornare
5. **Utente autenticato**: Comportamento invariato per utenti loggati
6. **Gestione errori**: Comportamento con dati malformati o errori di rete

## Supporto

Per supporto tecnico o segnalazione bug, contattare:
- **Email**: supporto@infologis.biz
- **Website**: www.infologis.biz
