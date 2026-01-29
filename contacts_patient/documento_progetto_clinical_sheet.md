---

## **4. MODIFICHE VISTE BACKEND**

### **4.1 Vista Partner Principale**
**File**: `views/res_partner_views.xml`

#### **Modifica al Tab "Cartella clinica" → "Dati clinici"**
```xml
<page string="Dati clinici" invisible="not is_patient">
    <div class="oe_button_box">
        <button name="action_open_clinical_sheet" 
                type="object" 
                class="oe_stat_button" 
                icon="fa-folder-medical"
                invisible="not has_clinical_sheet">
            <div class="o_field_widget">
                <span class="o_stat_text">Apri</span>
                <span class="o_stat_text">Cartella Clinica</span>
            </div>
        </button>
        
        <button name="action_create_clinical_sheet" 
                type="object" 
                class="oe_stat_button" 
                icon="fa-plus"
                invisible="has_clinical_sheet">
            <div class="o_field_widget">
                <span class="o_stat_text">Crea</span>
                <span class="o_stat_text">Cartella Clinica</span>
            </div>
        </button>
    </div>
    
    <group string="Équipe" col="2">
        <field name="tutor"/>
        <field name="date_tutor_assignment"/>
        <field name="type_professional"/>
        <field name="professional"/>
        <field name="date_professional_assignment"/>
        <field name="date_taken_charge"/>
    </group>
    
    <group string="Stato Cartella Clinica" col="2" invisible="not has_clinical_sheet">
        <field name="has_clinical_sheet" invisible="1"/>
        <field name="clinical_sheet_id" invisible="1"/>
        <!-- Mostra info completamento se scheda esiste -->
        <label string="Completamento Generale:"/>
        <div>
            <field name="clinical_sheet_id.overall_completion" widget="progressbar"/>
        </div>
    </group>
</page>
```

### **4.2 Nuova Vista "Cartella Clinica"**
**File**: `views/clinical_sheet_view.xml`

#### **Window Action per Cartella Clinica**
```xml
<record id="action_clinical_sheet" model="ir.actions.act_window">
    <field name="name">Cartella Clinica</field>
    <field name="res_model">clinical.sheet</field>
    <field name="view_mode">form</field>
    <field name="view_id" ref="view_clinical_sheet_form"/>
    <field name="target">current</field>
</record>
```

#### **Vista Form Completa per clinical.sheet**
```xml
<record id="view_clinical_sheet_form" model="ir.ui.view">
    <field name="name">clinical.sheet.form</field>
    <field name="model">clinical.sheet</field>
    <field name="arch" type="xml">
        <form string="Cartella Clinica">
            <!-- Header con dati paziente -->
            <header>
                <div class="oe_title">
                    <h1>
                        <span>Cartella Clinica - </span>
                        <field name="name" readonly="1" class="oe_inline"/>
                    </h1>
                </div>
            </header>
            
            <sheet>
                <!-- Informazioni paziente in evidenza -->
                <div class="oe_button_box">
                    <button class="oe_stat_button" icon="fa-user" type="object" name="action_view_partner">
                        <div class="o_field_widget">
                            <span class="o_stat_text">Vai al</span>
                            <span class="o_stat_text">Contatto</span>
                        </div>
                    </button>
                </div>
                
                <group class="patient_summary" col="4">
                    <field name="partner_id" readonly="1"/>
                    <field name="partner_id.email" readonly="1"/>
                    <field name="partner_id.phone" readonly="1"/>
                    <field name="partner_id.date_taken_charge" readonly="1"/>
                </group>
                
                <!-- Progress indicators -->
                <group string="Stato Completamento Sezioni" col="5">
                    <field name="section_1_completion" widget="progressbar"/>
                    <field name="section_2_completion" widget="progressbar"/>
                    <field name="section_3_completion" widget="progressbar"/>
                    <field name="section_4_completion" widget="progressbar"/>
                    <field name="section_5_completion" widget="progressbar"/>
                    <field name="section_6_completion" widget="progressbar"/>
                    <field name="section_7_completion" widget="progressbar"/>
                    <field name="section_8_completion" widget="progressbar"/>
                    <field name="section_9_completion" widget="progressbar"/>
                    <field name="section_10_completion" widget="progressbar"/>
                </group>
                
                <group col="2">
                    <field name="overall_completion" widget="progressbar"/>
                    <field name="risk_assessment" readonly="1"/>
                </group>
                
                <!-- 10 Sub-tabs per sezioni -->
                <notebook>
                    <page string="1. Consultazione">
                        <group string="Motivo e Contesto" col="2">
                            <field name="reason_for_consultation" colspan="2"/>
                            <field name="triggering_factors" colspan="2"/>
                            <field name="daily_life_impact" colspan="2"/>
                            <field name="symptoms_duration"/>
                        </group>
                    </page>
                    
                    <page string="2. Anamnesi Psichiatrica">
                        <group string="Diagnosi e Trattamenti Pregressi" col="2">
                            <field name="previous_psychiatric_diagnoses" colspan="2"/>
                            <field name="previous_psychotherapies" colspan="2"/>
                            <field name="previous_medications" colspan="2"/>
                            <field name="psychiatric_hospitalizations" colspan="2"/>
                        </group>
                        
                        <group string="Comportamenti a Rischio" col="2">
                            <field name="previous_suicide_attempts"/>
                            <field name="suicide_attempts_details" 
                                   invisible="not previous_suicide_attempts" colspan="2"/>
                            <field name="self_harm_behaviors"/>
                            <field name="self_harm_details" 
                                   invisible="not self_harm_behaviors" colspan="2"/>
                            <field name="aggressive_behaviors"/>
                            <field name="aggressive_details" 
                                   invisible="not aggressive_behaviors" colspan="2"/>
                        </group>
                        
                        <group string="Storia Familiare" col="2">
                            <field name="family_psychiatric_history"/>
                            <field name="family_history_details" 
                                   invisible="not family_psychiatric_history" colspan="2"/>
                        </group>
                    </page>
                    
                    <page string="3. Anamnesi Medica">
                        <group string="Condizioni Mediche" col="2">
                            <field name="chronic_diseases"/>
                            <field name="chronic_diseases_details" 
                                   invisible="not chronic_diseases" colspan="2"/>
                            <field name="previous_surgeries"/>
                            <field name="surgeries_details" 
                                   invisible="not previous_surgeries" colspan="2"/>
                            <field name="current_medications" colspan="2"/>
                        </group>
                        
                        <group string="Allergie e Condizioni Specifiche" col="2">
                            <field name="allergies"/>
                            <field name="allergies_details" 
                                   invisible="not allergies" colspan="2"/>
                            <field name="pregnancy_breastfeeding"/>
                            <field name="pregnancy_weeks" 
                                   invisible="pregnancy_breastfeeding == 'not_applicable'"/>
                        </group>
                    </page>
                    
                    <page string="4. Sostanze">
                        <group string="Uso di Sostanze" col="2">
                            <field name="smoking"/>
                            <field name="smoking_details" 
                                   invisible="not smoking" colspan="2"/>
                            <field name="alcohol"/>
                            <field name="alcohol_details" 
                                   invisible="not alcohol" colspan="2"/>
                            <field name="illegal_drugs"/>
                            <field name="drugs_details" 
                                   invisible="not illegal_drugs" colspan="2"/>
                        </group>
                    </page>
                    
                    <page string="5. Sociale/Familiare">
                        <group string="Contesto di Vita" col="2">
                            <field name="living_situation"/>
                            <field name="social_support"/>
                            <field name="social_support_description" colspan="2"/>
                            <field name="significant_relationships" colspan="2"/>
                        </group>
                        
                        <group string="Storia e Contesti" col="2">
                            <field name="developmental_history" colspan="2"/>
                            <field name="family_context" colspan="2"/>
                            <field name="social_context" colspan="2"/>
                            <field name="work_context" colspan="2"/>
                            <field name="cultural_aspects" colspan="2"/>
                        </group>
                    </page>
                    
                    <page string="6. Sintomi Attuali">
                        <group string="Descrizione Problema" col="2">
                            <field name="problem_description" colspan="2"/>
                            <field name="symptoms_onset"/>
                            <field name="current_issues" colspan="2"/>
                        </group>
                        
                        <group string="Sintomi dell'Umore" col="2">
                            <field name="sadness_depression" colspan="2"/>
                            <field name="anhedonia" colspan="2"/>
                            <field name="irritability_anger" colspan="2"/>
                            <field name="euphoria_elevated_mood" colspan="2"/>
                            <field name="emotional_lability" colspan="2"/>
                        </group>
                        
                        <group string="Sintomi d'Ansia" col="2">
                            <field name="generalized_anxiety" colspan="2"/>
                            <field name="panic_attacks" colspan="2"/>
                            <field name="phobias" colspan="2"/>
                            <field name="ocd_symptoms" colspan="2"/>
                            <field name="ptsd_symptoms" colspan="2"/>
                        </group>
                        
                        <group string="Sintomi Psicotici" col="2">
                            <field name="hallucinations" colspan="2"/>
                            <field name="delusions" colspan="2"/>
                            <field name="thought_disorganization" colspan="2"/>
                        </group>
                        
                        <group string="Sintomi Cognitivi" col="2">
                            <field name="concentration_difficulties" colspan="2"/>
                            <field name="memory_problems" colspan="2"/>
                            <field name="planning_difficulties" colspan="2"/>
                        </group>
                        
                        <group string="Sintomi Fisici/Somatici" col="2">
                            <field name="sleep_disturbances" colspan="2"/>
                            <field name="appetite_changes" colspan="2"/>
                            <field name="fatigue" colspan="2"/>
                            <field name="somatic_symptoms" colspan="2"/>
                        </group>
                    </page>
                    
                    <page string="7. Esame Psichico">
                        <group string="Aspetto e Comportamento" col="2">
                            <field name="appearance_hygiene" colspan="2"/>
                            <field name="attitude" colspan="2"/>
                            <field name="mimics_gestures" colspan="2"/>
                            <field name="psychomotor_activity" colspan="2"/>
                        </group>
                        
                        <group string="Linguaggio" col="2">
                            <field name="language_quality" colspan="2"/>
                            <field name="language_quantity" colspan="2"/>
                            <field name="language_tone" colspan="2"/>
                        </group>
                        
                        <group string="Umore e Affettività" col="2">
                            <field name="reported_mood" colspan="2"/>
                            <field name="observed_affect" colspan="2"/>
                        </group>
                        
                        <group string="Pensiero" col="2">
                            <field name="thought_form" colspan="2"/>
                            <field name="thought_content" colspan="2"/>
                        </group>
                        
                        <group string="Percezione" col="2">
                            <field name="exam_hallucinations" colspan="2"/>
                            <field name="illusions" colspan="2"/>
                            <field name="derealization" colspan="2"/>
                        </group>
                        
                        <group string="Cognizione" col="2">
                            <field name="orientation" colspan="2"/>
                            <field name="attention_concentration" colspan="2"/>
                            <field name="memory_exam" colspan="2"/>
                            <field name="abstraction_capacity" colspan="2"/>
                            <field name="insight"/>
                            <field name="judgment"/>
                        </group>
                    </page>
                    
                    <page string="8. Valutazione Rischio">
                        <group string="Rischio Generale" col="2">
                            <field name="risk_assessment"/>
                        </group>
                        
                        <group string="Rischio Suicidario" col="2">
                            <field name="suicidal_ideation"/>
                            <field name="suicide_planning" 
                                   invisible="suicidal_ideation == 'absent'"/>
                            <field name="suicide_plan_details" 
                                   invisible="suicide_planning == 'absent'" colspan="2"/>
                            <field name="suicide_intention" 
                                   invisible="suicidal_ideation == 'absent'"/>
                            <field name="suicide_means_available" 
                                   invisible="suicidal_ideation == 'absent'"/>
                            <field name="suicide_means_details" 
                                   invisible="not suicide_means_available" colspan="2"/>
                            <field name="suicide_risk_factors" 
                                   invisible="suicidal_ideation == 'absent'" colspan="2"/>
                        </group>
                        
                        <group string="Rischio Eterolesivo" col="2">
                            <field name="aggressive_ideation"/>
                            <field name="aggression_target" 
                                   invisible="aggressive_ideation == 'absent'" colspan="2"/>
                            <field name="aggression_planning" 
                                   invisible="aggressive_ideation == 'absent'"/>
                            <field name="aggression_plan_details" 
                                   invisible="aggression_planning == 'absent'" colspan="2"/>
                            <field name="aggression_intention" 
                                   invisible="aggressive_ideation == 'absent'"/>
                            <field name="aggression_means_available" 
                                   invisible="aggressive_ideation == 'absent'"/>
                            <field name="aggression_means_details" 
                                   invisible="not aggression_means_available" colspan="2"/>
                            <field name="aggression_risk_factors" 
                                   invisible="aggressive_ideation == 'absent'" colspan="2"/>
                        </group>
                        
                        <group string="Rischio Auto-negligenza" col="4">
                            <field name="hygiene_risk"/>
                            <field name="nutrition_risk"/>
                            <field name="medication_risk"/>
                            <field name="financial_risk"/>
                            <field name="housing_risk"/>
                            <field name="exploitation_vulnerability"/>
                            <field name="self_care_impact" colspan="4"/>
                        </group>
                    </page>
                    
                    <page string="9. Fattori Protettivi">
                        <group string="Risorse del Paziente" col="2">
                            <field name="individual_protective_factors" colspan="2"/>
                            <field name="social_protective_factors" colspan="2"/>
                            <field name="treatment_engagement" colspan="2"/>
                            <field name="stability_factors" colspan="2"/>
                        </group>
                    </page>
                    
                    <page string="10. Conclusioni">
                        <group string="Aspettative e Obiettivi" col="2">
                            <field name="patient_expectations" colspan="2"/>
                            <field name="treatment_goals" colspan="2"/>
                        </group>
                        
                        <group string="Valutazione Clinica" col="2">
                            <field name="clinical_summary" colspan="2"/>
                            <field name="diagnostic_hypotheses" colspan="2"/>
                            <field name="main_problem_areas" colspan="2"/>
                            <field name="relevant_risk_protective_factors" colspan="2"/>
                        </group>
                        
                        <group string="Diagnosi" col="2">
                            <field name="primary_diagnosis"/>
                            <field name="secondary_diagnosis"/>
                            <field name="diagnosis_code" colspan="2"/>
                            <field name="diagnostic_criteria" colspan="2"/>
                            <field name="differential_diagnosis" colspan="2"/>
                            <field name="comorbidity" colspan="2"/>
                        </group>
                        
                        <group string="Piano di Trattamento" col="2">
                            <field name="treatment_plan" colspan="2"/>
                        </group>
                    </page>
                </notebook>
            </sheet>
        </form>
    </field>
</record>
```

