from odoo import models, fields, api


class ClinicalSheet(models.Model):
    _name = 'clinical.sheet'
    _description = 'Scheda Clinica Paziente'
    _order = 'create_date desc'

    partner_id = fields.Many2one('res.partner', string='Paziente', required=True, ondelete='cascade',
                                domain=[('is_patient', '=', True)])
    name = fields.Char(related='partner_id.name', store=True, readonly=True)
    active = fields.Boolean(default=True)

    # --- Campi migrati da res.partner e nuovi campi ---
    # Sezione 1: Consultazione
    reason_for_consultation = fields.Text('Motivo della consulenza/presa in carico')
    symptoms_duration = fields.Char('Durata dei sintomi')
    triggering_factors = fields.Text('Fattori scatenanti percepiti')
    daily_life_impact = fields.Text('Impatto sulla vita quotidiana')

    # Sezione 4: Sintomi Attuali (campi esistenti)
    problem_description = fields.Text('Descrizione del problema presentato')
    symptoms_onset = fields.Date('Data di inizio dei sintomi')
    current_issues = fields.Text('Problematiche attuali riferite dal paziente')

    # Sezione 3: Sociale/Familiare (campi esistenti)
    family_context = fields.Text('Contesto familiare rilevante')
    social_context = fields.Text('Contesto sociale e relazionale')
    work_context = fields.Text('Contesto lavorativo o scolastico')

    # Sezione 2.1: Anamnesi Psichiatrica
    previous_psychotherapies = fields.Text('Trattamenti precedentemente ricevuti')
    previous_psychiatric_diagnoses = fields.Text('Diagnosi psichiatriche pregresse')
    previous_medications = fields.Text('Farmaci precedenti')
    psychiatric_hospitalizations = fields.Text('Ricoveri psichiatrici')
    previous_suicide_attempts = fields.Boolean('Tentativi suicidio pregressi')
    suicide_attempts_details = fields.Text('Dettagli tentativi suicidio')
    self_harm_behaviors = fields.Boolean('Comportamenti autolesivi')
    self_harm_details = fields.Text('Dettagli autolesioni')
    aggressive_behaviors = fields.Boolean('Comportamenti aggressivi pregressi')
    aggressive_details = fields.Text('Dettagli comportamenti aggressivi')
    family_psychiatric_history = fields.Boolean('Storia familiare psichiatrica')
    family_history_details = fields.Text('Dettagli storia familiare')

    # Sezione 2.2: Anamnesi Medica
    chronic_diseases = fields.Boolean('Malattie croniche attuali')
    chronic_diseases_details = fields.Text('Dettagli malattie croniche')
    previous_surgeries = fields.Boolean('Interventi chirurgici pregressi')
    surgeries_details = fields.Text('Dettagli interventi')
    current_medications = fields.Text('Farmaci attuali')
    allergies = fields.Boolean('Allergie')
    allergies_details = fields.Text('Dettagli allergie')
    pregnancy_breastfeeding = fields.Selection([
        ('not_applicable', 'Non applicabile'),
        ('pregnant', 'Gravidanza'),
        ('breastfeeding', 'Allattamento')
    ], string='Gravidanza/Allattamento')
    pregnancy_weeks = fields.Char('Settimane/Mesi')

    # Sezione 2.3: Sostanze
    smoking = fields.Boolean('Fumo')
    smoking_details = fields.Text('Dettagli fumo')
    alcohol = fields.Boolean('Consumo alcol')
    alcohol_details = fields.Text('Dettagli alcol')
    illegal_drugs = fields.Boolean('Uso sostanze')
    drugs_details = fields.Text('Dettagli sostanze')

    # Sezione 3: Sociale/Familiare (nuovi campi)
    living_situation = fields.Selection([
        ('alone', 'Vive da solo/a'),
        ('family', 'Con famiglia d\'origine'),
        ('partner', 'Con partner'),
        ('children', 'Con figli'),
        ('facility', 'Struttura protetta'),
        ('other', 'Altro')
    ], string='Situazione abitativa')
    social_support = fields.Selection([
        ('adequate', 'Adeguato'),
        ('poor', 'Scarso'),
        ('absent', 'Assente')
    ], string='Supporto sociale')
    social_support_description = fields.Text('Descrizione supporto')
    significant_relationships = fields.Text('Relazioni significative')
    developmental_history = fields.Text('Storia evolutiva')
    cultural_aspects = fields.Text('Aspetti culturali/spirituali')

    # Sezione 4: Sintomi Attuali (nuovi campi)
    sadness_depression = fields.Text('Tristezza/Depressione')
    anhedonia = fields.Text('Perdita interesse/piacere')
    irritability_anger = fields.Text('Irritabilità/rabbia')
    euphoria_elevated_mood = fields.Text('Euforia/umore elevato')
    emotional_lability = fields.Text('Labilità emotiva')
    generalized_anxiety = fields.Text('Ansia generalizzata')
    panic_attacks = fields.Text('Attacchi di panico')
    phobias = fields.Text('Fobie')
    ocd_symptoms = fields.Text('Sintomi ossessivo-compulsivi')
    ptsd_symptoms = fields.Text('Sintomi post-traumatici')
    hallucinations = fields.Text('Allucinazioni')
    delusions = fields.Text('Deliri')
    thought_disorganization = fields.Text('Disorganizzazione pensiero')
    concentration_difficulties = fields.Text('Difficoltà concentrazione')
    memory_problems = fields.Text('Problemi memoria')
    planning_difficulties = fields.Text('Difficoltà pianificazione')
    sleep_disturbances = fields.Text('Disturbi del sonno')
    appetite_changes = fields.Text('Alterazioni appetito')
    fatigue = fields.Text('Fatica/mancanza energia')
    somatic_symptoms = fields.Text('Sintomi somatici')

    # Sezione 5: Esame Obiettivo Psichico
    appearance_hygiene = fields.Text('Abbigliamento e igiene')
    attitude = fields.Text('Atteggiamento')
    mimics_gestures = fields.Text('Mimica e gestualità')
    psychomotor_activity = fields.Text('Attività psicomotoria')
    language_quality = fields.Text('Qualità linguaggio')
    language_quantity = fields.Text('Quantità linguaggio')
    language_tone = fields.Text('Tono/volume')
    reported_mood = fields.Text('Umore riferito')
    observed_affect = fields.Text('Affettività osservata')
    thought_form = fields.Text('Forma del pensiero')
    thought_content = fields.Text('Contenuto del pensiero')
    exam_hallucinations = fields.Text('Allucinazioni (esame)')
    illusions = fields.Text('Illusioni')
    derealization = fields.Text('Derealizzazione/Depersonalizzazione')
    orientation = fields.Text('Orientamento')
    attention_concentration = fields.Text('Attenzione e concentrazione')
    memory_exam = fields.Text('Memoria')
    abstraction_capacity = fields.Text('Capacità di astrazione')
    insight = fields.Selection([
        ('good', 'Buono'),
        ('partial', 'Parziale'),
        ('absent', 'Assente')
    ], string='Insight')
    judgment = fields.Selection([
        ('good', 'Buono'),
        ('partial', 'Parziale'),
        ('compromised', 'Compromesso')
    ], string='Giudizio')

    # Sezione 6: Valutazione Rischio
    suicidal_ideation = fields.Selection([
        ('absent', 'Assente'),
        ('mild', 'Lieve'),
        ('moderate', 'Moderata'),
        ('severe', 'Grave')
    ], string='Ideazione suicidaria')
    suicide_planning = fields.Selection([
        ('absent', 'Assente'),
        ('undefined', 'Indefinita'),
        ('defined', 'Definita')
    ], string='Pianificazione suicidaria')
    suicide_plan_details = fields.Text('Dettagli pianificazione')
    suicide_intention = fields.Selection([
        ('absent', 'Assente'),
        ('low', 'Bassa'),
        ('moderate', 'Moderata'),
        ('high', 'Alta')
    ], string='Intenzione suicidaria')
    suicide_means_available = fields.Boolean('Mezzi disponibili')
    suicide_means_details = fields.Text('Dettagli mezzi')
    suicide_risk_factors = fields.Text('Fattori rischio aggiuntivi')

    aggressive_ideation = fields.Selection([
        ('absent', 'Assente'),
        ('mild', 'Lieve'),
        ('moderate', 'Moderata'),
        ('severe', 'Grave')
    ], string='Ideazione aggressiva')
    aggression_target = fields.Text('Verso chi')
    aggression_planning = fields.Selection([
        ('absent', 'Assente'),
        ('undefined', 'Indefinita'),
        ('defined', 'Definita')
    ], string='Pianificazione aggressiva')
    aggression_plan_details = fields.Text('Dettagli pianificazione')
    aggression_intention = fields.Selection([
        ('absent', 'Assente'),
        ('low', 'Bassa'),
        ('moderate', 'Moderata'),
        ('high', 'Alta')
    ], string='Intenzione aggressiva')
    aggression_means_available = fields.Boolean('Mezzi aggressione disponibili')
    aggression_means_details = fields.Text('Dettagli mezzi aggressione')
    aggression_risk_factors = fields.Text('Fattori rischio aggressivo')

    hygiene_risk = fields.Boolean('Rischio igiene')
    nutrition_risk = fields.Boolean('Rischio alimentazione')
    medication_risk = fields.Boolean('Rischio farmaci')
    financial_risk = fields.Boolean('Rischio finanze')
    housing_risk = fields.Boolean('Rischio abitazione')
    exploitation_vulnerability = fields.Boolean('Vulnerabilità sfruttamento')
    self_care_impact = fields.Text('Impatto capacità auto-cura')

    # Sezione 7: Fattori Protettivi
    individual_protective_factors = fields.Text('Fattori individuali')
    social_protective_factors = fields.Text('Supporto sociale')
    treatment_engagement = fields.Text('Coinvolgimento trattamento')
    stability_factors = fields.Text('Stabilità generale')

    # Sezione 8: Aspettative
    patient_expectations = fields.Text('Aspettative paziente')

    # Sezione 9: Impressione Clinica
    clinical_summary = fields.Text('Sintesi dati principali')
    diagnostic_hypotheses = fields.Text('Ipotesi diagnostiche')
    main_problem_areas = fields.Text('Aree problematiche principali')
    relevant_risk_protective_factors = fields.Text('Fattori rilevanti')

    # Sezione 10: Diagnosi e Piano
    primary_diagnosis = fields.Char('Diagnosi primaria')
    secondary_diagnosis = fields.Char('Diagnosi secondaria')
    diagnosis_code = fields.Char('Codice diagnosi (es. da DSM-5 o ICD-10)')
    diagnostic_criteria = fields.Text('Criteri diagnostici utilizzati')
    differential_diagnosis = fields.Text('Diagnosi differenziale considerata')
    comorbidity = fields.Text('Comorbilità e sintomi secondari')
    risk_assessment = fields.Selection([
        ('low', 'Basso'),
        ('medium', 'Medio'),
        ('high', 'Alto')
    ], string='Valutazione del rischio')
    treatment_goals = fields.Text('Obiettivi del trattamento')
    treatment_plan = fields.Text('Piano di trattamento proposto')
    overall_completion = fields.Float(
    string='Completamento complessivo',
    compute='_compute_overall_completion',
    store=True
)

    # Computed fields
    section_1_completion = fields.Float('Completamento Consultazione', compute='_compute_section_1_completion', store=True)
    section_2_completion = fields.Float('Completamento Anamnesi Psichiatrica', compute='_compute_section_2_completion', store=True)
    section_3_completion = fields.Float('Completamento Anamnesi Medica', compute='_compute_section_3_completion', store=True)
    section_4_completion = fields.Float('Completamento Sostanze', compute='_compute_section_4_completion', store=True)
    section_5_completion = fields.Float('Completamento Sociale/Familiare', compute='_compute_section_5_completion', store=True)
    section_6_completion = fields.Float('Completamento Sintomi Attuali', compute='_compute_section_6_completion', store=True)
    section_7_completion = fields.Float('Completamento Esame Psichico', compute='_compute_section_7_completion', store=True)
    section_8_completion = fields.Float('Completamento Valutazione Rischio', compute='_compute_section_8_completion', store=True)
    section_9_completion = fields.Float('Completamento Fattori Protettivi', compute='_compute_section_9_completion', store=True)
    section_10_completion = fields.Float('Completamento Conclusioni', compute='_compute_section_10_completion', store=True)


    @api.depends('reason_for_consultation', 'symptoms_duration', 'triggering_factors', 'daily_life_impact')
    def _compute_section_1_completion(self):
        for record in self:
            fields_set = [record.reason_for_consultation, record.symptoms_duration,
                          record.triggering_factors, record.daily_life_impact]
            filled = sum(1 for f in fields_set if f)
            record.section_1_completion = (filled / len(fields_set)) * 100 if fields_set else 0

    @api.depends('previous_psychotherapies', 'previous_psychiatric_diagnoses', 'previous_medications',
                 'psychiatric_hospitalizations', 'previous_suicide_attempts', 'suicide_attempts_details',
                 'self_harm_behaviors', 'self_harm_details', 'aggressive_behaviors', 'aggressive_details',
                 'family_psychiatric_history', 'family_history_details')
    def _compute_section_2_completion(self):
        for record in self:
            fields_set = [
                record.previous_psychotherapies,
                record.previous_psychiatric_diagnoses,
                record.previous_medications,
                record.psychiatric_hospitalizations,
            ]
            if record.previous_suicide_attempts:
                fields_set.append(record.suicide_attempts_details)
            if record.self_harm_behaviors:
                fields_set.append(record.self_harm_details)
            if record.aggressive_behaviors:
                fields_set.append(record.aggressive_details)
            if record.family_psychiatric_history:
                fields_set.append(record.family_history_details)
            filled = sum(1 for f in fields_set if f)
            total = len(fields_set)
            record.section_2_completion = (filled / total) * 100 if total else 0


    @api.depends('chronic_diseases', 'chronic_diseases_details',
                 'previous_surgeries', 'surgeries_details', 'current_medications',
                 'allergies', 'allergies_details',
                 'pregnancy_breastfeeding', 'pregnancy_weeks')
    def _compute_section_3_completion(self):
        for record in self:
            fields_set = [record.chronic_diseases,
                          record.previous_surgeries,
                          record.current_medications,
                          record.allergies,
                          record.pregnancy_breastfeeding]
            if record.chronic_diseases:
                fields_set.append(record.chronic_diseases_details)
            if record.previous_surgeries:
                fields_set.append(record.surgeries_details)
            if record.allergies:
                fields_set.append(record.allergies_details)
            if record.pregnancy_breastfeeding and record.pregnancy_breastfeeding != 'not_applicable':
                fields_set.append(record.pregnancy_weeks)
            filled = sum(1 for f in fields_set if f)
            record.section_3_completion = (filled / len(fields_set)) * 100 if fields_set else 0

    @api.depends('smoking', 'smoking_details', 'alcohol', 'alcohol_details',
                 'illegal_drugs', 'drugs_details')
    def _compute_section_4_completion(self):
        for record in self:
            fields_set = [record.smoking, record.alcohol, record.illegal_drugs]
            if record.smoking:
                fields_set.append(record.smoking_details)
            if record.alcohol:
                fields_set.append(record.alcohol_details)
            if record.illegal_drugs:
                fields_set.append(record.drugs_details)
            filled = sum(1 for f in fields_set if f)
            record.section_4_completion = (filled / len(fields_set)) * 100 if fields_set else 0

    @api.depends('living_situation', 'social_support', 'social_support_description',
                 'significant_relationships', 'developmental_history',
                 'family_context', 'social_context', 'work_context',
                 'cultural_aspects')
    def _compute_section_5_completion(self):
        for record in self:
            fields_set = [record.living_situation, record.social_support,
                          record.social_support_description,
                          record.significant_relationships,
                          record.developmental_history,
                          record.family_context, record.social_context,
                          record.work_context, record.cultural_aspects]
            filled = sum(1 for f in fields_set if f)
            record.section_5_completion = (filled / len(fields_set)) * 100 if fields_set else 0

    @api.depends('problem_description', 'symptoms_onset', 'current_issues',
                 'sadness_depression', 'anhedonia', 'irritability_anger',
                 'euphoria_elevated_mood', 'emotional_lability', 'generalized_anxiety',
                 'panic_attacks', 'phobias', 'ocd_symptoms', 'ptsd_symptoms',
                 'hallucinations', 'delusions', 'thought_disorganization',
                 'concentration_difficulties', 'memory_problems', 'planning_difficulties',
                 'sleep_disturbances', 'appetite_changes', 'fatigue', 'somatic_symptoms')
    def _compute_section_6_completion(self):
        for record in self:
            fields_set = [record.problem_description, record.symptoms_onset,
                          record.current_issues, record.sadness_depression,
                          record.anhedonia, record.irritability_anger,
                          record.euphoria_elevated_mood, record.emotional_lability,
                          record.generalized_anxiety, record.panic_attacks,
                          record.phobias, record.ocd_symptoms, record.ptsd_symptoms,
                          record.hallucinations, record.delusions, record.thought_disorganization,
                          record.concentration_difficulties, record.memory_problems,
                          record.planning_difficulties, record.sleep_disturbances,
                          record.appetite_changes, record.fatigue, record.somatic_symptoms]
            filled = sum(1 for f in fields_set if f)
            record.section_6_completion = (filled / len(fields_set)) * 100 if fields_set else 0

    @api.depends('appearance_hygiene', 'attitude', 'mimics_gestures',
                 'psychomotor_activity', 'language_quality', 'language_quantity',
                 'language_tone', 'reported_mood', 'observed_affect', 'thought_form',
                 'thought_content', 'exam_hallucinations', 'illusions', 'derealization',
                 'orientation', 'attention_concentration', 'memory_exam',
                 'abstraction_capacity', 'insight', 'judgment')
    def _compute_section_7_completion(self):
        for record in self:
            fields_set = [record.appearance_hygiene, record.attitude, record.mimics_gestures,
                          record.psychomotor_activity, record.language_quality,
                          record.language_quantity, record.language_tone, record.reported_mood,
                          record.observed_affect, record.thought_form, record.thought_content,
                          record.exam_hallucinations, record.illusions, record.derealization,
                          record.orientation, record.attention_concentration, record.memory_exam,
                          record.abstraction_capacity, record.insight, record.judgment]
            filled = sum(1 for f in fields_set if f)
            record.section_7_completion = (filled / len(fields_set)) * 100 if fields_set else 0

    @api.depends('risk_assessment', 'suicidal_ideation', 'suicide_planning',
                 'suicide_plan_details', 'suicide_intention', 'suicide_means_available',
                 'suicide_means_details', 'suicide_risk_factors', 'aggressive_ideation',
                 'aggression_target', 'aggression_planning', 'aggression_plan_details',
                 'aggression_intention', 'aggression_means_available',
                 'aggression_means_details', 'aggression_risk_factors',
                 'hygiene_risk', 'nutrition_risk', 'medication_risk',
                 'financial_risk', 'housing_risk', 'exploitation_vulnerability',
                 'self_care_impact')
    def _compute_section_8_completion(self):
        for record in self:
            fields_set = [record.risk_assessment, record.suicidal_ideation,
                          record.suicide_planning, record.suicide_intention,
                          record.suicide_means_available, record.suicide_risk_factors,
                          record.aggressive_ideation, record.aggression_planning,
                          record.aggression_intention, record.aggression_means_available,
                          record.aggression_risk_factors, record.hygiene_risk,
                          record.nutrition_risk, record.medication_risk,
                          record.financial_risk, record.housing_risk,
                          record.exploitation_vulnerability, record.self_care_impact]
            if record.suicidal_ideation and record.suicidal_ideation != 'absent':
                fields_set.append(record.suicide_plan_details)
            if record.suicide_means_available:
                fields_set.append(record.suicide_means_details)
            if record.aggressive_ideation and record.aggressive_ideation != 'absent':
                fields_set.append(record.aggression_target)
            if record.aggression_planning and record.aggression_planning != 'absent':
                fields_set.append(record.aggression_plan_details)
            if record.aggression_means_available:
                fields_set.append(record.aggression_means_details)
            filled = sum(1 for f in fields_set if f)
            record.section_8_completion = (filled / len(fields_set)) * 100 if fields_set else 0

    @api.depends('individual_protective_factors', 'social_protective_factors',
                 'treatment_engagement', 'stability_factors')
    def _compute_section_9_completion(self):
        for record in self:
            fields_set = [record.individual_protective_factors,
                          record.social_protective_factors,
                          record.treatment_engagement,
                          record.stability_factors]
            filled = sum(1 for f in fields_set if f)
            record.section_9_completion = (filled / len(fields_set)) * 100 if fields_set else 0

    @api.depends('patient_expectations', 'clinical_summary', 'diagnostic_hypotheses',
                 'main_problem_areas', 'relevant_risk_protective_factors',
                 'primary_diagnosis', 'secondary_diagnosis', 'diagnosis_code',
                 'diagnostic_criteria', 'differential_diagnosis', 'comorbidity',
                 'treatment_plan')
    def _compute_section_10_completion(self):
        for record in self:
            fields_set = [record.patient_expectations, record.clinical_summary,
                          record.diagnostic_hypotheses, record.main_problem_areas,
                          record.relevant_risk_protective_factors, record.primary_diagnosis,
                          record.secondary_diagnosis, record.diagnosis_code,
                          record.diagnostic_criteria, record.differential_diagnosis,
                          record.comorbidity, record.treatment_plan]
            filled = sum(1 for f in fields_set if f)
            record.section_10_completion = (filled / len(fields_set)) * 100 if fields_set else 0

    @api.depends('section_1_completion', 'section_2_completion', 'section_3_completion',
                 'section_4_completion', 'section_5_completion', 'section_6_completion',
                 'section_7_completion', 'section_8_completion', 'section_9_completion',
                 'section_10_completion')
    def _compute_overall_completion(self):
        for record in self:
            vals = [
                record.section_1_completion,
                record.section_2_completion,
                record.section_3_completion,
                record.section_4_completion,
                record.section_5_completion,
                record.section_6_completion,
                record.section_7_completion,
                record.section_8_completion,
                record.section_9_completion,
                record.section_10_completion,
            ]
            # Calcola la media delle sezioni completate
            record.overall_completion = sum(vals) / len(vals) if vals else 0
