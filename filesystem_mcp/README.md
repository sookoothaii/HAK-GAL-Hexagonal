# HAK_GAL Filesystem MCP Server v2.0

Ein dedizierter MCP Server für erweiterte Dateioperationen und Code-Ausführung, getrennt vom Haupt-KB-Server für saubere Architektur.

## Features

- **20 spezialisierte Tools** für Filesystem-Operationen (erweitert von 15)
- **Code-Ausführung** in 4 Sprachen (Python, JavaScript, Bash, PowerShell)
- **Erweiterte Datei-Tools** inkl. Diff, Hash, Tail
- **Batch-Copy** Tool für effiziente Datei-Kopien
- **Saubere Trennung** von KB und Filesystem-Operationen
- **Write-Protection** mit optionalem Auth-Token

## Tools (20 Total)

### Execution (1 Tool)
- `execute_code` - Führt Code sicher in Sandbox aus

### File Operations (10 Tools)
- `read_file` - Liest Dateiinhalt
- `write_file` - Schreibt Datei
- `list_files` - Listet Dateien
- `get_file_info` - Datei-Metadaten
- `directory_tree` - Zeigt Verzeichnisbaum
- `create_file` - Erstellt neue Datei
- `delete_file` - Löscht Datei/Verzeichnis
- `move_file` - Verschiebt/Benennt um
- `copy_batch` - Kopiert einzelne oder mehrere Dateien
- `create_directory` - **NEU!** Erstellt Verzeichnis (rekursiv)

### Analysis & Comparison (3 Tools)
- `file_diff` - **NEU!** Vergleicht zwei Dateien
- `calculate_hash` - **NEU!** Berechnet Datei-Hash (MD5, SHA1, SHA256)
- `tail_file` - **NEU!** Zeigt letzte N Zeilen (ideal für Logs)

### Search & Edit (5 Tools)
- `grep` - Sucht Muster in Dateien
- `find_files` - Findet Dateien nach Muster
- `search` - Einheitliche Suche
- `edit_file` - Ersetzt Text in Datei
- `multi_edit` - Mehrfach-Ersetzungen

### Code Tools (1 Tool)
- `format_code` - **NEU!** Formatiert Python-Code

## Installation

```bash
cd D:\MCP Mods\HAK_GAL_HEXAGONAL\filesystem_mcp
pip install -r requirements.txt
```

## Verwendung

### Standalone
```bash
python hak_gal_filesystem.py
```

### Mit mehreren MCP Servern in Claude Desktop

Fügen Sie zu Ihrer Claude Desktop Config (`%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "hak-gal-kb": {
      "command": "python",
      "args": ["D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\ultimate_mcp\\hakgal_mcp_ultimate.py"],
      "env": {
        "HAKGAL_WRITE_TOKEN": "your-token"
      }
    },
    "hak-gal-filesystem": {
      "command": "python",
      "args": ["D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\filesystem_mcp\\hak_gal_filesystem.py"],
      "env": {
        "HAKGAL_WRITE_TOKEN": "your-token"
      }
    }
  }
}
```

## Neue Tools in v2.0

### create_directory
```json
{
  "name": "create_directory",
  "arguments": {
    "path": "D:/projects/new_project/src",
    "auth_token": "your-token"
  }
}
```

### file_diff
```json
{
  "name": "file_diff",
  "arguments": {
    "file1": "original.py",
    "file2": "modified.py",
    "context_lines": 3
  }
}
```

### calculate_hash
```json
{
  "name": "calculate_hash",
  "arguments": {
    "path": "important_file.zip",
    "algorithm": "sha256"
  }
}
```

### tail_file
```json
{
  "name": "tail_file",
  "arguments": {
    "path": "application.log",
    "lines": 50
  }
}
```

### format_code
```json
{
  "name": "format_code",
  "arguments": {
    "path": "messy_code.py",
    "auth_token": "your-token"
  }
}
```

## Konfiguration

### Environment Variables
```
HAKGAL_WRITE_ENABLED=true       # Write-Operationen erlauben
HAKGAL_WRITE_TOKEN=secret       # Optional: Token für Schreibschutz
MCP_EXEC_MAX_OUTPUT=50000       # Max Output-Größe
MCP_EXEC_TIMEOUT_PY=30          # Python Timeout
MCP_EXEC_TIMEOUT_JS=30          # JavaScript Timeout
MCP_EXEC_TIMEOUT_SH=30          # Bash Timeout
MCP_EXEC_TIMEOUT_PS=30          # PowerShell Timeout
```

## Zukünftige Erweiterungen

Für folgende Tools wären zusätzliche Dependencies nötig:
- `archive_extract` / `archive_create` (ZIP/TAR support)
- `compile_code` (Compiler-Support)
- `lint_code` (Linter-Integration)
- `get_tech_stack` (Projekt-Analyse)

Diese können bei Bedarf in v3.0 ergänzt werden.

## Changelog

### v2.0.0 (2025-01-18)
- Added `create_directory` - Directory creation
- Added `file_diff` - File comparison
- Added `calculate_hash` - File checksums
- Added `tail_file` - Log file monitoring
- Added `format_code` - Basic Python formatting
- Total tools increased from 15 to 20

### v1.0.0 (2025-01-18)
- Initial release with 15 tools
- Basic file operations
- Code execution
- Search and edit capabilities

## Logs

- Hauptlog: `D:\MCP Mods\HAK_GAL_HEXAGONAL\filesystem_mcp.log`
- Execution temp: `%TEMP%\hakgal_filesystem_exec\`

## Version

2.0.0 - Enhanced with 5 additional tools