#### **Vista Tree per Elenco Cartelle Cliniche**
```xml
<record id="view_clinical_sheet_tree" model="ir.ui.view">
    <field name="name">clinical.sheet.tree</field>
    <field name="model">clinical.sheet</field>
    <field name="arch" type="xml">
        <tree string="Cartelle Cliniche">
            <field name="partner_id"/>
            <field name="partner_id.email"/>
            <field name="overall_completion" widget="progressbar"/>
            <field name="risk_assessment"/>
            <field name="write_date"/>
            <field name="create_date"/>
        </tree>
    </field>
</record>
```

#### **Action per Menu Cartelle Cliniche**
```xml
<record id="action_clinical_sheet_list" model="ir.actions.act_window">
    <field name="name">Cartelle Cliniche</field>
    <field name="res_model">clinical.sheet</field>
    <field name="view_mode">tree,form</field>
    <field name="domain">[('partner_id.is_patient', '=', True)]</field>
    <field name="context">{}</field>
</record>

<menuitem id="menu_clinical_sheets" 
          name="Cartelle Cliniche" 
          parent="contacts.menu_contacts" 
          action="action_clinical_sheet_list"
          sequence="15"/>
```

---

## **5. INTERFACCIA PORTALE MODERNA**

### **5.1 Estensione Controller Portale**
**File**: `controllers/portal.py`

#### **Nuove Route per clinical.sheet**
```python
@http.route(['/my/patient/<int:patient_id>/clinical-sheet'], 
            type='http', auth="user", website=True)
def clinical_sheet_portal(self, patient_id, **kw):
    employee = request.env.user.employee_id
    
    if not employee:
        return request.redirect('/my')
        
    try:
        contact = request.env['res.partner'].sudo().browse(patient_id)
        if not contact.exists() or not contact.is_patient or contact.tutor.id != employee.id:
            raise AccessError(_("You don't have access to this contact."))
    except (AccessError, MissingError):
        return request.redirect('/my/assigned_contacts')

    # Recupera o crea scheda clinica
    clinical_sheet = contact.clinical_sheet_id
    if not clinical_sheet:
        clinical_sheet = request.env['clinical.sheet'].sudo().create({
            'partner_id': contact.id
        })

    values = self._prepare_portal_layout_values()
    values.update({
        'page_name': 'clinical_sheet',
        'contact': contact,
        'clinical_sheet': clinical_sheet,
    })
    
    return request.render("contacts_patient.clinical_sheet_portal", values)

@http.route(['/my/patient/<int:patient_id>/clinical-sheet/save'], 
            type='http', auth="user", methods=['POST'], website=True)
def clinical_sheet_save(self, patient_id, **kw):
    employee = request.env.user.employee_id
    
    if not employee:
        return request.redirect('/my')
        
    try:
        contact = request.env['res.partner'].sudo().browse(patient_id)
        if not contact.exists() or not contact.is_patient or contact.tutor.id != employee.id:
            raise AccessError(_("You don't have access to this contact."))
            
        clinical_sheet = contact.clinical_sheet_id
        if not clinical_sheet:
            clinical_sheet = request.env['clinical.sheet'].sudo().create({
                'partner_id': contact.id
            })
        
        # Aggiorna tutti i campi dal form
        update_vals = {}
        for field_name in clinical_sheet._fields:
            if field_name in kw and field_name not in ['id', 'partner_id', 'name', 'create_date', 'write_date']:
                update_vals[field_name] = kw[field_name]
        
        if update_vals:
            clinical_sheet.sudo().write(update_vals)
        
        return request.redirect(f'/my/patient/{patient_id}/clinical-sheet')
        
    except Exception as e:
        # Log error e redirect con messaggio
        return request.redirect(f'/my/patient/{patient_id}/clinical-sheet?error=save_failed')
```

### **5.2 Template Portale con Card Espandibili**
**File**: `templates/clinical_sheet_portal.xml`

