#!/usr/bin/env python3
"""Backup script for HAK_GAL MCP Server files"""

import shutil
from pathlib import Path
from datetime import datetime

# Source file
source = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/scripts/hak_gal_mcp_fixed.py")

# Create backup with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/backups")
backup_dir.mkdir(parents=True, exist_ok=True)

backup_file = backup_dir / f"hak_gal_mcp_fixed_backup_{timestamp}.py"

# Copy the file
if source.exists():
    shutil.copy2(source, backup_file)
    print(f"✅ Backup created: {backup_file}")
    print(f"   Size: {backup_file.stat().st_size} bytes")
else:
    print(f"❌ Source file not found: {source}")
