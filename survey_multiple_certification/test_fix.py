#!/usr/bin/env python3
"""
Script di test per verificare la risoluzione dell'errore 
"No default view of type 'tree' could be found"
"""

import xml.etree.ElementTree as ET
import os

def test_xml_validity():
    """Test che i file XML siano validi"""
    xml_files = [
        'views/survey_certification_threshold_views.xml',
        'views/survey_survey_views.xml'
    ]
    
    for xml_file in xml_files:
        if os.path.exists(xml_file):
            try:
                ET.parse(xml_file)
                print(f"✓ {xml_file} è un XML valido")
            except ET.ParseError as e:
                print(f"✗ {xml_file} contiene errori XML: {e}")
        else:
            print(f"✗ {xml_file} non trovato")

def test_action_window_exists():
    """Test che l'action window sia stato creato"""
    xml_file = 'views/survey_certification_threshold_views.xml'
    if not os.path.exists(xml_file):
        print(f"✗ {xml_file} non trovato")
        return
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Cerca l'action window
        action_found = False
        for record in root.findall(".//record[@id='action_survey_certification_threshold']"):
            if record.get('model') == 'ir.actions.act_window':
                action_found = True
                print("✓ Action window 'action_survey_certification_threshold' trovato")
                break
        
        if not action_found:
            print("✗ Action window 'action_survey_certification_threshold' non trovato")
            
        # Cerca il menu item
        menu_found = False
        for menuitem in root.findall(".//menuitem[@id='menu_survey_certification_thresholds']"):
            menu_found = True
            print("✓ Menu item 'menu_survey_certification_thresholds' trovato")
            break
            
        if not menu_found:
            print("✗ Menu item 'menu_survey_certification_thresholds' non trovato")
            
    except ET.ParseError as e:
        print(f"✗ Errore nel parsing di {xml_file}: {e}")

def test_file_order_in_manifest():
    """Test che l'ordine dei file nel manifest sia corretto"""
    manifest_file = '__manifest__.py'
    if not os.path.exists(manifest_file):
        print(f"✗ {manifest_file} non trovato")
        return
    
    with open(manifest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Trova la posizione dei file critici
    threshold_views_pos = content.find("'views/survey_certification_threshold_views.xml'")
    survey_views_pos = content.find("'views/survey_survey_views.xml'")
    
    if threshold_views_pos == -1:
        print("✗ 'views/survey_certification_threshold_views.xml' non trovato in __manifest__.py")
    elif survey_views_pos == -1:
        print("✗ 'views/survey_survey_views.xml' non trovato in __manifest__.py")
    elif threshold_views_pos < survey_views_pos:
        print("✓ Ordine dei file nel manifest è corretto (threshold_views prima di survey_views)")
    else:
        print("✗ Ordine dei file nel manifest non è corretto")

if __name__ == "__main__":
    print("=== TEST RISOLUZIONE ERRORE SURVEY MULTIPLE CERTIFICATION ===")
    print()
    
    test_xml_validity()
    print()
    
    test_action_window_exists()
    print()
    
    test_file_order_in_manifest()
    print()
    
    print("=== FINE TEST ===")