#### **Template Principale**
```xml
<template id="clinical_sheet_portal" name="Clinical Sheet Portal">
    <t t-call="portal.portal_layout">
        <div class="container-fluid clinical-portal">
            
            <!-- Header Paziente -->
            <div class="patient-header">
                <div class="row">
                    <div class="col-md-8">
                        <h2 t-field="contact.name"/>
                        <div class="patient-info">
                            <span t-field="contact.email"/>
                            <span t-if="contact.phone"> - <span t-field="contact.phone"/></span>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="risk-indicators text-end">
                            <div t-if="clinical_sheet.risk_assessment == 'high'" 
                                 class="alert alert-danger mb-2">
                                🔴 Rischio Alto
                            </div>
                            <div t-elif="clinical_sheet.risk_assessment == 'medium'" 
                                 class="alert alert-warning mb-2">
                                🟡 Rischio Medio
                            </div>
                            <div class="completion-info">
                                <strong>Completamento: </strong>
                                <span t-field="clinical_sheet.overall_completion"/>%
                                <div class="progress mt-1">
                                    <div class="progress-bar" 
                                         t-att-style="'width: ' + str(clinical_sheet.overall_completion) + '%'">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Layout a 3 Colonne -->
            <div class="row">
                <!-- Sidebar Navigation -->
                <div class="col-md-3">
                    <div class="clinical-sidebar sticky-top">
                        <nav class="section-nav">
                            <a href="#section-1" class="nav-item" data-section="consultation">
                                <i class="fa fa-clipboard"></i>
                                <span>1. Consultazione</span>
                                <span class="status-indicator" 
                                      t-att-class="'complete' if clinical_sheet.section_1_completion == 100 else 'partial' if clinical_sheet.section_1_completion > 0 else 'empty'"></span>
                            </a>
                            <a href="#section-2" class="nav-item" data-section="psychiatric">
                                <i class="fa fa-brain"></i>
                                <span>2. Anamnesi Psichiatrica</span>
                                <span class="status-indicator" 
                                      t-att-class="'complete' if clinical_sheet.section_2_completion == 100 else 'partial' if clinical_sheet.section_2_completion > 0 else 'empty'"></span>
                            </a>
                            <!-- Continua per tutte le 10 sezioni -->
                            <a href="#section-3" class="nav-item" data-section="medical">
                                <i class="fa fa-heartbeat"></i>
                                <span>3. Anamnesi Medica</span>
                                <span class="status-indicator" 
                                      t-att-class="'complete' if clinical_sheet.section_3_completion == 100 else 'partial' if clinical_sheet.section_3_completion > 0 else 'empty'"></span>
                            </a>
                            <a href="#section-4" class="nav-item" data-section="substances">
                                <i class="fa fa-flask"></i>
                                <span>4. Sostanze</span>
                                <span class="status-indicator" 
                                      t-att-class="'complete' if clinical_sheet.section_4_completion == 100 else 'partial' if clinical_sheet.section_4_completion > 0 else 'empty'"></span>
                            </a>
                            <a href="#section-5" class="nav-item" data-section="social">
                                <i class="fa fa-users"></i>
                                <span>5. Sociale/Familiare</span>
                                <span class="status-indicator" 
                                      t-att-class="'complete' if clinical_sheet.section_5_completion == 100 else 'partial' if clinical_sheet.section_5_completion > 0 else 'empty'"></span>
                            </a>
                            <a href="#section-6" class="nav-item" data-section="symptoms">
                                <i class="fa fa-thermometer-half"></i>
                                <span>6. Sintomi Attuali</span>
                                <span class="status-indicator" 
                                      t-att-class="'complete' if clinical_sheet.section_6_completion == 100 else 'partial' if clinical_sheet.section_6_completion > 0 else 'empty'"></span>
                            </a>
                            <a href="#section-7" class="nav-item" data-section="exam">
                                <i class="fa fa-search"></i>
                                <span>7. Esame Psichico</span>
                                <span class="status-indicator" 
                                      t-att-class="'complete' if clinical_sheet.section_7_completion == 100 else 'partial' if clinical_sheet.section_7_completion > 0 else 'empty'"></span>
                            </a>
                            <a href="#section-8" class="nav-item" data-section="risk">
                                <i class="fa fa-exclamation-triangle"></i>
                                <span>8. Valutazione Rischio</span>
                                <span class="status-indicator" 
                                      t-att-class="'complete' if clinical_sheet.section_8_completion == 100 else 'partial' if clinical_sheet.section_8_completion > 0 else 'empty'"></span>
                            </a>
                            <a href="#section-9" class="nav-item" data-section="protective">
                                <i class="fa fa-shield-alt"></i>
                                <span>9. Fattori Protettivi</span>
                                <span class="status-indicator" 
                                      t-att-class="'complete' if clinical_sheet.section_9_completion == 100 else 'partial' if clinical_sheet.section_9_completion > 0 else 'empty'"></span>
                            </a>
                            <a href="#section-10" class="nav-item" data-section="conclusions">
                                <i class="fa fa-clipboard-check"></i>
                                <span>10. Conclusioni</span>
                                <span class="status-indicator" 
                                      t-att-class="'complete' if clinical_sheet.section_10_completion == 100 else 'partial' if clinical_sheet.section_10_completion > 0 else 'empty'"></span>
                            </a>
                        </nav>
                    </div>
                </div>

                <!-- Content Area -->
                <div class="col-md-6">
                    <form method="post" class="clinical-form" 
                          t-attf-action="/my/patient/#{contact.id}/clinical-sheet/save">
                        <input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>
                        
                        <!-- Card Sezione 1: Consultazione -->
                        <div class="clinical-card collapsed" id="section-1" data-section="consultation">
                            <div class="card">
                                <div class="card-header" onclick="toggleCard(this)">
                                    <h5>
                                        <i class="fa fa-clipboard"></i>
                                        1. Motivo della Consultazione
                                        <i class="fa fa-chevron-down collapse-icon float-end"></i>
                                    </h5>
                                </div>
                                <div class="card-body collapsible-content" style="display: none;">
                                    <div class="form-group mb-3">
                                        <label>Motivo principale riferito dal paziente:</label>
                                        <textarea name="reason_for_consultation" 
                                                  class="form-control" 
                                                  rows="4" 
                                                  t-raw="clinical_sheet.reason_for_consultation"></textarea>
                                    </div>
                                    <div class="form-group mb-3">
                                        <label>Durata sintomatologia attuale:</label>
                                        <input type="text" name="symptoms_duration" 
                                               class="form-control"
                                               t-att-value="clinical_sheet.symptoms_duration"/>
                                    </div>
                                    <div class="form-group mb-3">
                                        <label>Fattori scatenanti percepiti:</label>
                                        <textarea name="triggering_factors" 
                                                  class="form-control" 
                                                  rows="3" 
                                                  t-raw="clinical_sheet.triggering_factors"></textarea>
                                    </div>
                                    <div class="form-group mb-3">
                                        <label>Impatto sulla vita quotidiana:</label>
                                        <textarea name="daily_life_impact" 
                                                  class="form-control" 
                                                  rows="3" 
                                                  t-raw="clinical_sheet.daily_life_impact"></textarea>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Card Sezione 2: Anamnesi Psichiatrica -->
                        <div class="clinical-card collapsed" id="section-2" data-section="psychiatric">
                            <div class="card">
                                <div class="card-header" onclick="toggleCard(this)">
                                    <h5>
                                        <i class="fa fa-brain"></i>
                                        2. Anamnesi Psichiatrica
                                        <i class="fa fa-chevron-down collapse-icon float-end"></i>
                                    </h5>
                                </div>
                                <div class="card-body collapsible-content" style="display: none;">
                                    <!-- Subsection: Diagnosi e Trattamenti -->
                                    <h6 class="text-muted">Diagnosi e Trattamenti Pregressi</h6>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="form-group mb-3">
                                                <label>Diagnosi psichiatriche pregresse:</label>
                                                <textarea name="previous_psychiatric_diagnoses" 
                                                          class="form-control" 
                                                          rows="3" 
                                                          t-raw="clinical_sheet.previous_psychiatric_diagnoses"></textarea>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="form-group mb-3">
                                                <label>Psicoterapie precedenti:</label>
                                                <textarea name="previous_psychotherapies" 
                                                          class="form-control" 
                                                          rows="3" 
                                                          t-raw="clinical_sheet.previous_psychotherapies"></textarea>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <!-- Comportamenti a Rischio -->
                                    <h6 class="text-muted mt-4">Comportamenti a Rischio</h6>
                                    <div class="form-check mb-2">
                                        <input type="checkbox" name="previous_suicide_attempts" 
                                               class="form-check-input" value="1"
                                               t-att-checked="clinical_sheet.previous_suicide_attempts"/>
                                        <label class="form-check-label">Tentativi di suicidio pregressi</label>
                                    </div>
                                    <div class="form-group mb-3 suicide-details" 
                                         t-att-style="'display: none;' if not clinical_sheet.previous_suicide_attempts else ''">
                                        <textarea name="suicide_attempts_details" 
                                                  class="form-control" 
                                                  rows="2" 
                                                  placeholder="Dettagli tentativi suicidio..."
                                                  t-raw="clinical_sheet.suicide_attempts_details"></textarea>
                                    </div>
                                    
                                    <!-- Altri campi simili per autolesioni e aggressività -->
                                </div>
                            </div>
                        </div>

                        <!-- Card Sezioni 3-10 con struttura simile -->
                        <!-- Per brevità mostro solo la struttura base -->
                        
                        <!-- Sezione 3: Anamnesi Medica -->
                        <div class="clinical-card collapsed" id="section-3" data-section="medical">
                            <div class="card">
                                <div class="card-header" onclick="toggleCard(this)">
                                    <h5>
                                        <i class="fa fa-heartbeat"></i>
                                        3. Anamnesi Medica Generale
                                        <i class="fa fa-chevron-down collapse-icon float-end"></i>
                                    </h5>
                                </div>
                                <div class="card-body collapsible-content" style="display: none;">
                                    <!-- Campi anamnesi medica -->
                                </div>
                            </div>
                        </div>

                        <!-- Sezioni 4-10 continuano con la stessa struttura -->
                        
                        <!-- Form Actions -->
                        <div class="form-actions mt-4">
                            <div class="d-flex justify-content-between">
                                <a t-attf-href="/my/assigned_contacts/#{contact.id}" 
                                   class="btn btn-secondary">
                                    <i class="fa fa-arrow-left"></i> Torna al Contatto
                                </a>
                                <button type="submit" class="btn btn-primary btn-lg">
                                    <i class="fa fa-save"></i> Salva Cartella Clinica
                                </button>
                            </div>
                        </div>
                    </form>
                </div>

                <!-- Summary Panel -->
                <div class="col-md-3">
                    <div class="summary-panel sticky-top">
                        <div class="card mb-3">
                            <div class="card-header">
                                <h6 class="mb-0">Indicatori di Rischio</h6>
                            </div>
                            <div class="card-body">
                                <div t-if="clinical_sheet.suicidal_ideation and clinical_sheet.suicidal_ideation != 'absent'" 
                                     t-att-class="'alert alert-danger' if clinical_sheet.suicidal_ideation == 'severe' else 'alert alert-warning'">
                                    <strong>Rischio Suicidario:</strong><br/>
                                    <span t-field="clinical_sheet.suicidal_ideation"/>
                                </div>
                                
                                <div t-if="clinical_sheet.aggressive_ideation and clinical_sheet.aggressive_ideation != 'absent'" 
                                     t-att-class="'alert alert-danger' if clinical_sheet.aggressive_ideation == 'severe' else 'alert alert-warning'">
                                    <strong>Rischio Aggressivo:</strong><br/>
                                    <span t-field="clinical_sheet.aggressive_ideation"/>
                                </div>
                                
                                <div t-if="not clinical_sheet.suicidal_ideation and not clinical_sheet.aggressive_ideation" 
                                     class="text-muted">
                                    Nessun rischio particolare segnalato
                                </div>
                            </div>
                        </div>
                        
                        <div class="card">
                            <div class="card-header">
                                <h6 class="mb-0">Progresso Completamento</h6>
                            </div>
                            <div class="card-body">
                                <div class="progress-item mb-2">
                                    <small>1. Consultazione</small>
                                    <div class="progress">
                                        <div class="progress-bar" 
                                             t-att-style="'width: ' + str(clinical_sheet.section_1_completion or 0) + '%'">
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="progress-item mb-2">
                                    <small>2. Anamnesi Psichiatrica</small>
                                    <div class="progress">
                                        <div class="progress-bar" 
                                             t-att-style="'width: ' + str(clinical_sheet.section_2_completion or 0) + '%'">
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Continua per tutte le sezioni -->
                                
                                <hr/>
                                <div class="text-center">
                                    <strong>Completamento Generale</strong>
                                    <div class="progress mt-2">
                                        <div class="progress-bar progress-bar-success" 
                                             t-att-style="'width: ' + str(clinical_sheet.overall_completion or 0) + '%'">
                                            <span t-field="clinical_sheet.overall_completion"/>%
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </t>
</template>
```

