# GitHub Repository Final Cleanup Checklist
## Stand: 21.01.2025

### 1. Sofort-Maßnahmen (Git-kritisch):
- [ ] **Große Dateien löschen** (122.7 MB):
  - `mcp_server.log` (47.8 MB)
  - `mcp_server.jsonl` (31.9 MB)
  - `caddy.exe` (42.9 MB)

### 2. ROOT_CLEANUP_V2.py ausführen:
```bash
python ROOT_CLEANUP_V2.py
```

### 3. Archive löschen:
- [ ] `_cleanup_archive_2025-09-22/` Ordner entfernen
- [ ] `scripts/_archive_2025-09-22_01-04/` Ordner entfernen

### 4. .gitignore aktualisieren:
```gitignore
# Große Dateien
*.log
*.jsonl
*.exe

# Temporäre DB-Dateien  
*.db-shm
*.db-wal

# Archive
_cleanup_archive_*/
_archive_*/

# Reports und Validierung
*_report.json
*_batch.json
verification_report_*.json
```

### 5. Git-Befehle zum Abschluss:
```bash
git add .gitignore
git rm --cached mcp_server.log mcp_server.jsonl caddy.exe
git add -A
git commit -m "Final cleanup: Remove large files and organize root directory"
git push
```

### Verifizierung:
- [ ] Keine Dateien > 100 MB im Repository
- [ ] Root-Verzeichnis enthält nur essenzielle Dateien
- [ ] .gitignore verhindert zukünftige Probleme
