#!/usr/bin/env python3
"""
Einfacher UTF-8 Fix für delegate_task
Behebt den Encoding-Fehler bei Claude-Aufrufen
"""

import json

def fix_delegate_task():
    """Fixe die delegate_task Funktion für UTF-8 Safety"""
    
    print("=== UTF-8 FIX FÜR DELEGATE_TASK ===\n")
    
    # Test-Daten mit problematischen Zeichen
    test_data = {
        "task": "Analysiere HAK/GAL System",
        "context": {
            "special_chars": "äöüÄÖÜß€",
            "emoji": "🔧✅❌",
            "unicode": "你好世界"
        }
    }
    
    print("1. Test verschiedene JSON-Encoding-Methoden:\n")
    
    # Methode 1: Standard (kann Probleme verursachen)
    try:
        json1 = json.dumps(test_data)
        print(f"Standard json.dumps: OK")
        print(f"  Länge: {len(json1)} bytes")
    except Exception as e:
        print(f"Standard json.dumps: FEHLER - {e}")
    
    # Methode 2: Mit ensure_ascii=True (sicher für MCP)
    try:
        json2 = json.dumps(test_data, ensure_ascii=True)
        print(f"\njson.dumps mit ensure_ascii=True: OK")
        print(f"  Länge: {len(json2)} bytes")
        print(f"  Beispiel: {json2[:100]}...")
    except Exception as e:
        print(f"json.dumps mit ensure_ascii=True: FEHLER - {e}")
    
    # Methode 3: Mit ensure_ascii=False (für lokale Verwendung)
    try:
        json3 = json.dumps(test_data, ensure_ascii=False)
        print(f"\njson.dumps mit ensure_ascii=False: OK")
        print(f"  Länge: {len(json3)} bytes")
        print(f"  Beispiel: {json3[:100]}...")
    except Exception as e:
        print(f"json.dumps mit ensure_ascii=False: FEHLER - {e}")
    
    print("\n2. Empfehlung für MCP-Server:")
    print("   - Verwende IMMER ensure_ascii=True für:")
    print("     * send_response()")
    print("     * Tool-Result JSON")
    print("     * Delegate-Task Context")
    print("   - Verwende ensure_ascii=False nur für:")
    print("     * Lokale Dateien")
    print("     * Audit-Logs")
    
    print("\n3. Quick-Fix für aktuellen Fehler:")
    print("   In hakgal_mcp_ultimate.py:")
    print("   - Zeile 447: json.dumps(response, ensure_ascii=True)")
    print("   - Zeile 1990: json.dumps(context, ensure_ascii=True)")
    print("   - Zeile 2041: json.dumps(context, ensure_ascii=True)")
    print("   - Zeile 2105: json.dumps(context, ensure_ascii=True)")
    
    return True

def create_safe_wrapper():
    """Erstelle eine sichere JSON-Wrapper-Funktion"""
    
    def safe_json_dumps(data, for_transmission=True):
        """
        Sicherer JSON-Dumps Wrapper
        
        Args:
            data: Zu serialisierende Daten
            for_transmission: True für MCP/Network, False für lokale Dateien
        """
        if for_transmission:
            # Für Übertragung: ASCII-only
            return json.dumps(data, ensure_ascii=True)
        else:
            # Für lokale Speicherung: UTF-8
            return json.dumps(data, ensure_ascii=False, indent=2)
    
    return safe_json_dumps

if __name__ == "__main__":
    fix_delegate_task()
    
    print("\n" + "="*50)
    print("✅ UTF-8 Fix-Analyse abgeschlossen")
    print("="*50)
    
    # Test safe wrapper
    safe_dumps = create_safe_wrapper()
    test = {"message": "Hallo Welt! 你好 🌍"}
    
    print("\nSafe Wrapper Test:")
    print(f"  Für Transmission: {safe_dumps(test, for_transmission=True)}")
    print(f"  Für lokale Datei: {safe_dumps(test, for_transmission=False)}")