### **5.3 JavaScript per Interattività**
**File**: `static/src/js/clinical_portal.js`

```javascript
$(document).ready(function() {
    
    // Card expand/collapse functionality
    window.toggleCard = function(header) {
        const card = $(header).closest('.clinical-card');
        const content = card.find('.collapsible-content');
        const icon = card.find('.collapse-icon');
        
        if (card.hasClass('collapsed')) {
            content.slideDown(300);
            card.removeClass('collapsed');
            icon.removeClass('fa-chevron-down').addClass('fa-chevron-up');
        } else {
            content.slideUp(300);
            card.addClass('collapsed');
            icon.removeClass('fa-chevron-up').addClass('fa-chevron-down');
        }
    };
    
    // Smooth scrolling navigation
    $('.section-nav a').click(function(e) {
        e.preventDefault();
        const target = $(this).attr('href');
        const targetCard = $(target);
        
        // Espandi la card target se collassata
        if (targetCard.hasClass('collapsed')) {
            toggleCard(targetCard.find('.card-header')[0]);
        }
        
        // Scroll to target
        $('html, body').animate({
            scrollTop: targetCard.offset().top - 100
        }, 500);
        
        // Update active nav item
        $('.section-nav a').removeClass('active');
        $(this).addClass('active');
    });
    
    // Conditional field display
    $('input[name="previous_suicide_attempts"]').change(function() {
        const detailsDiv = $('.suicide-details');
        if ($(this).is(':checked')) {
            detailsDiv.slideDown();
        } else {
            detailsDiv.slideUp();
            detailsDiv.find('textarea').val('');
        }
    });
    
    // Auto-expand first empty section
    function autoExpandFirstEmpty() {
        $('.clinical-card.collapsed').each(function() {
            const isEmpty = $(this).find('input, textarea, select').filter(function() {
                return $(this).val() !== '';
            }).length === 0;
            
            if (isEmpty) {
                toggleCard($(this).find('.card-header')[0]);
                return false; // Stop dopo il primo
            }
        });
    }
    
    // Initialize
    autoExpandFirstEmpty();
    
    // Highlight current section while scrolling
    $(window).scroll(function() {
        const scrollTop = $(window).scrollTop();
        $('.clinical-card').each(function() {
            const cardTop = $(this).offset().top - 150;
            const cardBottom = cardTop + $(this).outerHeight();
            
            if (scrollTop >= cardTop && scrollTop < cardBottom) {
                const sectionId = $(this).attr('id');
                $('.section-nav a').removeClass('active');
                $('.section-nav a[href="#' + sectionId + '"]').addClass('active');
            }
        });
    });
});
```

### **5.4 CSS Styling**
**File**: `static/src/css/clinical_portal.css`

```css
.clinical-portal {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f8f9fa;
}

.patient-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 25px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.patient-info {
    font-size: 0.9em;
    opacity: 0.9;
    margin-top: 5px;
}

.clinical-sidebar {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.section-nav .nav-item {
    display: flex;
    align-items: center;
    padding: 12px 15px;
    color: #495057;
    text-decoration: none;
    border-radius: 8px;
    margin-bottom: 8px;
    transition: all 0.3s ease;
    border: 1px solid transparent;
}

.section-nav .nav-item:hover {
    background: #e3f2fd;
    color: #1976d2;
    border-color: #bbdefb;
}

.section-nav .nav-item.active {
    background: #1976d2;
    color: white;
    box-shadow: 0 2px 8px rgba(25, 118, 210, 0.3);
}

.section-nav .nav-item i {
    margin-right: 10px;
    width: 20px;
    text-align: center;
}

.section-nav .nav-item span {
    flex: 1;
}

.status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-left: 10px;
    border: 2px solid white;
}

.status-indicator.complete { background: #4caf50; }
.status-indicator.partial { background: #ff9800; }
.status-indicator.empty { background: #f44336; }

.clinical-card {
    margin-bottom: 20px;
    transition: all 0.3s ease;
}

.clinical-card .card {
    border: none;
    box-shadow: 0 2px 15px rgba(0,0,0,0.08);
    border-radius: 12px;
    overflow: hidden;
}

.clinical-card.collapsed .card {
    opacity: 0.8;
    transform: scale(0.98);
}

.clinical-card .card-header {
    background: linear-gradient(45deg, #f8f9fa, #e9ecef);
    border-bottom: 1px solid #dee2e6;
    cursor: pointer;
    transition: all 0.3s ease;
    padding: 15px 20px;
}

.clinical-card .card-header:hover {
    background: linear-gradient(45deg, #e9ecef, #dee2e6);
}

.clinical-card .card-header h5 {
    margin: 0;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.clinical-card .card-header i.fa-chevron-down,
.clinical-card .card-header i.fa-chevron-up {
    transition: transform 0.3s ease;
}

.clinical-card .card-body {
    padding: 25px;
}

.summary-panel .card {
    border: none;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    border-radius: 12px;
}

.summary-panel .card-header {
    background: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
    padding: 12px 20px;
}

.progress-item small {
    color: #6c757d;
    font-weight: 500;
}

.progress {
    height: 6px;
    border-radius: 3px;
    background-color: #e9ecef;
}

.progress-bar {
    border-radius: 3px;
    transition: width 0.3s ease;
}

.risk-indicators .alert {
    padding: 8px 12px;
    margin-bottom: 8px;
    border-radius: 6px;
    font-size: 0.85em;
}

.completion-info {
    font-size: 0.9em;
}

.form-actions {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

/* Responsive Design */
@media (max-width: 768px) {
    .clinical-sidebar {
        position: static !important;
        margin-bottom: 20px;
    }
    
    .section-nav {
        display: flex;
        overflow-x: auto;
        padding-bottom: 10px;
    }
    
    .section-nav .nav-item {
        white-space: nowrap;
        min-width: 180px;
        margin-right: 10px;
    }
    
    .summary-panel {
        order: -1;
        margin-bottom: 20px;
    }
    
    .patient-header .row {
        text-align: center;
    }
    
    .patient-header .col-md-4 {
        margin-top: 15px;
    }
}

@media (max-width: 576px) {
    .clinical-portal {
        padding: 0 10px;
    }
    
    .patient-header {
        padding: 20px 15px;
    }
    
    .clinical-card .card-body {
        padding: 20px 15px;
    }
    
    .section-nav .nav-item span {
        font-size: 0.85em;
    }
}
```

---

## **6. IMPLEMENTAZIONE PROGRESS TRACKING**

### **6.1 Computed Fields per Sezioni**
**File**: `models/clinical_sheet.py`

```python
# Computed Fields per ogni sezione
@api.depends('reason_for_consultation', 'symptoms_duration', 'triggering_factors', 'daily_life_impact')
def _compute_section_1_completion(self):
    for record in self:
        fields = [
            record.reason_for_consultation,
            record.symptoms_duration, 
            record.triggering_factors,
            record.daily_life_impact
        ]
        completed = sum(1 for field in fields if field and str(field).strip())
        record.section_1_completion = (completed / len(fields)) * 100 if fields else 0

@api.depends('previous_psychiatric_diagnoses', 'previous_psychotherapies', 'previous_medications', 
             'psychiatric_hospitalizations', 'previous_suicide_attempts', 'suicide_attempts_details',
             'self_harm_behaviors', 'self_harm_details', 'aggressive_behaviors', 'aggressive_details',
             'family_psychiatric_history', 'family_history_details')
def _compute_section_2_completion(self):
    for record in self:
        fields = [
            record.previous_psychiatric_diagnoses,
            record.previous_psychotherapies,
            record.previous_medications,
            record.psychiatric_hospitalizations,
        ]
        # Campi condizionali
        if record.previous_suicide_attempts:
            fields.append(record.suicide_attempts_details)
        if record.self_harm_behaviors:
            fields.append(record.self_harm_details)
        if record.aggressive_behaviors:
            fields.append(record.aggressive_details)
        if record.family_psychiatric_history:
            fields.append(record.family_history_details)
            
        completed = sum(1 for field in fields if field and str(field).strip())
        total_expected = 4 + (
            (1 if record.previous_suicide_attempts else 0) +
            (1 if record.self_harm_behaviors else 0) +
            (1 if record.aggressive_behaviors else 0) +
            (1 if record.family_psychiatric_history else 0)
        )
        record.section_2_completion = (completed / total_expected) * 100 if total_expected > 0 else 0

# Continua per tutte le 10 sezioni...

@api.depends('section_1_completion', 'section_2_completion', 'section_3_completion',
             'section_4_completion', 'section_5_completion', 'section_6_completion',
             'section_7_completion', 'section_8_completion', 'section_9_completion',
             'section_10_completion')
def _compute_overall_completion(self):
    for record in self:
        sections = [
            record.section_1_completion or 0,
            record.section_2_completion or 0,
            record.section_3_completion or 0,
            record.section_4_completion or 0,
            record.section_5_completion or 0,
            record.section_6_completion or 0,
            record.section_7_completion or 0,
            record.section_8_completion or 0,
            record.section_9_completion or 0,
            record.section_10_completion or 0,
        ]
        record.overall_completion = sum(sections) / len(sections) if sections else 0

# Field definitions
section_1_completion = fields.Float("Completamento Consultazione", compute='_compute_section_1_completion', store=True)
section_2_completion = fields.Float("Completamento Anamnesi Psichiatrica", compute='_compute_section_2_completion', store=True)
# ... per tutte le 10 sezioni
overall_completion = fields.Float("Completamento Generale", compute='_compute_overall_completion', store=True)
```

---

## **7. SICUREZZA E ACCESSI**

### **7.1 Estensione Record Rules Esistenti**
**File**: `security/ir.rule.xml`

