# Git Cleanup Plan für HAK-GAL

## Situation
- Kein GitHub Remote verbunden
- 20+ uncommittete Änderungen
- Viele gelöschte Dokumentations-Dateien

## Empfohlene Schritte

### 1. Backup erstellen
```bash
# Komplettes Backup des aktuellen Zustands
cd "D:\MCP Mods"
xcopy "HAK_GAL_HEXAGONAL" "HAK_GAL_HEXAGONAL_BACKUP_$(date +%Y%m%d)" /E /I
```

### 2. Git-Status analysieren
```bash
cd "D:\MCP Mods\HAK_GAL_HEXAGONAL"
git status > git_status_report.txt
git diff > git_diff_report.txt
```

### 3. Entscheidung treffen

#### Option A: Alles committen (Quick & Dirty)
```bash
git add -A
git commit -m "WIP: Checkpoint before major refactoring - includes deletions and experiments"
```

#### Option B: Selektives Cleanup (Sauber)
```bash
# Gelöschte Docs wiederherstellen (falls wichtig)
git checkout -- CLAUDE_DESKTOP_MANUAL_CONFIG.md
git checkout -- MCP_README.md
# ... etc

# Nur wichtige Änderungen committen
git add .claude/settings.local.json
git add .cursor/mcp.json
git commit -m "config: Update Claude and Cursor settings"

# Rest in separaten Commit
git add CLAUDE.md GEMINI.md
git commit -m "docs: Update LLM context files"
```

### 4. GitHub Repository

**Frage:** Haben Sie ein GitHub Repository für dieses Projekt?
- Falls JA → Remote hinzufügen und pushen
- Falls NEIN → Neues Repository erstellen

## Nächste Schritte NACH Git-Cleanup

Erst wenn Git sauber ist:
1. Feature-Branch erstellen
2. Plugin-System entwickeln
3. Regelmäßige Commits
4. GitHub synchron halten

## Warnung
Ohne saubere Versionskontrolle riskieren Sie:
- Verlust von Arbeit
- Keine Rollback-Möglichkeit
- Schwierige Zusammenarbeit
- Keine Historie der Änderungen
