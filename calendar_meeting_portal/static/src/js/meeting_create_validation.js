/** @odoo-module **/

/**
 * Validazione form per creazione appuntamenti nel portale
 * Odoo 18 - Vanilla JavaScript
 */

(function() {
    function init() {
        const meetingForm = document.querySelector('.needs-validation');
        if (!meetingForm) {
            //console.info('meeting_create_validation: .needs-validation not found');
            return; // Non siamo nella pagina giusta, esci
        }

        const partnerSearchInput = document.getElementById('partner_id_search');
        const partnerHiddenInput = document.getElementById('partner_id');
        const partnerListContainer = document.getElementById('partner_list_container');

        // Mapping di partner per ricerca veloce
        let partnerMap = {};
        if (partnerListContainer) {
            const partnerItems = partnerListContainer.querySelectorAll('.partner-item');
            partnerItems.forEach(item => {
                const partnerId = item.dataset.partnerId;
                const name = (item.querySelector('.font-weight-normal') || {}).textContent || '';
                const email = (item.querySelector('.text-muted') || {}).textContent || '';
                if (partnerId) {
                    partnerMap[partnerId] = { name: name.trim(), email: email.trim() };
                }
            });
        }

        function setPartnerValidity(isValid, message) {
            if (!partnerSearchInput) {
                return;
            }

            if (isValid) {
                partnerSearchInput.setCustomValidity('');
                partnerSearchInput.classList.remove('is-invalid');
                partnerSearchInput.classList.add('is-valid');
            } else {
                partnerSearchInput.setCustomValidity(message || 'Seleziona un partecipante valido dalla lista');
                partnerSearchInput.classList.remove('is-valid');
                partnerSearchInput.classList.add('is-invalid');
            }
        }

        function filterPartnerList(searchText) {
            if (!partnerListContainer) return;

            const searchLower = (searchText || '').toLowerCase().trim();
            const partnerItems = partnerListContainer.querySelectorAll('.partner-item');
            
            partnerItems.forEach(item => {
                const name = (item.querySelector('.font-weight-normal') || {}).textContent || '';
                const email = (item.querySelector('.text-muted') || {}).textContent || '';
                const combinedText = (name + ' ' + email).toLowerCase();
                
                if (searchLower === '' || combinedText.includes(searchLower)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        }

        function selectPartner(partnerId, partnerName) {
            if (!partnerHiddenInput || !partnerSearchInput) return;

            partnerHiddenInput.value = String(partnerId);
            partnerSearchInput.value = partnerName || '';
            setPartnerValidity(true);
            
            // Aggiorna la classe di selezione
            if (partnerListContainer) {
                const partnerItems = partnerListContainer.querySelectorAll('.partner-item');
                partnerItems.forEach(item => {
                    if (item.dataset.partnerId === String(partnerId)) {
                        item.style.backgroundColor = '#7c4dff';
                        item.style.color = '#ffffff';
                        item.classList.add('selected');
                    } else {
                        item.style.backgroundColor = '';
                        item.style.color = '';
                        item.classList.remove('selected');
                    }
                });
            }
        }

        if (partnerSearchInput && partnerHiddenInput && partnerListContainer) {
            // Event listener per filtraggio durante la digitazione
            partnerSearchInput.addEventListener('input', function() {
                const searchText = this.value || '';
                filterPartnerList(searchText);
                partnerHiddenInput.value = '';
                partnerSearchInput.classList.remove('is-valid', 'is-invalid');
                partnerSearchInput.setCustomValidity('');
            });

            // Event listener per click sui partner
            const partnerItems = partnerListContainer.querySelectorAll('.partner-item');
            partnerItems.forEach(item => {
                item.addEventListener('click', function(e) {
                    const partnerId = this.dataset.partnerId;
                    const partnerName = (this.querySelector('.font-weight-normal') || {}).textContent || '';
                    selectPartner(partnerId, partnerName.trim());
                });
                
                // Supporto per keyboard (Enter/Space)
                item.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        const partnerId = this.dataset.partnerId;
                        const partnerName = (this.querySelector('.font-weight-normal') || {}).textContent || '';
                        selectPartner(partnerId, partnerName.trim());
                    }
                });
            });

            partnerSearchInput.addEventListener('blur', function() {
                // Se il campo hidden è vuoto, segnala errore
                if (!partnerHiddenInput.value) {
                    setPartnerValidity(false, 'Seleziona un partecipante valido dalla lista');
                }
            });

            // Se il backend ha ripopolato partner_id, ripristina la selezione
            if ((partnerHiddenInput.value || '').trim()) {
                const partnerId = partnerHiddenInput.value;
                if (partnerMap[partnerId]) {
                    const partnerInfo = partnerMap[partnerId];
                    const displayName = partnerInfo.email ? 
                        partnerInfo.name + ' (' + partnerInfo.email + ')' : 
                        partnerInfo.name;
                    selectPartner(partnerId, displayName);
                }
            }
        }

    // Validazione form Bootstrap
    meetingForm.addEventListener('submit', function(event) {
        const partnerOk = (partnerHiddenInput && (partnerHiddenInput.value || '').trim());

        if (!meetingForm.checkValidity() || !partnerOk) {
            event.preventDefault();
            event.stopPropagation();
            if (!partnerOk && partnerSearchInput) {
                setPartnerValidity(false, 'Seleziona un partecipante valido dalla lista');
                partnerSearchInput.focus();
            }
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