```xml
<!-- Regola per clinical.sheet - accesso via tutor -->
<record id="rule_clinical_sheet_tutor_access" model="ir.rule">
    <field name="name">Clinical Sheet: portal tutors access</field>
    <field name="model_id" ref="model_clinical_sheet"/>
    <field name="domain_force">[('partner_id.tutor.user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="False"/>
</record>

<!-- Regola per utenti interni - accesso completo -->
<record id="rule_clinical_sheet_internal_access" model="ir.rule">
    <field name="name">Clinical Sheet: internal users full access</field>
    <field name="model_id" ref="model_clinical_sheet"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>
</record>
```

### **7.2 Access Rights per clinical.sheet**
**File**: `security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_clinical_sheet_portal,clinical.sheet portal,model_clinical_sheet,base.group_portal,1,1,1,0
access_clinical_sheet_user,clinical.sheet user,model_clinical_sheet,base.group_user,1,1,1,1
access_clinical_sheet_manager,clinical.sheet manager,model_clinical_sheet,base.group_system,1,1,1,1
```

---

## **8. PIANO DI IMPLEMENTAZIONE**

### **8.1 Fase 1: Modello Dati (Priorità Alta)**
1. **Creare nuovo modello** `clinical.sheet` con 98 campi
2. **Modificare** `res.partner` per relazione One2One
3. **Rimuovere** 25 campi clinici da `res.partner`
4. **Implementare** computed fields per progress tracking
5. **Test** modello in backend con dati di esempio

### **8.2 Fase 2: Backend Odoo (Priorità Alta)**
1. **Modificare** vista partner principale (tab "Dati clinici")
2. **Creare** vista "Cartella Clinica" con 10 sub-tabs
3. **Implementare** action methods per apertura/creazione scheda
4. **Creare** menu e azioni per lista cartelle cliniche
5. **Test** navigazione e funzionalità backend

### **8.3 Fase 3: Sicurezza e Accessi (Priorità Alta)**
1. **Configurare** record rules per `clinical.sheet`
2. **Impostare** access rights per gruppi utenti
3. **Test** accessi portale e backend
4. **Verificare** isolamento dati tra tutor

### **8.4 Fase 4: Portale Base (Priorità Media)**
1. **Estendere** controller esistente con nuove route
2. **Creare** template base con card espandibili
3. **Implementare** form submission e validazione
4. **Test** funzionalità base portale

### **8.5 Fase 5: UX Avanzata (Priorità Bassa)**
1. **Implementare** JavaScript per interattività
2. **Applicare** CSS styling avanzato
3. **Ottimizzare** per dispositivi mobile
4. **Test** user experience completa

---

## **9. CONSIDERAZIONI TECNICHE**

### **9.1 Performance**
- **Relazione One2One**: Efficiente per accessi diretti senza impatto su `res.partner`
- **Computed fields**: Utilizzare `store=True` per campi di completamento
- **Lazy loading**: I campi Text non impattano performance di caricamento
- **Database indexes**: Non necessari per i nuovi campi

### **9.2 Manutenibilità**
- **Separazione logica**: Dati clinici isolati in modello dedicato
- **Naming convention**: Nomi campi descrittivi e consistenti
- **Modularità**: Sezioni organizzate logicamente
- **Estendibilità**: Facile aggiungere nuovi campi o sezioni

### **9.3 Compatibilità**
- **Odoo 18.0**: Piena compatibilità con framework corrente
- **Moduli esistenti**: Nessun conflitto, dati équipe rimangono in `res.partner`
- **Upgrade path**: Struttura compatibile con future versioni
- **Migration strategy**: Script per spostare dati esistenti da `res.partner` a `clinical.sheet`# Documento di Progetto - Estensione Modulo Contacts Patient

## **1. OVERVIEW DEL PROGETTO**

### **1.1 Obiettivo**
Estendere il modulo `contacts_patient` esistente per implementare una scheda clinica completa con 98 campi organizzati in 10 sezioni tematiche, accessibile sia da backend Odoo che da interfaccia portale moderna.

### **1.2 Stato Attuale**
- **Modulo esistente**: `contacts_patient` v18.0.7.0.0
- **Campi presenti**: 25 campi clinici + 6 campi équipe
- **Funzionalità**: Gestione pazienti base con accesso portale

### **1.3 Deliverable**
- **84 nuovi campi** nel modello `res.partner`
- **Vista backend** dedicata "Cartella Clinica" con 10 sub-tabs
- **Interfaccia portale** moderna con card espandibili e auto-save
- **Sistema progress tracking** per completamento sezioni

---

## **2. ARCHITETTURA TECNICA**

### **2.1 Dipendenze**
```python
'depends': ['contacts', 'hr', 'website', 'portal']
```

### **2.2 Struttura Modulo**
```
contacts_patient/
├── models/
│   └── res_partner.py          # Estensione con 84 nuovi campi
├── views/
│   ├── res_partner_views.xml   # Vista backend modificata
│   └── clinical_sheet_view.xml # Nuova vista "Cartella Clinica"
├── controllers/
│   └── portal.py               # Estensione controller esistente
├── templates/
│   ├── clinical_sheet_portal.xml # Nuova interfaccia portale
│   └── (template esistenti)     # Mantenuti invariati
└── static/src/
    ├── js/clinical_portal.js   # JavaScript per interfaccia
    └── css/clinical_portal.css # Styling personalizzato
```

---

# Documento di Progetto - Estensione Modulo Contacts Patient

## **1. OVERVIEW DEL PROGETTO**

### **1.1 Obiettivo**
Estendere il modulo `contacts_patient` esistente per implementare una scheda clinica completa con 98 campi organizzati in 10 sezioni tematiche, tramite un nuovo modello `clinical.sheet` collegato a `res.partner` con relazione One2One, accessibile sia da backend Odoo che da interfaccia portale moderna.

### **1.2 Stato Attuale**
- **Modulo esistente**: `contacts_patient` v18.0.7.0.0
- **Campi presenti**: 25 campi clinici in `res.partner` + 6 campi équipe
- **Funzionalità**: Gestione pazienti base con accesso portale

### **1.3 Deliverable**
- **Nuovo modello** `clinical.sheet` con 98 campi clinici
- **Relazione One2One** tra `clinical.sheet` e `res.partner`
- **Vista backend** dedicata "Cartella Clinica" con 10 sub-tabs
- **Interfaccia portale** moderna con card espandibili
- **Sistema progress tracking** per completamento sezioni

---

## **2. ARCHITETTURA TECNICA**

### **2.1 Dipendenze**
```python
'depends': ['contacts', 'hr', 'website', 'portal']
```

### **2.2 Struttura Modulo**
```
contacts_patient/
├── models/
│   ├── res_partner.py          # Estensione con relazione clinical.sheet
│   └── clinical_sheet.py       # NUOVO: Modello scheda clinica
├── views/
│   ├── res_partner_views.xml   # Vista backend modificata
│   └── clinical_sheet_view.xml # Nuova vista "Cartella Clinica"
├── controllers/
│   └── portal.py               # Estensione controller esistente
├── templates/
│   ├── clinical_sheet_portal.xml # Nuova interfaccia portale
│   └── (template esistenti)     # Mantenuti invariati
└── static/src/
    ├── js/clinical_portal.js   # JavaScript per interfaccia
    └── css/clinical_portal.css # Styling personalizzato
```

---

## **3. MAPPATURA CAMPI ESISTENTI vs NUOVI**

### **3.1 Riepilogo Migrazione Campi**

| **Azione** | **Quantità** | **Descrizione** |
|------------|--------------|-----------------|
| ✅ **MANTIENI in res.partner** | 6 campi | Campi équipe (tutor, professional, date_*) |
| 🔄 **MIGRA a clinical.sheet** | 25 campi | Campi clinici esistenti spostati |
| ➕ **AGGIUNGI a clinical.sheet** | 73 campi | Nuovi campi per completare scheda |
| **📊 TOTALE clinical.sheet** | **98 campi** | Scheda clinica completa |

### **3.2 Campi da Mantenere in res.partner (6 campi équipe)**
```python
# QUESTI RIMANGONO in res.partner
is_patient = fields.Boolean("Paziente")
tutor = fields.Many2one('hr.employee', "Tutor")
date_tutor_assignment = fields.Date("Data assegnazione tutor")
type_professional = fields.Many2one('hr.job', "Tipo professionista")
professional = fields.Many2one('hr.employee', "Professionista")
date_professional_assignment = fields.Date("Data assegnazione professionista")
date_taken_charge = fields.Date("Data presa in carico")
```

### **3.3 Campi da Migrare da res.partner a clinical.sheet (25 campi)**

**Campi diagnosi (6 campi):**
- `primary_diagnosis` → `clinical.sheet.primary_diagnosis`
- `secondary_diagnosis` → `clinical.sheet.secondary_diagnosis`
- `diagnosis_code` → `clinical.sheet.diagnosis_code`
- `diagnostic_criteria` → `clinical.sheet.diagnostic_criteria`
- `differential_diagnosis` → `clinical.sheet.differential_diagnosis`
- `comorbidity` → `clinical.sheet.comorbidity`

**Campi clinici base (12 campi):**
- `reason_for_consultation` → `clinical.sheet.reason_for_consultation`
- `problem_description` → `clinical.sheet.problem_description`
- `symptoms_onset` → `clinical.sheet.symptoms_onset`
- `symptoms_duration` → `clinical.sheet.symptoms_duration`
- `previous_treatments` → `clinical.sheet.previous_psychotherapies`
- `current_issues` → `clinical.sheet.current_issues`
- `family_context` → `clinical.sheet.family_context`
- `social_context` → `clinical.sheet.social_context`
- `work_context` → `clinical.sheet.work_context`
- `risk_assessment` → `clinical.sheet.risk_assessment`
- `treatment_goals` → `clinical.sheet.treatment_goals`
- `referrals` → `clinical.sheet.treatment_plan`

### **3.4 Nuovi Campi da Aggiungere (73 campi)**

**Per sezione:**
- **Sezione 1 (Consultazione)**: +2 campi (4 totali)
- **Sezione 2.1 (Anamnesi Psichiatrica)**: +11 campi (12 totali)
- **Sezione 2.2 (Anamnesi Medica)**: +9 campi (9 totali)  
- **Sezione 2.3 (Sostanze)**: +6 campi (6 totali)
- **Sezione 3 (Sociale/Familiare)**: +6 campi (9 totali)
- **Sezione 4 (Sintomi Attuali)**: +18 campi (21 totali)
- **Sezione 5 (Esame Psichico)**: +20 campi (20 totali)
- **Sezione 6 (Valutazione Rischio)**: +21 campi (22 totali)
- **Sezione 7 (Fattori Protettivi)**: +4 campi (4 totali)
- **Sezione 8-10 (Conclusioni)**: +6 campi (11 totali)

