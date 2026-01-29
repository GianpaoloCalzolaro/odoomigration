$(document).ready(function() {

    //if ($('.clinical-portal').length === 0) {
    //    console.info('clinical_portal: no .clinical-portal elements found');
    //    return;
   // }
    
  //  console.log('Clinical Portal JS loaded');
  //  console.log('Found clinical cards:', $('.clinical-card').length);
    
    // Funzione per espandere/collassare le card
    function toggleCard(cardElement) {
        var $card = $(cardElement);
        if (!$card.length) {
            console.warn('toggleCard: card element not found', cardElement);
            return;
        }

        var $content = $card.find('.collapsible-content');
        var $icon = $card.find('.collapse-icon');

        if (!$content.length || !$icon.length) {
            console.warn('toggleCard: missing content or icon in', $card.attr('id'));
        }

        //console.log('Toggling card:', $card.attr('id'));
        
        if ($card.hasClass('collapsed')) {
            // Espandi
            $content.slideDown(300);
            $card.removeClass('collapsed');
            $icon.removeClass('fa-chevron-down').addClass('fa-chevron-up');
           // console.log('Card expanded');
        } else {
            // Collassa
            $content.slideUp(300);
            $card.addClass('collapsed');
            $icon.removeClass('fa-chevron-up').addClass('fa-chevron-down');
           // console.log('Card collapsed');
        }
    }
    
    // Event delegation per gestire i click sui header delle card
    $(document).on('click', '.clinical-card .card-header', function(e) {
        e.preventDefault();
        e.stopPropagation();

        var $card = $(this).closest('.clinical-card');
        if ($card.length) {
            // console.log('Card header clicked');
            toggleCard($card);
        } else {
            console.warn('Card header clicked but card not found');
        }
    });
    
    // Funzione globale per compatibilità con onclick
    window.toggleCard = function(header) {
        // console.log('Global toggleCard called');
        var $card = $(header).closest('.clinical-card');
        toggleCard($card);
    };
    
    // Expand only the first card
    function expandFirstCard() {
        var $first = $('.clinical-card').first();
        if ($first.length) {
           // console.log('Expanding first card:', $first.attr('id'));
            $first.removeClass('collapsed');
            $first.find('.collapsible-content').show();
            $first.find('.collapse-icon').removeClass('fa-chevron-down').addClass('fa-chevron-up');
        } else {
            console.warn('expandFirstCard: no cards found');
        }
    }
    
    // Inizializza le card come collassate
    function initializeCards() {
        //console.log('Initializing cards');
        var $cards = $('.clinical-card');

        if (!$cards.length) {
            console.warn('initializeCards: no cards found');
            return;
        }

        $cards.addClass('collapsed');
        $cards.find('.collapsible-content').hide();
        $cards.find('.collapse-icon').removeClass('fa-chevron-up').addClass('fa-chevron-down');

        expandFirstCard();
    }
    
    
    // Gestione campi condizionali (checkbox che mostrano/nascondono altri campi)
    $(document).on('change', 'input[type="checkbox"]', function() {
        var $checkbox = $(this);
        var fieldName = $checkbox.attr('name');
        
        // console.log('Checkbox changed:', fieldName, $checkbox.is(':checked'));
        
        // Gestisci campi condizionali specifici
        var conditionalFields = {
            'previous_suicide_attempts': 'suicide_attempts_details',
            'self_harm_behaviors': 'self_harm_details',
            'aggressive_behaviors': 'aggressive_details',
            'family_psychiatric_history': 'family_history_details',
            'chronic_diseases': 'chronic_diseases_details',
            'previous_surgeries': 'surgeries_details',
            'allergies': 'allergies_details',
            'smoking': 'smoking_details',
            'alcohol': 'alcohol_details',
            'illegal_drugs': 'drugs_details',
            'suicide_means_available': 'suicide_means_details',
            'aggression_means_available': 'aggression_means_details'
        };
        
        if (conditionalFields[fieldName]) {
            var targetField = conditionalFields[fieldName];
            var $details = $('textarea[name="' + targetField + '"], input[name="' + targetField + '"]').closest('.form-group');
            
            if ($checkbox.is(':checked')) {
                $details.slideDown(200);
            } else {
                $details.slideUp(200);
                $details.find('textarea, input').val('');
            }
        }
    });
    
    // Gestione campi select condizionali
    $(document).on('change', 'select', function() {
        var $select = $(this);
        var fieldName = $select.attr('name');
        var value = $select.val();
        
        // console.log('Select changed:', fieldName, value);
        
        // Gestisci visibilità campi basata su selezioni
        if (fieldName === 'suicidal_ideation') {
            var $relatedFields = $('select[name="suicide_planning"], textarea[name="suicide_plan_details"], select[name="suicide_intention"], input[name="suicide_means_available"], textarea[name="suicide_means_details"], textarea[name="suicide_risk_factors"]').closest('.form-group');
            
            if (value && value !== 'absent') {
                $relatedFields.slideDown(200);
            } else {
                $relatedFields.slideUp(200);
            }
        }
        
        if (fieldName === 'aggressive_ideation') {
            var $relatedFields = $('textarea[name="aggression_target"], select[name="aggression_planning"], textarea[name="aggression_plan_details"], select[name="aggression_intention"], input[name="aggression_means_available"], textarea[name="aggression_means_details"], textarea[name="aggression_risk_factors"]').closest('.form-group');
            
            if (value && value !== 'absent') {
                $relatedFields.slideDown(200);
            } else {
                $relatedFields.slideUp(200);
            }
        }
        
        if (fieldName === 'pregnancy_breastfeeding') {
            var $weeksField = $('input[name="pregnancy_weeks"]').closest('.form-group');

            if (value && value !== 'not_applicable') {
                $weeksField.slideDown(200);
            } else {
                $weeksField.slideUp(200);
            }
        }
    });

    // Calcolo automatico dell'età
    function computeAge(dateStr) {
        if (!dateStr) {
            return '';
        }
        var today = new Date();
        var birth = new Date(dateStr);
        var age = today.getFullYear() - birth.getFullYear();
        var m = today.getMonth() - birth.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
            age--;
        }
        return age;
    }

    $(document).on('change', 'input[name="birth_date"]', function() {
        var age = computeAge($(this).val());
        $('#age_input').val(age);
    });
    
    
    var selectedProfessionalId = null;
    var loadingIndicator = $('#professionalLoading');
    var tagsIndicator = $('#tagsLoading');

    function showLoading() {
        if (loadingIndicator.length) {
            loadingIndicator.removeClass('d-none');
        }
        if (tagsIndicator.length) {
            tagsIndicator.removeClass('d-none');
        }
    }

    function hideLoading() {
        if (loadingIndicator.length) {
            loadingIndicator.addClass('d-none');
        }
        if (tagsIndicator.length) {
            tagsIndicator.addClass('d-none');
        }
    }

    function apiCall(route, params) {
        if (window.odoo && odoo.rpc) {
            return odoo.rpc.query({route: route, params: params || {}});
        }
        var url = route;
        if (params && Object.keys(params).length) {
            url += '?' + new URLSearchParams(params).toString();
        }
        return fetch(url, {credentials: 'same-origin'}).then(function(r){return r.json();});
    }

    function rpcCall(params) {
        return apiCall('/my/search/professionals', params);
    }

   function updateProfessionalsTable(list) {
       var $tbody = $('#professionalsTableBody');
       $tbody.empty();
        if(!list.length){
            $tbody.append('<tr><td colspan="8" class="text-center no-result">Nessun professionista trovato</td></tr>');
            return;
        }
        list.forEach(function(p){
            var $row = $('<tr>');
            $row.append($('<td>').text(p.name));
            $row.append($('<td>').text(p.job_title || ''));
            var tagText = (p.tags || []).map(function(t){return t.name;}).join(', ');
            $row.append($('<td>').text(tagText));
            $row.append($('<td>').text(p.region || ''));
            $row.append($('<td>').text(p.mobile_phone || 'N/D'));
            $row.append($('<td>').text(p.work_email || 'N/D'));
            $row.append($('<td>').text(p.limite_incarichi_raggiunto ? 'Sì' : 'No'));
            var $btn = $('<button type="button" class="btn btn-sm btn-primary select-professional">Seleziona</button>');
            $btn.attr('data-id', p.id)
                .attr('data-name', p.name)
                .attr('data-job', p.job_id)
                .attr('data-job-name', p.job_name);
            $row.append($('<td>').append($btn));
            $tbody.append($row);
        });
    }

    function populateRegions(data) {
        var $region = $('#regionFilter');
        if ($region.children().length <= 1) {
            data.forEach(function(r){
                $region.append($('<option>', {value: r, text: r}));
            });
        }
    }

    function populateDepartments(list){
        var $department = $('#departmentFilter');
        $department.empty().append($('<option>', {value:'', text:'Seleziona dipartimento'}));
        list.forEach(function(d){
            $department.append($('<option>', {value:d.id, text:d.name}));
        });
    }

    function populateTags(list){
        var $tags = $('#tagsFilter');
        $tags.empty();
        list.forEach(function(t){
            $tags.append($('<option>', {value:t.id, text:t.name}));
        });
    }

    function loadModalData() {
        showLoading();
        rpcCall({}).then(function(data){
            populateRegions(data.regions);
            hideLoading();
        }).catch(function(){
            alert('Errore nel caricamento dei filtri');
            hideLoading();
        });
    }

    function loadInitialFilters(){
        showLoading();
        Promise.all([
            apiCall('/my/search/departments'),
            apiCall('/my/search/tags')
        ]).then(function(results){
            if(results[0].departments){
                populateDepartments(results[0].departments);
            }
            if(results[1].tags){
                populateTags(results[1].tags);
            }
            hideLoading();
            loadModalData();
        }).catch(function(){
            alert('Errore iniziale caricamento filtri');
            hideLoading();
        });
    }

    function handleDepartmentChange(){
        var depId = $('#departmentFilter').val();
        var $job = $('#jobFilter');
        $job.empty().append($('<option>', {value:'', text:'Seleziona tipo professionista'}));
        if(!depId){
            return;
        }
        apiCall('/my/search/jobs', {department_id: depId}).then(function(data){
            (data.jobs || []).forEach(function(j){
                $job.append($('<option>', {value:j.id, text:j.name}));
            });
        }).catch(function(){
            alert('Errore nel caricamento dei ruoli');
        });
    }

    function getSelectedTagIds(){
        var vals = $('#tagsFilter').val();
        return vals ? vals.map(function(v){ return parseInt(v); }) : [];
    }

    function renderSelectedTags(){
        var $container = $('#selectedTags');
        $container.empty();
        $('#tagsFilter option:selected').each(function(){
            var id = $(this).val();
            var text = $(this).text();
            var $badge = $('<span class="badge bg-secondary me-1 mb-1">'+text+' <i class="fa fa-times remove-tag" data-id="'+id+'"></i></span>');
            $container.append($badge);
        });
    }

    function filterProfessionals() {
        var dep = $('#departmentFilter').val();
        if(!dep){
            dep = 5;
        }
        var params = {department_id: dep};
        var r = $('#regionFilter').val();
        var j = $('#jobFilter').val();
        var tags = getSelectedTagIds();
        if (r) { params.region = r; }
        if (j) { params.job_id = j; }
        if (tags.length) { params.category_ids = tags; }
        showLoading();
        rpcCall(params).then(function(data){
            populateRegions(data.regions);
            updateProfessionalsTable(data.professionals);
            hideLoading();
        }).catch(function(err){
            alert('Errore durante la ricerca professionisti');
            hideLoading();
        });
    }

    $('body').on('click', '#selectProfessionalBtn', function(){
        loadInitialFilters();
    });

    $('body').on('change', '#departmentFilter', function(){
        handleDepartmentChange();
    });

    $('body').on('change', '#tagsFilter', function(){
        renderSelectedTags();
    });

    $('body').on('click', '#searchButton', function(){
        filterProfessionals();
    });

    $('body').on('click', '#selectedTags .remove-tag', function(){
        var id = $(this).data('id');
        $('#tagsFilter option[value="'+id+'"]').prop('selected', false);
        renderSelectedTags();
    });

    $('body').on('click', '.select-professional', function(){
        var id = $(this).data('id');
        var name = $(this).data('name');
        var job = $(this).data('job');
        var jobName = $(this).data('job-name');
        $('#professionalName').val(name);
        $('#professionalId').val(id);
        if(job){
            $('#typeProfessionalId').val(job);
            $('#typeProfessionalName').val(jobName || '');
        }
        var modalEl = document.getElementById('professionalModal');
        var modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) { modal.hide(); }
    });

    $('#edit_contact_form').on('submit', function(e){
        var valid = true;
        if (!$('#professionalId').val()) {
            $('#professionalName').addClass('is-invalid');
            valid = false;
        }
        if (!$('#typeProfessionalId').val()) {
            $('#typeProfessionalName').addClass('is-invalid');
            valid = false;
        }
        if (!valid) {
            e.preventDefault();
        }
    });

    // Inizializza tutto
    initializeCards();
    
    // Gestisci i campi condizionali esistenti al caricamento della pagina
    $('input[type="checkbox"]:checked').each(function() {
        $(this).trigger('change');
    });
    
    $('select').each(function() {
        if ($(this).val()) {
            $(this).trigger('change');
        }
    });
});
