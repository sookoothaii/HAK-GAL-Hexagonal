#!/usr/bin/env python3
"""
Installiert/fixt die Claude Desktop MCP-Konfiguration:
- Setzt mcpServers['hak-gal'] auf command=str('python') und args=[<hak_gal_mcp_v2.py>]
- Legt ein Backup der bisherigen Datei an
"""

import json
import os
from pathlib import Path
from datetime import datetime


def main() -> None:
    appdata = os.environ.get("APPDATA", "")
    config_path = Path(appdata) / "Claude" / "claude_desktop_config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Backup
    if config_path.exists():
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        backup = config_path.with_suffix(config_path.suffix + f".bak.{ts}")
        try:
            backup.write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"Backup: {backup}")
        except Exception:
            pass

    # Load or init
    try:
        config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    except Exception:
        config = {}

    if not isinstance(config, dict):
        config = {}
    mcp = config.get("mcpServers")
    if not isinstance(mcp, dict):
        mcp = {}
        config["mcpServers"] = mcp

    # Prefer pinned venv python if available
    venv_hexa = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/.venv_hexa/Scripts/python.exe")
    preferred_python = str(venv_hexa).replace('/', '\\') if venv_hexa.exists() else "python"

    # Write entry → benutze den "fixed" Server mit korrektem MCP-Initialize & tools/list
    server_entry = {
        "command": preferred_python,
        "args": [
            "-u",
            "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hak_gal_mcp_fixed.py"
        ],
        "env": {
            "PYTHONIOENCODING": "utf-8",
            "PYTHONPATH": "D:\\MCP Mods\\HAK_GAL_HEXAGONAL"
        }
    }
    mcp["hak-gal"] = server_entry
    mcp["hak_gal"] = server_entry

    # Save
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")

    # Verify types
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    entry = (cfg.get("mcpServers") or {}).get("hak-gal", {})
    cmd = entry.get("command")
    args = entry.get("args")
    print("Updated:", str(config_path))
    print("command:", cmd, f"(type={type(cmd).__name__})")
    print("args:", args, f"(type={type(args).__name__})")


if __name__ == "__main__":
    main()

import os, json

# Config-Pfad
config_path = os.path.join(os.environ['APPDATA'], 'Claude', 'claude_desktop_config.json')
print(f"Config-Pfad: {config_path}")

# Backup erstellen
backup_path = config_path + '.backup'
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup erstellt: {backup_path}")
except:
    print("⚠️ Keine existierende Config gefunden")

# Config laden oder neu erstellen
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print("✅ Existierende Config geladen")
except:
    config = {}
    print("📝 Neue Config wird erstellt")

# HAK-GAL MCP Server hinzufügen
if 'mcpServers' not in config:
    config['mcpServers'] = {}
    print("📝 mcpServers Sektion erstellt")

# HAK-GAL konfigurieren (mit korrektem Format!)
config['mcpServers']['hak-gal'] = {
    'command': 'python',  # STRING, nicht Array!
    'args': ['D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hak_gal_mcp_v2.py']
}
print("✅ HAK-GAL MCP Server konfiguriert")

# Config speichern
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2)
    
print("\n" + "="*50)
print("✅ CONFIG ERFOLGREICH INSTALLIERT!")
print("="*50)
print("\nNächste Schritte:")
print("1. Claude KOMPLETT beenden (auch System Tray)")
print("2. Claude neu starten")
print("3. Testen mit: 'What MCP tools do you have?'")
print("\nErwartete Tools:")
print("- search_knowledge")
print("- get_system_status")
