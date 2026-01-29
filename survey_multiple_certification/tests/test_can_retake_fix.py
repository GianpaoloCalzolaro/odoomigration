#!/usr/bin/env python3
"""
Script di test per verificare la risoluzione dell'errore answer.can_retake
"""

import os
import re

def test_can_retake_fix():
    """Test che la fix per can_retake sia stata applicata correttamente"""
    
    print("=== TEST FIX CAN_RETAKE ===")
    print()
    
    # Test 1: Verifica che answer.can_retake non sia più presente nei template
    print("1. Verificando che answer.can_retake sia stato rimosso dai template...")
    
    template_file = 'views/survey_templates.xml'
    if os.path.exists(template_file):
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'answer.can_retake' in content:
            print(f"   ❌ ERRORE: answer.can_retake ancora presente in {template_file}")
            return False
        else:
            print(f"   ✅ OK: answer.can_retake rimosso da {template_file}")
    else:
        print(f"   ❌ ERRORE: {template_file} non trovato")
        return False
    
    # Test 2: Verifica che can_retake sia presente nel template
    print("\n2. Verificando che can_retake sia presente nel template...")
    
    if 'can_retake' in content and 't-if="can_retake"' in content:
        print(f"   ✅ OK: can_retake presente in {template_file}")
    else:
        print(f"   ❌ ERRORE: can_retake non trovato in {template_file}")
        return False
    
    # Test 3: Verifica che la logica can_retake sia presente nel controller
    print("\n3. Verificando che la logica can_retake sia presente nel controller...")
    
    controller_file = 'controllers/main.py'
    if os.path.exists(controller_file):
        with open(controller_file, 'r', encoding='utf-8') as f:
            controller_content = f.read()
        
        # Cerca i pattern chiave
        patterns = [
            r"can_retake\s*=",
            r"response\.qcontext\['can_retake'\]",
            r"# Questa logica sostituisce il campo answer\.can_retake"
        ]
        
        all_patterns_found = True
        for pattern in patterns:
            if not re.search(pattern, controller_content):
                print(f"   ❌ ERRORE: Pattern '{pattern}' non trovato nel controller")
                all_patterns_found = False
        
        if all_patterns_found:
            print(f"   ✅ OK: Logica can_retake presente in {controller_file}")
        else:
            return False
    else:
        print(f"   ❌ ERRORE: {controller_file} non trovato")
        return False
    
    # Test 4: Verifica che il commento esplicativo sia presente
    print("\n4. Verificando che i commenti esplicativi siano presenti...")
    
    if "Questa logica sostituisce il campo answer.can_retake che non esiste nel modello" in controller_content:
        print("   ✅ OK: Commento esplicativo presente nel controller")
    else:
        print("   ❌ ERRORE: Commento esplicativo mancante nel controller")
        return False
    
    print("\n=== TUTTI I TEST PASSATI ===")
    print("✅ La fix per answer.can_retake è stata applicata correttamente!")
    print()
    print("Prossimi passi:")
    print("1. Riavviare Odoo per caricare le modifiche")
    print("2. Testare completando un sondaggio")
    print("3. Verificare che non ci siano più errori alla fine del sondaggio")
    print("4. Verificare che il pulsante 'Ripeti il test' appaia quando appropriato")
    
    return True

if __name__ == "__main__":
    success = test_can_retake_fix()
    if not success:
        print("\n❌ ALCUNI TEST SONO FALLITI")
        exit(1)
    else:
        print("\n🎉 TUTTI I TEST SONO PASSATI!")