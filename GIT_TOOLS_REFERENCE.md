# HAK-GAL Git Tools Referenz

## Verfügbare Git-Befehle über HAK-GAL MCP Tools

### Status-Befehle
```python
# Git Status
hak-gal-filesystem:git_status
  - path: Repository-Pfad
  
# Git Log (Commit-Historie)
hak-gal-filesystem:git_log
  - limit: Anzahl Commits
  - path: Repository-Pfad
  
# Git Branch
hak-gal-filesystem:git_branch
  - action: list|create|switch|delete
  - name: Branch-Name (optional)
  - path: Repository-Pfad
```

### Änderungs-Befehle
```python
# Git Commit
hak-gal-filesystem:git_commit
  - message: Commit-Nachricht
  - add_all: true/false (optional)
  - path: Repository-Pfad
  - auth_token: erforderlich
  
# Git Push
hak-gal-filesystem:git_push
  - branch: Branch-Name
  - remote: Remote-Name (default: origin)
  - path: Repository-Pfad
  - auth_token: erforderlich
  
# Git Pull
hak-gal-filesystem:git_pull
  - branch: Branch-Name
  - remote: Remote-Name (default: origin)
  - path: Repository-Pfad
```

## Beispiel-Workflow

### 1. Status prüfen
```
hak-gal-filesystem:git_status(path="D:\MCP Mods\HAK_GAL_HEXAGONAL")
```

### 2. Änderungen committen
```
hak-gal-filesystem:git_commit(
  message="Update documentation", 
  add_all=true, 
  path="D:\MCP Mods\HAK_GAL_HEXAGONAL",
  auth_token="515f57956e7bd15ddc3817573598f190"
)
```

### 3. Zum Remote pushen
```
hak-gal-filesystem:git_push(
  branch="main",
  remote="origin", 
  path="D:\MCP Mods\HAK_GAL_HEXAGONAL",
  auth_token="515f57956e7bd15ddc3817573598f190"
)
```

### 4. Updates vom Remote holen
```
hak-gal-filesystem:git_pull(
  branch="main",
  remote="origin",
  path="D:\MCP Mods\HAK_GAL_HEXAGONAL"
)
```

## Aktueller Repository-Status

- **Repository:** HAK-GAL-Hexagonal
- **GitHub URL:** https://github.com/sookoothaii/HAK-GAL-Hexagonal
- **Branch:** main
- **Letzter Commit:** 343d7f13 - PROJECT_HUB reorganization
- **Status:** ✅ Vollständig synchronisiert
- **Lokale Änderungen:** 203 uncommitted files (hauptsächlich Cleanup)

## Nächste Schritte

Falls Sie die lokalen Änderungen (gelöschte Batch-Dateien etc.) auch pushen möchten:

1. Review der Änderungen: `git_status`
2. Commit erstellen: `git_commit` mit aussagekräftiger Message
3. Push zum GitHub: `git_push`

---
*Generiert am 17.09.2025 mit HAK-GAL Git Tools*