---

## **3. MODIFICA MODELLO DATI**

### **3.1 Nuovo Modello clinical_sheet.py**

#### **3.1.1 Definizione Modello Base**
```python
class ClinicalSheet(models.Model):
    _name = 'clinical.sheet'
    _description = 'Scheda Clinica Paziente'
    _order = 'create_date desc'
    
    # Relazione con partner
    partner_id = fields.Many2one('res.partner', string="Paziente", 
                                required=True, ondelete='cascade',
                                domain=[('is_patient', '=', True)])
    
    # Campi base
    name = fields.Char(related='partner_id.name', readonly=True, store=True)
    active = fields.Boolean(default=True)
    
    # 98 Campi clinici organizzati per sezione
```

#### **3.1.2 Campi Migrati da res_partner (25 esistenti)**
```python
# SEZIONE 1: Consultazione (4 campi)
reason_for_consultation = fields.Text("Motivo della consulenza/presa in carico")
symptoms_duration = fields.Char("Durata dei sintomi")
triggering_factors = fields.Text("Fattori scatenanti percepiti")  # NUOVO
daily_life_impact = fields.Text("Impatto sulla vita quotidiana")  # NUOVO

# SEZIONE 4: Sintomi Attuali (3 campi esistenti)
problem_description = fields.Text("Descrizione del problema presentato")
symptoms_onset = fields.Date("Data di inizio dei sintomi")
current_issues = fields.Text("Problematiche attuali riferite dal paziente")

# SEZIONE 3: Sociale/Familiare (3 campi esistenti)
family_context = fields.Text("Contesto familiare rilevante")
social_context = fields.Text("Contesto sociale e relazionale")
work_context = fields.Text("Contesto lavorativo o scolastico")

# SEZIONE 2.1: Anamnesi Psichiatrica (1 campo esistente)
previous_psychotherapies = fields.Text("Trattamenti precedentemente ricevuti")

# SEZIONE 6: Valutazione Rischio (1 campo esistente)
risk_assessment = fields.Selection([
    ('low', 'Basso'),
    ('medium', 'Medio'),
    ('high', 'Alto')
], string="Valutazione del rischio")

# SEZIONE 8: Aspettative (1 campo esistente)
treatment_goals = fields.Text("Obiettivi del trattamento")

# SEZIONE 10: Raccomandazioni (1 campo esistente)
treatment_plan = fields.Text("Piano di trattamento proposto")

# Campi diagnosi esistenti (10 campi)
primary_diagnosis = fields.Char("Diagnosi primaria")
secondary_diagnosis = fields.Char("Diagnosi secondaria")
diagnosis_code = fields.Char("Codice diagnosi (es. da DSM-5 o ICD-10)")
diagnostic_criteria = fields.Text("Criteri diagnostici utilizzati")
differential_diagnosis = fields.Text("Diagnosi differenziale considerata")
comorbidity = fields.Text("Comorbilità e sintomi secondari")
```

#### **3.1.3 Nuovi Campi da Aggiungere (73 campi)**

**SEZIONE 2.1: Anamnesi Psichiatrica (11 nuovi)**
```python
previous_psychiatric_diagnoses = fields.Text("Diagnosi psichiatriche pregresse")
previous_medications = fields.Text("Farmaci precedenti")
psychiatric_hospitalizations = fields.Text("Ricoveri psichiatrici")
previous_suicide_attempts = fields.Boolean("Tentativi suicidio pregressi")
suicide_attempts_details = fields.Text("Dettagli tentativi suicidio")
self_harm_behaviors = fields.Boolean("Comportamenti autolesivi")
self_harm_details = fields.Text("Dettagli autolesioni")
aggressive_behaviors = fields.Boolean("Comportamenti aggressivi pregressi")
aggressive_details = fields.Text("Dettagli comportamenti aggressivi")
family_psychiatric_history = fields.Boolean("Storia familiare psichiatrica")
family_history_details = fields.Text("Dettagli storia familiare")
```

**SEZIONE 2.2: Anamnesi Medica (9 nuovi)**
```python
chronic_diseases = fields.Boolean("Malattie croniche attuali")
chronic_diseases_details = fields.Text("Dettagli malattie croniche")
previous_surgeries = fields.Boolean("Interventi chirurgici pregressi")
surgeries_details = fields.Text("Dettagli interventi")
current_medications = fields.Text("Farmaci attuali")
allergies = fields.Boolean("Allergie")
allergies_details = fields.Text("Dettagli allergie")
pregnancy_breastfeeding = fields.Selection([
    ('not_applicable', 'Non applicabile'),
    ('pregnant', 'Gravidanza'),
    ('breastfeeding', 'Allattamento')
], "Gravidanza/Allattamento")
pregnancy_weeks = fields.Char("Settimane/Mesi")
```

**SEZIONE 2.3: Sostanze (6 nuovi)**
```python
smoking = fields.Boolean("Fumo")
smoking_details = fields.Text("Dettagli fumo")
alcohol = fields.Boolean("Consumo alcol")
alcohol_details = fields.Text("Dettagli alcol")
illegal_drugs = fields.Boolean("Uso sostanze")
drugs_details = fields.Text("Dettagli sostanze")
```

**SEZIONE 3: Sociale/Familiare (3 nuovi)**
```python
living_situation = fields.Selection([
    ('alone', 'Vive da solo/a'),
    ('family', 'Con famiglia d\'origine'),
    ('partner', 'Con partner'),
    ('children', 'Con figli'),
    ('facility', 'Struttura protetta'),
    ('other', 'Altro')
], "Situazione abitativa")
social_support = fields.Selection([
    ('adequate', 'Adeguato'),
    ('poor', 'Scarso'),
    ('absent', 'Assente')
], "Supporto sociale")
social_support_description = fields.Text("Descrizione supporto")
significant_relationships = fields.Text("Relazioni significative")
developmental_history = fields.Text("Storia evolutiva")
cultural_aspects = fields.Text("Aspetti culturali/spirituali")
```

**SEZIONE 4: Sintomi Attuali (18 nuovi)**
```python
# Sintomi dell'umore
sadness_depression = fields.Text("Tristezza/Depressione")
anhedonia = fields.Text("Perdita interesse/piacere")
irritability_anger = fields.Text("Irritabilità/rabbia")
euphoria_elevated_mood = fields.Text("Euforia/umore elevato")
emotional_lability = fields.Text("Labilità emotiva")

# Sintomi d'ansia
generalized_anxiety = fields.Text("Ansia generalizzata")
panic_attacks = fields.Text("Attacchi di panico")
phobias = fields.Text("Fobie")
ocd_symptoms = fields.Text("Sintomi ossessivo-compulsivi")
ptsd_symptoms = fields.Text("Sintomi post-traumatici")

# Sintomi psicotici
hallucinations = fields.Text("Allucinazioni")
delusions = fields.Text("Deliri")
thought_disorganization = fields.Text("Disorganizzazione pensiero")

# Sintomi cognitivi
concentration_difficulties = fields.Text("Difficoltà concentrazione")
memory_problems = fields.Text("Problemi memoria")
planning_difficulties = fields.Text("Difficoltà pianificazione")

# Sintomi fisici
sleep_disturbances = fields.Text("Disturbi del sonno")
appetite_changes = fields.Text("Alterazioni appetito")
fatigue = fields.Text("Fatica/mancanza energia")
somatic_symptoms = fields.Text("Sintomi somatici")
```

**SEZIONE 5: Esame Obiettivo Psichico (20 nuovi)**
```python
# Aspetto e comportamento
appearance_hygiene = fields.Text("Abbigliamento e igiene")
attitude = fields.Text("Atteggiamento")
mimics_gestures = fields.Text("Mimica e gestualità")
psychomotor_activity = fields.Text("Attività psicomotoria")

# Linguaggio
language_quality = fields.Text("Qualità linguaggio")
language_quantity = fields.Text("Quantità linguaggio")
language_tone = fields.Text("Tono/volume")

# Umore e affettività
reported_mood = fields.Text("Umore riferito")
observed_affect = fields.Text("Affettività osservata")

# Pensiero
thought_form = fields.Text("Forma del pensiero")
thought_content = fields.Text("Contenuto del pensiero")

# Percezione
exam_hallucinations = fields.Text("Allucinazioni (esame)")
illusions = fields.Text("Illusioni")
derealization = fields.Text("Derealizzazione/Depersonalizzazione")

# Cognizione
orientation = fields.Text("Orientamento")
attention_concentration = fields.Text("Attenzione e concentrazione")
memory_exam = fields.Text("Memoria")
abstraction_capacity = fields.Text("Capacità di astrazione")
insight = fields.Selection([
    ('good', 'Buono'),
    ('partial', 'Parziale'),
    ('absent', 'Assente')
], "Insight")
judgment = fields.Selection([
    ('good', 'Buono'),
    ('partial', 'Parziale'),
    ('compromised', 'Compromesso')
], "Giudizio")
```

