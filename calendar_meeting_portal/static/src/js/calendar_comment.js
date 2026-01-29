/** @odoo-module **/

/**
 * Modulo per gestire i commenti nei meeting del portale calendar
 * Aggiornato per Odoo 18 - Rimozione jQuery e utilizzo vanilla JavaScript
 */

// Gestione eventi per il portale calendar meeting
document.addEventListener('DOMContentLoaded', function() {
    
    // Gestione click sui pulsanti per aprire modal commenti
    document.addEventListener('click', function(event) {
        // Pulsante per aprire modal commento
        if (event.target.classList.contains('update_calendar_details')) {
            // Pulisce il campo textarea quando si apre il modal
            const modalId = event.target.getAttribute('data-bs-target');
            if (modalId) {
                // Trova il modal corrispondente
                const modal = document.querySelector(modalId);
                if (modal) {
                    const textarea = modal.querySelector('.custom_calendar_comment');
                    if (textarea) {
                        textarea.value = '';
                    }
                }
            }
        }
        
        // Pulsante per chiudere modal commento
        if (event.target.classList.contains('hide_timesheet_comment_wizard')) {
            // Trova il modal parent e lo chiude
            const modal = event.target.closest('.MyCustomCalendarModal');
            if (modal) {
                // Usa Bootstrap 5 API per chiudere il modal
                const bootstrapModal = bootstrap.Modal.getInstance(modal);
                if (bootstrapModal) {
                    bootstrapModal.hide();
                }
            }
        }
    });

    // Gestione invio form commenti
    document.addEventListener('submit', function(event) {
        if (event.target.querySelector('.custom_calendar_comment')) {
            const textarea = event.target.querySelector('.custom_calendar_comment');
            
            // Validazione: controlla che il commento non sia vuoto
            if (!textarea.value.trim()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Mostra messaggio di errore
                textarea.classList.add('is-invalid');
                
                // Aggiungi feedback se non esiste
                let feedback = textarea.parentNode.querySelector('.invalid-feedback');
                if (!feedback) {
                    feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    feedback.textContent = 'Inserisci un messaggio prima di inviare.';
                    textarea.parentNode.appendChild(feedback);
                }
                
                return false;
            } else {
                // Rimuovi classe di errore se presente
                textarea.classList.remove('is-invalid');
            }
        }
    });

    // Gestione eventi sui textarea per rimuovere errori quando l'utente inizia a scrivere
    document.addEventListener('input', function(event) {
        if (event.target.classList.contains('custom_calendar_comment')) {
            if (event.target.value.trim()) {
                event.target.classList.remove('is-invalid');
            }
        }
    });
});

// Export per compatibilità con il sistema di moduli Odoo (se necessario)
export default {
    init: function() {
        console.log('Calendar Portal Comment module initialized');
    }
};
