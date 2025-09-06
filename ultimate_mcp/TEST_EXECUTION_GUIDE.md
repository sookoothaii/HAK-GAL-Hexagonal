# HAK-GAL Critical Tools Test Execution Guide

## 📋 Test-Übersicht

**11 Neue Tools** | **28 Test Cases** | **3 Test-Methoden**

### 🧪 Getestete Tools:

| Tool | Tests | Kritisch | Status |
|------|--------|----------|--------|
| 1. `evaluate_expression` | 5 | ✅ Ja | Mathematische/logische Ausdrücke |
| 2. `set_variable` | 4 | ✅ Ja | Workflow-Variablen setzen |
| 3. `get_variable` | 2 | ✅ Ja | Workflow-Variablen lesen |
| 4. `merge_branches` | 3 | ✅ Ja | Branch-Ergebnisse zusammenführen |
| 5. `wait_for_all` | 1 | ✅ Ja | Auf parallele Nodes warten |
| 6. `no_op` | 2 | ✅ Ja | Platzhalter-Node |
| 7. `comment` | 2 | ✅ Ja | Dokumentations-Node |
| 8. `metrics_collector` | 2 | ⚡ Nice | Performance-Metriken |
| 9. `workflow_status` | 1 | ⚡ Nice | Workflow-Status |
| 10. `cron_validator` | 4 | ⚡ Nice | Cron-Ausdrücke validieren |
| 11. `recurring_schedule` | 2 | ⚡ Nice | Wiederkehrende Schedules |

## 🚀 Test-Ausführung

### Option 1: Quick Test (Bash Script)
```bash
cd D:\MCP Mods\HAK_GAL_HEXAGONAL\ultimate_mcp
bash test_critical_tools.sh
```

### Option 2: Postman Collection
1. Öffnen Sie Postman
2. Import > Upload Files
3. Wählen Sie `HAK_GAL_Critical_Tools.postman_collection.json`
4. Set Environment Variable: `base_url = http://localhost:5002`
5. Run Collection

### Option 3: Automated Tests (pytest)
```bash
cd D:\MCP Mods\HAK_GAL_HEXAGONAL\ultimate_mcp
pip install pytest requests
pytest test_critical_tools_pytest.py -v
```

## 📊 Test-Beispiele

### 1. Expression Evaluation
```json
{
  "tool": "evaluate_expression",
  "arguments": {
    "expression": "x * 2 + y",
    "variables": {"x": 5, "y": 3}
  }
}
// Expected: {"result": 13, "type": "int"}
```

### 2. Branch Merging
```json
{
  "tool": "merge_branches",
  "arguments": {
    "branch_results": [
      {"success": true, "data": "A"},
      {"success": false, "data": "B"}
    ],
    "strategy": "first_success"
  }
}
// Expected: {"selected_branch": 0, "merged_data": {...}}
```

### 3. Cron Validation
```json
{
  "tool": "cron_validator",
  "arguments": {
    "expression": "0 9 * * MON-FRI"
  }
}
// Expected: {"valid": true, "fields": 5}
```

## ⚠️ Vor dem Testen

1. **Backend läuft?**
   ```bash
   cd D:\MCP Mods\HAK_GAL_HEXAGONAL
   python ultimate_mcp\hakgal_mcp_ultimate.py
   ```

2. **API läuft?** (Port 5002)
   ```bash
   cd D:\MCP Mods\HAK_GAL_HEXAGONAL
   python src_hexagonal\hexagonal_api_enhanced_clean.py
   ```

3. **Tools integriert?**
   - Backend: Tool-Definitionen und Implementierungen hinzugefügt
   - Frontend: NODE_CATALOG erweitert

## 📈 Erwartete Ergebnisse

✅ **Erfolgreiche Tests:**
- Expression evaluation mit Variablen
- Variable set/get Operationen
- Branch merging Strategien
- Cron-Validierung

⚠️ **Bekannte Einschränkungen:**
- `get_variable` benötigt Workflow-Kontext (gibt Default zurück)
- `wait_for_all` ist ein Koordinations-Placeholder
- `workflow_status` benötigt laufende Workflow-Engine

## 🔧 Troubleshooting

**Problem:** "Tool not found"
- Lösung: Tools zur `_get_tool_list()` hinzufügen

**Problem:** "Unknown tool in handle_tool_call"
- Lösung: Tool-Implementierung in `handle_tool_call()` hinzufügen

**Problem:** Frontend zeigt neue Tools nicht
- Lösung: NODE_CATALOG in WorkflowPro.tsx erweitern

---

**Status:** Bereit zum Testen! 🚀
