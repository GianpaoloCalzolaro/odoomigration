#!/usr/bin/env python3
"""
Script di test per verificare l'installazione del modulo Survey Multiple Certification
"""

import sys
import os

def check_module_structure():
    """Verifica la struttura del modulo"""
    required_files = [
        '__manifest__.py',
        '__init__.py',
        'models/__init__.py',
        'models/survey_survey.py',
        'models/survey_certification_threshold.py',
        'models/survey_user_input.py',
        'models/survey_user_input_history.py',
        'security/ir.model.access.csv',
        'security/survey_multiple_certification_security.xml',
        'views/survey_survey_views.xml',
        'views/survey_certification_threshold_views.xml',
        'views/survey_user_input_views.xml',
        'wizard/__init__.py',
        'wizard/survey_threshold_wizard.py',
        'wizard/survey_threshold_wizard_line.py',
        'wizard/survey_threshold_wizard_views.xml',
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ File mancanti:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ Tutti i file richiesti sono presenti")
        return True

def check_manifest():
    """Verifica il manifest"""
    try:
        with open('__manifest__.py', 'r', encoding='utf-8') as f:
            manifest_content = f.read()
        
        # Verifica che contenga le dipendenze necessarie
        required_deps = ['survey', 'gamification', 'web']
        for dep in required_deps:
            if f"'{dep}'" not in manifest_content:
                print(f"❌ Dipendenza mancante: {dep}")
                return False
        
        print("✅ Manifest corretto")
        return True
    except Exception as e:
        print(f"❌ Errore nel manifest: {e}")
        return False

def check_python_syntax():
    """Verifica la sintassi Python"""
    python_files = [
        '__init__.py',
        'models/__init__.py',
        'models/survey_survey.py',
        'models/survey_certification_threshold.py',
        'models/survey_user_input.py',
        'models/survey_user_input_history.py',
        'wizard/__init__.py',
        'wizard/survey_threshold_wizard.py',
        'wizard/survey_threshold_wizard_line.py',
    ]
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), file_path, 'exec')
        except SyntaxError as e:
            print(f"❌ Errore di sintassi in {file_path}: {e}")
            return False
        except Exception as e:
            print(f"❌ Errore in {file_path}: {e}")
            return False
    
    print("✅ Sintassi Python corretta")
    return True

def main():
    """Funzione principale"""
    print("🔍 Verifica modulo Survey Multiple Certification")
    print("=" * 50)
    
    all_checks_passed = True
    
    # Verifica struttura
    if not check_module_structure():
        all_checks_passed = False
    
    # Verifica manifest
    if not check_manifest():
        all_checks_passed = False
    
    # Verifica sintassi Python
    if not check_python_syntax():
        all_checks_passed = False
    
    print("=" * 50)
    if all_checks_passed:
        print("🎉 Tutte le verifiche sono passate! Il modulo è pronto per l'installazione.")
        print("\nPer installare il modulo:")
        print("1. Copiare la cartella in addons-path di Odoo")
        print("2. Riavviare Odoo con -u all o installare dal menu Apps")
        print("3. Cercare 'Survey Multiple Certification' e installare")
    else:
        print("❌ Alcune verifiche sono fallite. Controllare gli errori sopra.")
        sys.exit(1)

if __name__ == "__main__":
    main()
