DB Maintenance Guide (ASCII)

Scope
- T?gliches Online-Backup der SQLite-SSoT (WAL-Modus).
- W?chentliches VACUUM.
- Rotation: behalte die letzten 10 Backups.

Pfadkonstanten (anpassen bei Bedarf)
- Python venv: D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe
- CLI: D:\MCP Mods\HAK_GAL_HEXAGONAL\ultimate_mcp\db_maintenance.py
- Backups: D:\MCP Mods\HAK_GAL_HEXAGONAL\backups

Manuelle Ausf?hrung
- Backup jetzt:  
  powershell -NoProfile -Command "& 'D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe' 'D:\MCP Mods\HAK_GAL_HEXAGONAL\ultimate_mcp\db_maintenance.py' backup_now | cat"
- Rotation:  
  powershell -NoProfile -Command "& 'D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe' 'D:\MCP Mods\HAK_GAL_HEXAGONAL\ultimate_mcp\db_maintenance.py' rotate --keep-last 10 | cat"
- VACUUM:  
  powershell -NoProfile -Command "& 'D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe' 'D:\MCP Mods\HAK_GAL_HEXAGONAL\ultimate_mcp\db_maintenance.py' vacuum | cat"

Windows Task Scheduler (schtasks)
- T?gliches Backup 03:15 Uhr:  
  schtasks /Create /TN HAKGAL_DailyBackup /TR "powershell -NoProfile -Command \"& 'D:\MCP Mods\HAK_GAL_HEXAGONAL\\.venv_hexa\\Scripts\\python.exe' 'D:\MCP Mods\HAK_GAL_HEXAGONAL\\ultimate_mcp\\db_maintenance.py' backup_now; & 'D:\MCP Mods\HAK_GAL_HEXAGONAL\\.venv_hexa\\Scripts\\python.exe' 'D:\MCP Mods\HAK_GAL_HEXAGONAL\\ultimate_mcp\\db_maintenance.py' rotate --keep-last 10\"" /SC DAILY /ST 03:15 /RL HIGHEST /F
- W?chentliches VACUUM sonntags 03:30 Uhr:  
  schtasks /Create /TN HAKGAL_WeeklyVacuum /TR "powershell -NoProfile -Command \"& 'D:\MCP Mods\HAK_GAL_HEXAGONAL\\.venv_hexa\\Scripts\\python.exe' 'D:\MCP Mods\HAK_GAL_HEXAGONAL\\ultimate_mcp\\db_maintenance.py' vacuum\"" /SC WEEKLY /D SUN /ST 03:30 /RL HIGHEST /F

Verifikation
- Health-JSON pr?fen:  
  python - << PY
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path('D:/MCP Mods/HAK_GAL_HEXAGONAL/ultimate_mcp').resolve().parents[0]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer
async def main():
    s=HAKGALMCPServer(); out=[]
    async def cap(r): out.append(r)
    s.send_response=cap
    await s.handle_initialize({"id":1})
    await s.handle_tool_call({"id":2,"params":{"name":"health_check_json","arguments":{}}})
    for r in out:
        if r.get("id")==2:
            print((r.get("result") or {}).get("content")[0].get("text"))
asyncio.run(main())
PY

Hinweis
- Alle Ausgaben sind ASCII-sicher; PRAGMAs werden pro Verbindung erzwungen.
- Bei Modell?nderungen (Ports, Pfade) die obigen Befehle konsistent anpassen.