**SEZIONE 6: Valutazione Rischio (21 nuovi)**
```python
# Rischio suicidario
suicidal_ideation = fields.Selection([
    ('absent', 'Assente'),
    ('mild', 'Lieve'),
    ('moderate', 'Moderata'),
    ('severe', 'Grave')
], "Ideazione suicidaria")
suicide_planning = fields.Selection([
    ('absent', 'Assente'),
    ('undefined', 'Indefinita'),
    ('defined', 'Definita')
], "Pianificazione suicidaria")
suicide_plan_details = fields.Text("Dettagli pianificazione")
suicide_intention = fields.Selection([
    ('absent', 'Assente'),
    ('low', 'Bassa'),
    ('moderate', 'Moderata'),
    ('high', 'Alta')
], "Intenzione suicidaria")
suicide_means_available = fields.Boolean("Mezzi disponibili")
suicide_means_details = fields.Text("Dettagli mezzi")
suicide_risk_factors = fields.Text("Fattori rischio aggiuntivi")

# Rischio eterolesivo
aggressive_ideation = fields.Selection([
    ('absent', 'Assente'),
    ('mild', 'Lieve'),
    ('moderate', 'Moderata'),
    ('severe', 'Grave')
], "Ideazione aggressiva")
aggression_target = fields.Text("Verso chi")
aggression_planning = fields.Selection([
    ('absent', 'Assente'),
    ('undefined', 'Indefinita'),
    ('defined', 'Definita')
], "Pianificazione aggressiva")
aggression_plan_details = fields.Text("Dettagli pianificazione")
aggression_intention = fields.Selection([
    ('absent', 'Assente'),
    ('low', 'Bassa'),
    ('moderate', 'Moderata'),
    ('high', 'Alta')
], "Intenzione aggressiva")
aggression_means_available = fields.Boolean("Mezzi aggressione disponibili")
aggression_means_details = fields.Text("Dettagli mezzi aggressione")
aggression_risk_factors = fields.Text("Fattori rischio aggressivo")

# Auto-negligenza
hygiene_risk = fields.Boolean("Rischio igiene")
nutrition_risk = fields.Boolean("Rischio alimentazione")
medication_risk = fields.Boolean("Rischio farmaci")
financial_risk = fields.Boolean("Rischio finanze")
housing_risk = fields.Boolean("Rischio abitazione")
exploitation_vulnerability = fields.Boolean("Vulnerabilità sfruttamento")
self_care_impact = fields.Text("Impatto capacità auto-cura")
```

**SEZIONE 7: Fattori Protettivi (4 nuovi)**
```python
individual_protective_factors = fields.Text("Fattori individuali")
social_protective_factors = fields.Text("Supporto sociale")
treatment_engagement = fields.Text("Coinvolgimento trattamento")
stability_factors = fields.Text("Stabilità generale")
```

**SEZIONE 8: Aspettative (1 nuovo)**
```python
patient_expectations = fields.Text("Aspettative paziente")
```

**SEZIONE 9: Impressione Clinica (4 nuovi)**
```python
clinical_summary = fields.Text("Sintesi dati principali")
diagnostic_hypotheses = fields.Text("Ipotesi diagnostiche")
main_problem_areas = fields.Text("Aree problematiche principali")
relevant_risk_protective_factors = fields.Text("Fattori rilevanti")
```

#### **3.1.4 Computed Fields per Progress Tracking**
```python
@api.depends('reason_for_consultation', 'symptoms_duration', 'triggering_factors', 'daily_life_impact')
def _compute_section_1_completion(self):
    for record in self:
        fields = [record.reason_for_consultation, record.symptoms_duration, 
                 record.triggering_factors, record.daily_life_impact]
        completed = sum(1 for field in fields if field)
        record.section_1_completion = (completed / len(fields)) * 100

# Metodi simili per le altre 9 sezioni

@api.depends('section_1_completion', 'section_2_completion', ..., 'section_10_completion')
def _compute_overall_completion(self):
    for record in self:
        sections = [record.section_1_completion, record.section_2_completion, ...]
        record.overall_completion = sum(sections) / len(sections) if sections else 0

section_1_completion = fields.Float("Completamento Consultazione", compute='_compute_section_1_completion')
section_2_completion = fields.Float("Completamento Anamnesi Psichiatrica", compute='_compute_section_2_completion')
# ... per tutte le 10 sezioni
overall_completion = fields.Float("Completamento Generale", compute='_compute_overall_completion')
```

### **3.2 Modifica res_partner.py**

#### **3.2.1 Relazione One2One con clinical.sheet**
```python
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # Relazione One2One con scheda clinica
    clinical_sheet_id = fields.One2many('clinical.sheet', 'partner_id', 
                                       string="Scheda Clinica",
                                       help="Scheda clinica del paziente")
    
    # Computed field per verificare esistenza scheda
    has_clinical_sheet = fields.Boolean("Ha Scheda Clinica", 
                                       compute='_compute_has_clinical_sheet')
    
    @api.depends('clinical_sheet_id')
    def _compute_has_clinical_sheet(self):
        for partner in self:
            partner.has_clinical_sheet = bool(partner.clinical_sheet_id)
    
    def action_create_clinical_sheet(self):
        """Crea una nuova scheda clinica per il paziente"""
        if not self.clinical_sheet_id:
            clinical_sheet = self.env['clinical.sheet'].create({
                'partner_id': self.id,
            })
            return self.action_open_clinical_sheet()
        else:
            return self.action_open_clinical_sheet()
    
    def action_open_clinical_sheet(self):
        """Apre la scheda clinica esistente"""
        if not self.clinical_sheet_id:
            return self.action_create_clinical_sheet()
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Cartella Clinica - {self.name}',
            'res_model': 'clinical.sheet',
            'res_id': self.clinical_sheet_id[0].id,
            'view_mode': 'form',
            'view_id': self.env.ref('contacts_patient.view_clinical_sheet_form').id,
            'target': 'current',
            'context': self.env.context,
        }
```

#### **3.2.2 Rimozione Campi Migrati**
I 25 campi clinici esistenti in `res.partner` verranno rimossi e migrati nel nuovo modello `clinical.sheet`. I campi équipe rimangono in `res.partner`:

```python
# MANTENERE in res.partner (6 campi équipe)
tutor = fields.Many2one('hr.employee', string="Tutor")
date_tutor_assignment = fields.Date("Data di assegnazione del tutor")
type_professional = fields.Many2one('hr.job', string="Tipo di professionista")
professional = fields.Many2one('hr.employee', string="Professionista")
date_professional_assignment = fields.Date("Data di assegnazione del professionista")
date_taken_charge = fields.Date("Data di presa in carico")

# RIMUOVERE da res.partner (25 campi clinici)
# Questi campi verranno spostati in clinical.sheet
``` Impressione Clinica (4 nuovi)**
```python
clinical_summary = fields.Text("Sintesi dati principali")
diagnostic_hypotheses = fields.Text("Ipotesi diagnostiche")
main_problem_areas = fields.Text("Aree problematiche principali")
relevant_risk_protective_factors = fields.Text("Fattori rilevanti")
```

#### **3.1.4 Computed Fields per Progress Tracking**
```python
@api.depends('campo1', 'campo2', ...)
def _compute_section_completion(self):
    # Calcolo percentuale completamento per sezione
    
section_1_completion = fields.Float("Completamento Consultazione", compute='_compute_section_completion')
section_2_completion = fields.Float("Completamento Anamnesi Psichiatrica", compute='_compute_section_completion')
# ... per tutte le 10 sezioni
overall_completion = fields.Float("Completamento Generale", compute='_compute_section_completion')
```

---

## **4. MODIFICHE VISTE BACKEND**

### **4.1 Vista Partner Principale**
**File**: `views/res_partner_views.xml`

#### **Modifica al Tab "Cartella clinica"**
```xml
<page string="Dati clinici" invisible="not is_patient">
    <div class="oe_button_box">
        <button name="action_open_clinical_sheet" 
                type="object" 
                class="oe_stat_button" 
                icon="fa-folder-medical">
            <div class="o_field_widget">
                <span class="o_stat_text">Apri</span>
                <span class="o_stat_text">Cartella Clinica</span>
            </div>
        </button>
    </div>
    
    <group string="Équipe" col="2">
        <field name="tutor"/>
        <field name="date_tutor_assignment"/>
        <field name="type_professional"/>
        <field name="professional"/>
        <field name="date_professional_assignment"/>
        <field name="date_taken_charge"/>
    </group>
    
    <group string="Completamento Scheda" col="2">
        <field name="overall_completion" widget="progressbar"/>
        <!-- Indicatori per sezione -->
    </group>
</page>
```

### **4.2 Nuova Vista "Cartella Clinica"**
**File**: `views/clinical_sheet_view.xml`

#### **Window Action**
```xml
<record id="action_clinical_sheet" model="ir.actions.act_window">
    <field name="name">Cartella Clinica</field>
    <field name="res_model">res.partner</field>
    <field name="view_mode">form</field>
    <field name="view_id" ref="view_clinical_sheet_form"/>
    <field name="target">new</field>
    <field name="context">{'default_is_patient': True}</field>
</record>
```

#### **Vista Form Specializzata**
```xml
<record id="view_clinical_sheet_form" model="ir.ui.view">
    <field name="name">Cartella Clinica</field>
    <field name="model">res.partner</field>
    <field name="arch" type="xml">
        <form string="Cartella Clinica">
            <!-- Header con dati paziente -->
            <header>
                <h1>
                    <field name="name" readonly="1" class="oe_inline"/>
                </h1>
                <group col="4" class="patient_header">
                    <field name="email" readonly="1"/>
                    <field name="phone" readonly="1"/>
                    <field name="date_taken_charge" readonly="1"/>
                    <field name="risk_assessment" readonly="1"/>
                </group>
            </header>
            
            <!-- Progress indicators -->
            <div class="progress_section">
                <group col="5">
                    <field name="section_1_completion" widget="progressbar"/>
                    <field name="section_2_completion" widget="progressbar"/>
                    <!-- ... altre sezioni -->
                </group>
            </div>
            
            <!-- 10 Sub-tabs per sezioni -->
            <notebook>
                <page string="1. Consultazione">
                    <group col="2">
                        <field name="reason_for_consultation"/>
                        <field name="symptoms_duration"/>
                        <field name="triggering_factors"/>
                        <field name="daily_life_impact"/>
                    </group>
                </page>
                
                <page string="2. Anamnesi Psichiatrica">
                    <group string="Diagnosi e Trattamenti">
                        <field name="previous_psychiatric_diagnoses"/>
                        <field name="previous_psychotherapies"/>
                        <field name="previous_medications"/>
                        <field name="psychiatric_hospitalizations"/>
                    </group>
                    <group string="Comportamenti a Rischio">
                        <field name="previous_suicide_attempts"/>
                        <field name="suicide_attempts_details" invisible="not previous_suicide_attempts"/>
                        <field name="self_harm_behaviors"/>
                        <field name="self_harm_details" invisible="not self_harm_behaviors"/>
                        <field name="aggressive_behaviors"/>
                        <field name="aggressive_details" invisible="not aggressive_behaviors"/>
                    </group>
                    <group string="Storia Familiare">
                        <field name="family_psychiatric_history"/>
                        <field name="family_history_details" invisible="not family_psychiatric_history"/>
                    </group>
                </page>
                
                <!-- ... altre 8 sezioni con struttura simile -->
                
            </notebook>
        </form>
    </field>
</record>
```

