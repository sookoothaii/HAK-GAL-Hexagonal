# Dateien die aus GitHub entfernt werden sollten

## 🔴 DEFINITIV ENTFERNEN:

### Temporäre/Debug-Dateien:
- `audit_report_20250911_190429.json` - Lokaler Audit-Report
- `governance_monitor.html` - Temporäres Monitoring HTML
- `mcp_server.jsonl` - Server Log-Datei
- `emergency_dumps/` - Kompletter Ordner (Crash-Dumps)

### Generierte Analyse-Reports:
- `mcp_tools_extracted.json` - Generierte Tool-Liste
- `node_catalog.csv` - Generierte Katalog-Datei
- `node_catalog.json` - Generierte Katalog-Datei  
- `node_catalog_analysis.json` - Analyse-Output
- `node_catalog_debug.json` - Debug-Output
- `tools_diff_report.csv` - Diff-Report
- `tools_diff_report.json` - Diff-Report

### Datenbank (sollte heruntergeladen werden):
- `hexagonal_kb.db` - SQLite DB (2.85 MB) - User soll download_kb.sh nutzen!

### Build-Artefakte:
- `package-lock.json` - NPM lock file (kontrovers, aber oft excluded)

## 🟡 MÖGLICHERWEISE ENTFERNEN:

### Snapshots (je nach Verwendung):
- `snapshots/` - Wenn nur für lokale Tests

### Test-Ordner:
- `test_filesystem/` - Wenn nur Test-Outputs enthält

## ✅ BEHALTEN (aber bereits in .gitignore?):

### Lokale Configs (sollten in .gitignore sein):
- `.env` (falls vorhanden)
- Lokale Claude Desktop configs

## EMPFOHLENE .gitignore ERGÄNZUNGEN:

```gitignore
# Database (users should download)
hexagonal_kb.db
*.db

# Reports and Analysis
audit_report_*.json
*_report.json
*_report.csv
node_catalog*.json
node_catalog*.csv
mcp_tools_extracted.json
tools_diff_*.json
tools_diff_*.csv

# Debug and Monitoring
governance_monitor.html
*.jsonl
mcp_server.jsonl

# Emergency/Crash dumps
emergency_dumps/
*.dump
*.crash

# Test outputs
test_filesystem/
test_outputs/
*.test.json

# Snapshots (if local only)
snapshots/

# IDE and Editor
.vscode/
.idea/
*.swp
*.swo

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv*/
venv*/
ENV*/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# OS
.DS_Store
Thumbs.db
desktop.ini

# Backup files  
*.backup*
*_backup.*
*_old.*
*_fixed.*
```
