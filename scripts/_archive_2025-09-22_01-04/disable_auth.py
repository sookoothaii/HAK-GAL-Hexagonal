#!/usr/bin/env python3
"""
Deaktiviert API-Key-Anforderung im Backend
===========================================
Nur für Entwicklung/Testing!
"""

from pathlib import Path
import shutil

def disable_api_key_requirement():
    """Kommentiert @require_api_key decorator aus"""
    
    api_file = Path("src_hexagonal/hexagonal_api_enhanced_clean.py")
    
    if not api_file.exists():
        print(f"❌ Datei nicht gefunden: {api_file}")
        return False
    
    # Backup erstellen
    backup = api_file.with_suffix('.py.backup_with_auth')
    if not backup.exists():
        shutil.copy(api_file, backup)
        print(f"✅ Backup erstellt: {backup}")
    
    # Inhalt lesen
    content = api_file.read_text(encoding='utf-8', errors='ignore')
    
    # @require_api_key auskommentieren
    new_content = content.replace(
        "@require_api_key",
        "# @require_api_key  # TEMPORÄR DEAKTIVIERT"
    )
    
    # Änderungen zählen
    changes = content.count("@require_api_key") - new_content.count("@require_api_key")
    
    if changes > 0:
        api_file.write_text(new_content, encoding='utf-8')
        print(f"✅ {changes} API-Key-Anforderungen deaktiviert")
        return True
    else:
        print("ℹ️ Keine Änderungen nötig (bereits deaktiviert)")
        return True

def main():
    print("=" * 60)
    print("API-KEY-ANFORDERUNG DEAKTIVIEREN")
    print("=" * 60)
    print("\n⚠️ ACHTUNG: Nur für Entwicklung/Testing!")
    print("In Produktion sollte die Authentifizierung aktiv sein!\n")
    
    if disable_api_key_requirement():
        print("\n✅ Erfolgreich! Backend muss neu gestartet werden.")
        print("\nNächste Schritte:")
        print("1. Backend stoppen (Ctrl+C)")
        print("2. Backend neu starten")
        print("3. Fakten sollten jetzt ohne API-Key hinzugefügt werden können")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
