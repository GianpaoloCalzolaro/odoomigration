/** @odoo-module **/

/**
 * Validazione form per creazione appuntamenti nel portale
 * Odoo 18 - Vanilla JavaScript
 */

(function() {
    function init() {
        const meetingForm = document.querySelector('.needs-validation');
        if (!meetingForm) {
            console.info('meeting_create_validation: .needs-validation not found');
            return; // Non siamo nella pagina giusta, esci
        }

    // Validazione form Bootstrap
    meetingForm.addEventListener('submit', function(event) {
        if (!meetingForm.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        } else {
            // Validazione aggiuntiva: data fine > data inizio
            const startDateInput = document.getElementById('start_date');
            const endDateInput = document.getElementById('end_date');
            
            if (startDateInput && endDateInput) {
                const startDate = new Date(startDateInput.value);
                const endDate = new Date(endDateInput.value);
                
                if (endDate <= startDate) {
                    event.preventDefault();
                    event.stopPropagation();
                    endDateInput.setCustomValidity('La data di fine deve essere successiva alla data di inizio');
                    
                    // Mostra il messaggio di errore
                    const feedback = endDateInput.parentNode.querySelector('.invalid-feedback') || 
                                   createInvalidFeedback(endDateInput.parentNode);
                    feedback.textContent = 'La data di fine deve essere successiva alla data di inizio';
                } else {
                    endDateInput.setCustomValidity('');
                }
            }
        }
        meetingForm.classList.add('was-validated');
    });

    // Validazione dinamica data inizio
    const startDateInput = document.getElementById('start_date');
    if (startDateInput) {
        startDateInput.addEventListener('change', function() {
            validateDateRange();
        });
    }

    // Validazione dinamica data fine
    const endDateInput = document.getElementById('end_date');
    if (endDateInput) {
        endDateInput.addEventListener('change', function() {
            validateDateRange();
        });
    }

    /**
     * Valida che la data di fine sia successiva alla data di inizio
     */
    function validateDateRange() {
        const startDateInput = document.getElementById('start_date');
        const endDateInput = document.getElementById('end_date');
        
        if (!startDateInput || !endDateInput || !startDateInput.value || !endDateInput.value) {
            return;
        }

        const startDate = new Date(startDateInput.value);
        const endDate = new Date(endDateInput.value);
        
        if (endDate <= startDate) {
            endDateInput.setCustomValidity('La data di fine deve essere successiva alla data di inizio');
            endDateInput.classList.add('is-invalid');
            
            // Crea o aggiorna il messaggio di errore
            const feedback = endDateInput.parentNode.querySelector('.invalid-feedback') || 
                           createInvalidFeedback(endDateInput.parentNode);
            feedback.textContent = 'La data di fine deve essere successiva alla data di inizio';
        } else {
            endDateInput.setCustomValidity('');
            endDateInput.classList.remove('is-invalid');
            
            // Rimuovi il messaggio di errore se presente
            const feedback = endDateInput.parentNode.querySelector('.invalid-feedback');
            if (feedback && feedback.dataset.customCreated) {
                feedback.remove();
            }
        }
    }

    /**
     * Crea un elemento per il feedback di errore
     * @param {Element} parent - Elemento parent dove aggiungere il feedback
     * @returns {Element} - Elemento feedback creato
     */
    function createInvalidFeedback(parent) {
        let feedback = parent.querySelector('.invalid-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            feedback.dataset.customCreated = 'true';
            parent.appendChild(feedback);
        }
        return feedback;
    }

    // Validazione campo nome appuntamento
    const meetingNameInput = document.getElementById('meeting_name');
    if (meetingNameInput) {
        meetingNameInput.addEventListener('input', function() {
            if (this.value.trim()) {
                this.classList.remove('is-invalid');
            }
        });
    }

    // Pre-imposta data minima per i campi data (non può essere nel passato)
    const now = new Date();
    const minDateTime = now.toISOString().slice(0, 16); // Format: YYYY-MM-DDTHH:MM
    
    if (startDateInput) {
        startDateInput.setAttribute('min', minDateTime);
    }
    if (endDateInput) {
        endDateInput.setAttribute('min', minDateTime);
    }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

// Export per compatibilità moduli Odoo
export default {
    init: function() {
        console.log('Meeting Create Validation module initialized');
    }
};
