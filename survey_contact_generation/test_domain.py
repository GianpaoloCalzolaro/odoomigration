#!/usr/bin/env python3
"""
Script di test per verificare la serializzazione dei domini
"""

# Simula il comportamento dei metodi compute
def test_domain_serialization():
    domain = [
        ("model", "=", "hr.applicant"),
        ("ttype", "in", ["char", "text"]),
        ("store", "=", True),
        ("readonly", "=", False),
    ]
    
    # Test 1: str() conversion
    str_domain = str(domain)
    print("Dominio come stringa:", str_domain)
    
    # Test 2: Parsing da stringa a lista
    try:
        import ast
        parsed_domain = ast.literal_eval(str_domain)
        print("Dominio parsato:", parsed_domain)
        print("Parsing riuscito:", parsed_domain == domain)
    except Exception as e:
        print("Errore nel parsing:", e)

if __name__ == "__main__":
    test_domain_serialization()
