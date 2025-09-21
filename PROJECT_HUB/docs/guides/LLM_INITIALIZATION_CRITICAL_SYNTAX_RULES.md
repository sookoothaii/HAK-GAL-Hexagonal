# LLM Initialization Critical Syntax Rules

**Generiert:** 2025-09-21  
**Zweck:** Prävention häufiger Interpretationsfehler bei LLM-Initialisierung

## Kritischer Filesystem-Path Interpretationsfehler (2025-09-21)

### Fehlerbeschreibung
**Problem:** `PROJECT_HUB` fälschlich zu `PROJECT HUB` konvertiert statt `PROJECT_HUB` zu belassen

**Korrekte Interpretation:**
- `D_MCP_Mods_HAK_GAL_HEXAGONAL_PROJECT_HUB` 
- = `D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB`

**Falsche Interpretation:**
- `D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT HUB` ❌

### Kontextsensitive Regel
**Nicht jeder Unterstrich = Dateisystem-Separator**
- Verzeichnisnamen mit Unterstrichen (`PROJECT_HUB`) müssen intakt bleiben
- Nur strukturelle Unterstriche zwischen Pfadelementen konvertieren

## Mandatory Syntax Search Requirement

### Step 0.5: Syntax-Regel-Suche (NEU)
Nach User Preferences Loading, vor Project Hub Exploration:

```
MANDATORY_SEARCHES = [
    "FileSystemPathConvention",
    "ProjectHubFileSystemLocation", 
    "LLMInitializationTemplateValidationChecklist",
    "NewLLMInstanceQuickReference"
]
```

### Implementation Rule
Jede neue LLM-Instanz MUSS vor dem ersten Filesystem-Zugriff die Syntax-Regeln aus der Knowledge Base laden.

## N-äre Fakten Syntax Reminder

**Korrekt:**
```
PredicateName(argument1:value1, argument2:value2, argument3:value3)
```

**Validation Checklist:**
- PascalCase für Prädikat-Namen ✓
- Unterstriche für zusammengesetzte Wörter ✓
- Doppelpunkt zwischen Argument und Wert ✓
- Kommas zwischen Argument-Wert-Paaren ✓
- Gesamter Fakt in Klammern ✓

## Quality Gate
Neue LLM-Instanzen müssen Syntax-Verständnis demonstrieren, bevor sie Filesystem-Operationen durchführen.
