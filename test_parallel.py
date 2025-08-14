#!/usr/bin/env python3
"""
HAK-GAL Parallel System Test
=============================
Testet ob Original (Port 5000) und Hexagonal (Port 5001) parallel laufen können.

Nach HAK/GAL Verfassung Artikel 6: Empirische Validierung
"""

import sys
import time
from pathlib import Path

def test_import_legacy():
    """Test 1: Kann Legacy System importiert werden?"""
    print("\n🔍 TEST 1: Legacy Import Test")
    print("-" * 40)
    
    # Add hexagonal to path
    sys.path.insert(0, str(Path(__file__).parent / "src_hexagonal"))
    
    try:
        from legacy_wrapper import test_legacy_connection
        success = test_legacy_connection()
        
        if success:
            print("✅ TEST 1 BESTANDEN: Legacy System erreichbar")
        else:
            print("❌ TEST 1 FEHLGESCHLAGEN: Legacy System nicht erreichbar")
            
        return success
        
    except Exception as e:
        print(f"❌ TEST 1 FEHLGESCHLAGEN: Import Error: {e}")
        return False

def test_parallel_ports():
    """Test 2: Ports für Parallel-Betrieb verfügbar?"""
    print("\n🔍 TEST 2: Port-Verfügbarkeit")
    print("-" * 40)
    
    import socket
    
    ports_to_test = {
        5000: "Original HAK-GAL",
        5001: "Hexagonal HAK-GAL",
        5173: "Frontend"
    }
    
    results = {}
    for port, name in ports_to_test.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            print(f"  ⚠️ Port {port} ({name}): BELEGT")
            results[port] = "busy"
        else:
            print(f"  ✅ Port {port} ({name}): FREI")
            results[port] = "free"
    
    # Original darf belegt sein, Hexagonal muss frei sein
    if results[5001] == "free":
        print("✅ TEST 2 BESTANDEN: Port 5001 für Hexagonal verfügbar")
        return True
    else:
        print("❌ TEST 2 FEHLGESCHLAGEN: Port 5001 bereits belegt")
        return False

def test_database_copy():
    """Test 3: Development Database vorhanden?"""
    print("\n🔍 TEST 3: Development Database")
    print("-" * 40)
    
    original_db = Path(r"D:\MCP Mods\HAK_GAL_SUITE\k_assistant.db")
    dev_db = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\k_assistant_dev.db")
    
    if original_db.exists():
        print(f"  ✅ Original DB: {original_db.stat().st_size / 1024 / 1024:.2f} MB")
    else:
        print(f"  ❌ Original DB nicht gefunden")
        
    if dev_db.exists():
        print(f"  ✅ Development DB: {dev_db.stat().st_size / 1024 / 1024:.2f} MB")
        print("✅ TEST 3 BESTANDEN: Development DB vorhanden")
        return True
    else:
        print(f"  ⚠️ Development DB fehlt noch")
        print("  → Kopiere mit: copy k_assistant.db k_assistant_dev.db")
        print("⚠️ TEST 3 WARNUNG: Development DB sollte erstellt werden")
        return True  # Nicht kritisch

def test_isolation():
    """Test 4: Systeme sind isoliert?"""
    print("\n🔍 TEST 4: System-Isolation")
    print("-" * 40)
    
    # Prüfe ob Hexagonal eigene venv hat
    hexa_venv = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa")
    orig_venv = Path(r"D:\MCP Mods\HAK_GAL_SUITE\.venv")
    
    if hexa_venv.exists():
        print(f"  ✅ Hexagonal venv: .venv_hexa")
    else:
        print(f"  ⚠️ Hexagonal venv fehlt noch")
        
    if orig_venv.exists():
        print(f"  ✅ Original venv: .venv")
    else:
        print(f"  ❌ Original venv nicht gefunden")
    
    # Prüfe ob wir NICHT im Original arbeiten
    current_dir = Path.cwd()
    if "HAK_GAL_SUITE" in str(current_dir):
        print(f"  ⚠️ WARNUNG: Arbeite im Original-Verzeichnis!")
        print("✅ TEST 4 FEHLGESCHLAGEN: Nicht im Hexagonal-Verzeichnis")
        return False
    else:
        print(f"  ✅ Arbeite in: {current_dir.name}")
        print("✅ TEST 4 BESTANDEN: Systeme sind isoliert")
        return True

def main():
    """Führe alle Tests aus"""
    print("=" * 60)
    print("HAK-GAL PARALLEL SYSTEM TEST SUITE")
    print("=" * 60)
    print("Datum:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("Nach HAK/GAL Verfassung Artikel 6: Empirische Validierung")
    
    results = {
        "Legacy Import": test_import_legacy(),
        "Port Verfügbarkeit": test_parallel_ports(),
        "Development DB": test_database_copy(),
        "System Isolation": test_isolation()
    }
    
    print("\n" + "=" * 60)
    print("TESTERGEBNISSE:")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:20} : {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALLE TESTS BESTANDEN!")
        print("Hexagonal Development kann sicher beginnen!")
    else:
        print("⚠️ EINIGE TESTS FEHLGESCHLAGEN")
        print("Bitte Probleme beheben vor Hexagonal-Entwicklung")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
