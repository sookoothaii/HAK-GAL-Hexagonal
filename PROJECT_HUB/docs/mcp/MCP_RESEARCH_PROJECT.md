# HAK_GAL MCP Integration - Forschungsprojekt

## Problem Statement
Claude Desktop MCP-Integration lädt nicht trotz korrekter Konfiguration und laufendem Backend.

## Hypothesen

### H1: JSON-RPC Protocol Mismatch
- Claude erwartet spezifisches JSON-RPC Format
- Server sendet falsches Format oder Timing

### H2: Process Spawn Issue  
- Windows-spezifisches Problem mit Python-Subprocess
- Path-Escaping oder Encoding-Probleme

### H3: Authentication/Security Block
- Claude blockiert lokale Server aus Sicherheitsgründen
- Fehlende Signatur oder Manifest

### H4: Version Incompatibility
- Claude Version unterstützt kein MCP
- MCP Protocol Version mismatch

## Experimente

### Experiment 1: Minimal Echo Server
```python
# mcp_minimal.py
import sys, json
while True:
    line = sys.stdin.readline()
    if line.strip():
        req = json.loads(line)
        if req.get("method") == "initialize":
            sys.stdout.write(json.dumps({
                "jsonrpc": "2.0",
                "id": req["id"],
                "result": {"capabilities": {"tools": {}}}
            }) + "\n")
            sys.stdout.flush()
```

**Config:**
```json
{
  "mcpServers": {
    "test": {
      "command": ["python", "mcp_minimal.py"]
    }
  }
}
```

### Experiment 2: Node.js Wrapper
```javascript
// mcp_wrapper.js
const { spawn } = require('child_process');
const python = spawn('python', ['hak_gal_mcp.py']);

python.stdout.on('data', (data) => {
  process.stdout.write(data);
});

process.stdin.on('data', (data) => {
  python.stdin.write(data);
});
```

### Experiment 3: Named Pipe Communication
```python
# mcp_pipe.py
import win32pipe, win32file
pipe_name = r'\\.\pipe\hak_gal_mcp'
pipe = win32pipe.CreateNamedPipe(
    pipe_name,
    win32pipe.PIPE_ACCESS_DUPLEX,
    win32pipe.PIPE_TYPE_MESSAGE,
    1, 65536, 65536, 0, None
)
```

### Experiment 4: Registry/Manifest Approach
```xml
<!-- hak_gal.manifest -->
<?xml version="1.0" encoding="UTF-8"?>
<manifest>
  <mcp-server>
    <name>HAK_GAL</name>
    <version>1.0.0</version>
    <executable>python</executable>
    <args>-m hak_gal_mcp</args>
  </mcp-server>
</manifest>
```

### Experiment 5: Direct HTTP Bridge
```python
# mcp_http_bridge.py
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/mcp', methods=['POST'])
def mcp_bridge():
    # Forward to actual MCP server
    result = subprocess.run(
        ['python', 'hak_gal_mcp.py'],
        input=request.json,
        capture_output=True
    )
    return jsonify(result.stdout)

app.run(port=5002)
```

## Debugging-Strategie

### 1. Process Monitor
- Tool: ProcMon von Sysinternals
- Filter: Process Name contains "Claude"
- Suche nach: CreateProcess Events für Python

### 2. Pipe Sniffing
```powershell
# PowerShell pipe monitor
Get-WmiObject Win32_PipeFile | Where {$_.Name -like "*mcp*"}
```

### 3. Claude Internal Logs
```javascript
// In Claude DevTools Console
console.log(window.__MCP_SERVERS);
console.log(window.__MCP_DEBUG);
```

### 4. Python Trace
```python
import sys
import functools

def trace_calls(frame, event, arg):
    if event == 'call':
        print(f"TRACE: {frame.f_code.co_filename}:{frame.f_lineno}")
    return trace_calls

sys.settrace(trace_calls)
```

## Alternative Architekturen

### A. WebSocket-Based MCP
```python
import websocket
import asyncio

class WebSocketMCP:
    def __init__(self):
        self.ws = websocket.WebSocketApp(
            "ws://localhost:5003/mcp",
            on_message=self.on_message
        )
```

### B. gRPC Integration
```proto
service HAKGALMCP {
  rpc Initialize(InitRequest) returns (InitResponse);
  rpc CallTool(ToolRequest) returns (ToolResponse);
}
```

### C. COM Object (Windows)
```python
import win32com.client

class HAKGALCOM:
    _reg_clsid_ = "{12345678-1234-5678-1234-567812345678}"
    _reg_progid_ = "HAKGAL.MCP"
```

## Nächste Schritte

1. **Test mit `mcp_debug_advanced.py`:**
   ```bash
   cd "D:\MCP Mods\HAK_GAL_HEXAGONAL"
   python mcp_debug_advanced.py
   ```

2. **Alternative Config testen:**
   - Kopiere eine Config aus `claude_config_alternatives.json`
   - Paste in `%APPDATA%\Claude\claude_desktop_config.json`
   - Claude neu starten

3. **Server manuell testen:**
   ```bash
   python hak_gal_mcp_fixed.py
   # In anderem Terminal:
   echo '{"jsonrpc":"2.0","method":"initialize","id":1}' | python hak_gal_mcp_fixed.py
   ```

4. **Process Monitor:**
   - Download ProcMon
   - Filter: ProcessName contains "Claude" OR "python"
   - Start Claude
   - Analysiere CreateProcess Events

## Erfolgskriterien

✅ Claude zeigt "MCP Tools available" in der UI
✅ Tool-Aufruf liefert Ergebnisse aus HAK_GAL KB
✅ Keine Errors in Claude Logs
✅ Server bleibt stabil über mehrere Requests

## Fallback-Plan

Falls MCP nicht funktioniert:

1. **HTTP API Bridge:**
   - HAK_GAL läuft auf Port 5001
   - Browser Extension als Bridge
   - Claude → Extension → HAK_GAL

2. **File Watcher:**
   - Claude schreibt Requests in File
   - HAK_GAL watched und antwortet
   - Results in separatem File

3. **Clipboard Integration:**
   - AutoHotkey Script
   - Intercepted Claude-Commands
   - Direct HAK_GAL Execution

## Dokumentation

Alle Experimente und Ergebnisse werden dokumentiert in:
- `mcp_experiments.log`
- `mcp_server.log` 
- Screenshots in `debug_screenshots/`

---

**Status:** Aktive Forschung
**Priorität:** Hoch (als Lernprojekt)
**Zeitrahmen:** Iterativ, kein fixer Deadline
