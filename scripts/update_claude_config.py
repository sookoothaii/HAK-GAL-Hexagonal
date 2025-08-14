#!/usr/bin/env python3
"""
Update Claude Desktop configuration (claude_desktop_config.json)
 - Creates file if missing
 - Backs up existing file with timestamp
 - Ensures mcpServers.hak-gal points to hak_gal_mcp_fixed.py via python -u
"""

import json
import os
from pathlib import Path
from datetime import datetime


def main() -> None:
    appdata = os.environ.get("APPDATA", "")
    config_path = Path(appdata) / "Claude" / "claude_desktop_config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Load or initialize config
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            config = {}
    else:
        config = {}

    # Backup
    if config_path.exists():
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = config_path.with_suffix(config_path.suffix + f".bak.{ts}")
        try:
            backup_path.write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")
        except Exception:
            pass

    # Ensure structure
    if not isinstance(config, dict):
        config = {}
    mcp = config.get("mcpServers")
    if not isinstance(mcp, dict):
        mcp = {}
        config["mcpServers"] = mcp

    # Determine preferred Python executable
    venv_hexa = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/.venv_hexa/Scripts/python.exe")
    venv_std = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/.venv/Scripts/python.exe")
    if venv_hexa.exists():
        python_cmd = str(venv_hexa).replace('/', '\\')
    elif venv_std.exists():
        python_cmd = str(venv_std).replace('/', '\\')
    else:
        python_cmd = "python"

    # Set server entry (both keys to be safe) using command string + args array per Claude schema
    server_entry = {
        "command": python_cmd,
        "args": [
            "-u",
            "-m",
            "hak_gal_mcp"
        ],
        "env": {
            "PYTHONIOENCODING": "utf-8",
            "PYTHONPATH": "D:\\MCP Mods\\HAK_GAL_HEXAGONAL"
        }
    }
    mcp["hak-gal"] = server_entry
    mcp["hak_gal"] = server_entry

    # Write back
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(str(config_path))
    print("Updated configuration:")
    print(json.dumps(config, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()