#### **Metodo nel Modello**
```python
def action_open_clinical_sheet(self):
    return {
        'type': 'ir.actions.act_window',
        'name': f'Cartella Clinica - {self.name}',
        'res_model': 'res.partner',
        'res_id': self.id,
        'view_mode': 'form',
        'view_id': self.env.ref('contacts_patient.view_clinical_sheet_form').id,
        'target': 'new',
        'context': self.env.context,
    }
```

---

## **5. INTERFACCIA PORTALE MODERNA**

### **5.1 Nuovo Controller Route**
**File**: `controllers/portal.py`

```python
@http.route(['/my/patient/<int:patient_id>/clinical-sheet'], 
            type='http', auth="user", website=True)
def clinical_sheet_portal(self, patient_id, **kw):
    # Controlli sicurezza esistenti
    # Logica per recuperare dati e sezioni
    # Render template con card espandibili
```

### **5.2 Template Portale con Card**
**File**: `templates/clinical_sheet_portal.xml`

#### **Struttura Layout**
```xml
<template id="clinical_sheet_portal">
    <t t-call="portal.portal_layout">
        <div class="container-fluid clinical-portal">
            
            <!-- Header Paziente -->
            <div class="patient-header">
                <div class="row">
                    <div class="col-md-8">
                        <h2 t-field="contact.name"/>
                        <div class="patient-info">
                            <span t-field="contact.email"/>
                            <span t-field="contact.phone"/>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="risk-indicators">
                            <span t-if="contact.risk_assessment == 'high'" 
                                  class="badge badge-danger">🔴 Rischio Alto</span>
                            <div class="completion-bar">
                                <span>Completamento: </span>
                                <span t-field="contact.overall_completion"/>%
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Layout a 3 Colonne -->
            <div class="row">
                <!-- Sidebar Navigation -->
                <div class="col-md-3">
                    <div class="clinical-sidebar sticky-top">
                        <nav class="section-nav">
                            <a href="#section-1" class="nav-item" data-section="consultation">
                                <i class="fa fa-clipboard"></i>
                                <span>1. Consultazione</span>
                                <span class="status-indicator" 
                                      t-att-class="'complete' if contact.section_1_completion == 100 else 'partial' if contact.section_1_completion > 0 else 'empty'"></span>
                            </a>
                            <!-- Altri 9 menu items -->
                        </nav>
                    </div>
                </div>

                <!-- Content Area -->
                <div class="col-md-6">
                    <form method="post" class="clinical-form">
                        
                        <!-- Card Sezione 1 -->
                        <div class="clinical-card collapsed" id="section-1" data-section="consultation">
                            <div class="card">
                                <div class="card-header" onclick="toggleCard(this)">
                                    <h5>
                                        <i class="fa fa-clipboard"></i>
                                        1. Motivo della Consultazione
                                        <i class="fa fa-chevron-down collapse-icon float-right"></i>
                                    </h5>
                                </div>
                                <div class="card-body collapsible-content" style="display: none;">
                                    <div class="form-group">
                                        <label>Motivo principale riferito dal paziente:</label>
                                        <textarea name="reason_for_consultation" 
                                                  class="form-control auto-save" 
                                                  data-field="reason_for_consultation"
                                                  rows="4" 
                                                  t-raw="contact.reason_for_consultation"></textarea>
                                    </div>
                                    <!-- Altri 3 campi -->
                                </div>
                            </div>
                        </div>

                        <!-- Card Sezione 2-10 con struttura simile -->
                        
                        <div class="form-actions">
                            <button type="submit" class="btn btn-primary">
                                <i class="fa fa-save"></i> Salva Modifiche
                            </button>
                        </div>
                    </form>
                </div>

                <!-- Summary Panel -->
                <div class="col-md-3">
                    <div class="summary-panel sticky-top">
                        <div class="card">
                            <div class="card-header">
                                <h6>Rischi Attuali</h6>
                            </div>
                            <div class="card-body">
                                <div t-if="contact.suicidal_ideation" 
                                     t-att-class="'alert alert-danger' if contact.suicidal_ideation == 'severe' else 'alert alert-warning'">
                                    🔴 Rischio Suicidario: <span t-field="contact.suicidal_ideation"/>
                                </div>
                                <!-- Altri indicatori -->
                            </div>
                        </div>
                        
                        <div class="card mt-3">
                            <div class="card-header">
                                <h6>Progresso Completamento</h6>
                            </div>
                            <div class="card-body">
                                <!-- Progress bars per sezione -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </t>
</template>
```

### **5.3 JavaScript Interattività**
**File**: `static/src/js/clinical_portal.js`

#### **Funzionalità Principali**
```javascript
// Card expand/collapse
function toggleCard(header) {
    const card = $(header).closest('.clinical-card');
    const content = card.find('.collapsible-content');
    
    if (card.hasClass('collapsed')) {
        content.slideDown();
        card.removeClass('collapsed');
    } else {
        content.slideUp();
        card.addClass('collapsed');
    }
}

// Auto-save (opzionale per future implementazioni)
$('.auto-save').on('input', debounce(function() {
    // Implementazione futura
}, 1000));

// Smooth scrolling navigation
$('.section-nav a').click(function(e) {
    e.preventDefault();
    const target = $(this).attr('href');
    
    // Espandi la card target se collassata
    const targetCard = $(target);
    if (targetCard.hasClass('collapsed')) {
        toggleCard(targetCard.find('.card-header')[0]);
    }
    
    $('html, body').animate({
        scrollTop: targetCard.offset().top - 100
    }, 500);
});

// Update progress indicators
function updateSectionProgress() {
    // Calcola completamento in base ai campi compilati
    // Aggiorna indicatori nella sidebar
}
```

### **5.4 CSS Styling**
**File**: `static/src/css/clinical_portal.css`

#### **Stili Principali**
```css
.clinical-portal {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.patient-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}

.clinical-sidebar {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 20px;
}

.clinical-card {
    margin-bottom: 20px;
    transition: all 0.3s ease;
}

.clinical-card .card {
    border: none;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    border-radius: 10px;
}

.clinical-card.collapsed .card {
    opacity: 0.7;
}

.clinical-card .card-header {
    background: #fff;
    border-bottom: 1px solid #e9ecef;
    cursor: pointer;
    transition: all 0.3s ease;
}

.clinical-card .card-header:hover {
    background: #f8f9fa;
}

.status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
    margin-left: 10px;
}

.status-indicator.complete { background: #28a745; }
.status-indicator.partial { background: #ffc107; }
.status-indicator.empty { background: #dc3545; }

/* Responsive */
@media (max-width: 768px) {
    .clinical-sidebar {
        position: static !important;
        margin-bottom: 20px;
    }
    
    .section-nav {
        display: flex;
        overflow-x: auto;
    }
}
```

---

## **6. IMPLEMENTAZIONE PROGRESS TRACKING**

### **6.1 Computed Fields**
```python
@api.depends('reason_for_consultation', 'symptoms_duration', 'triggering_factors', 'daily_life_impact')
def _compute_section_1_completion(self):
    for record in self:
        fields = [record.reason_for_consultation, record.symptoms_duration, 
                 record.triggering_factors, record.daily_life_impact]
        completed = sum(1 for field in fields if field)
        record.section_1_completion = (completed / len(fields)) * 100

# Metodi simili per le altre 9 sezioni

@api.depends('section_1_completion', 'section_2_completion', ..., 'section_10_completion')
def _compute_overall_completion(self):
    for record in self:
        sections = [record.section_1_completion, record.section_2_completion, ...]
        record.overall_completion = sum(sections) / len(sections)
```

### **6.2 Indicatori Visivi**
- **Sidebar**: Icone colorate per stato sezione
- **Progress bars**: Widget progressbar in backend
- **Summary panel**: Indicatori di completamento nel portale

---

## **7. SICUREZZA E ACCESSI**

### **7.1 Mantenimento Sistema Esistente**
- **Record rules**: Già implementate correttamente
- **Access rights**: Funzionanti per portale
- **Controlli tutor**: Da mantenere invariati

### **7.2 Nessuna Modifica Necessaria**
Il sistema di sicurezza esistente è adeguato per i nuovi campi.

---

## **8. PIANO DI IMPLEMENTAZIONE**

### **8.1 Fase 1: Modello Dati (Priorità Alta)**
1. Estendere `res_partner.py` con 84 nuovi campi
2. Implementare computed fields per progress tracking
3. Rinominare 2 campi esistenti
4. Test modello in backend

### **8.2 Fase 2: Backend Odoo (Priorità Alta)**
1. Modificare vista partner principale
2. Creare nuova vista "Cartella Clinica" con 10 sub-tabs
3. Implementare action method
4. Test navigazione backend

### **8.3 Fase 3: Portale Base (Priorità Media)**
1. Estendere controller esistente
2. Creare template base con card espandibili
3. Implementare layout responsive
4. Test funzionalità base portale

### **8.4 Fase 4: UX Avanzata (Priorità Bassa)**
1. Implementare JavaScript interattività
2. Styling CSS avanzato
3. Ottimizzazioni mobile
4. Test completo user experience

### **8.5 Fase 5: Testing e Deploy**
1. Test integrazione completa backend/portale
2. Verifica performance con dataset di test
3. Controllo responsive su diversi dispositivi
4. Validazione sicurezza e accessi
5. Deploy su ambiente di staging
6. User acceptance testing
7. Deploy su produzione

---

## **9. CONSIDERAZIONI TECNICHE**

### **9.1 Performance**
- **Computed fields**: Utilizzare `@api.depends` appropriati per evitare ricalcoli inutili
- **Lazy loading**: I campi Text non impattano significativamente le performance
- **Database indexes**: Non necessari per i nuovi campi (tutti Text/Boolean/Selection)
- **Memory usage**: 84 campi aggiuntivi hanno impatto minimo

### **9.2 Manutenibilità**
- **Naming convention**: Nomi campi descrittivi e consistenti
- **Documentazione**: Ogni campo ha string descrittiva in italiano
- **Modularità**: Sezioni logicamente separate nei template
- **Estendibilità**: Struttura facilmente estendibile per futuri campi

### **9.3 Compatibilità**
- **Odoo 18.0**: Piena compatibilità con framework corrente
- **Moduli esistenti**: Nessun conflitto con moduli standard
- **Upgrade path**: Struttura compatibile con future versioni Odoo
- **Database migration**: Non necessaria (database vuoto)