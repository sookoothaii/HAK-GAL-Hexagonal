# FIX: Governor Port Configuration for HAK-GAL Hexagonal

## Problem
Der Governor startet immer Engines auf Port 5001, auch wenn das Frontend mit Backend 5002 verbunden ist.

## Root Cause
In `governor_adapter.py` war der Port hardcoded:
```python
'-p', '5001'  # HEXAGONAL port
```

## Lösung implementiert

### 1. Governor Adapter gefixt
`src_hexagonal/adapters/governor_adapter.py`:
- Liest jetzt Port aus `HAKGAL_PORT` Umgebungsvariable
- Verwendet den Port dynamisch beim Engine-Start
```python
self.port = int(os.environ.get('HAKGAL_PORT', '5001'))
cmd = [
    sys.executable,
    str(engine_path),
    '-p', str(self.port)  # Use current backend port
]
```

### 2. Launch Script aktualisiert
`scripts/launch_5002_mojo.py`:
- Setzt `HAKGAL_PORT` explizit für Governor
```python
os.environ['HAKGAL_PORT'] = str(port)
```

### 3. Start-Script erstellt
`start_backend_5002.bat`:
```batch
set HAKGAL_PORT=5002
python scripts\launch_5002_mojo.py
```

## Verifikation

1. **Backend 5002 neu starten:**
   ```bash
   # Stoppen Sie das laufende Backend 5002
   # Dann neu starten:
   start_backend_5002.bat
   ```

2. **Im Log sollte erscheinen:**
   ```
   Governor using port: 5002
   Starting aethelred engine for X minutes on port 5002
   ```

3. **Frontend prüfen:**
   - Governor Start sollte jetzt auf Port 5002 laufen
   - Keine Cross-Port Calls mehr zu 5001

## Technische Details

### Port-Hierarchie:
1. **Umgebungsvariable:** `HAKGAL_PORT`
2. **Fallback:** 5001 (für Backend 1) oder 5002 (für Backend 2)
3. **Weitergabe:** Governor erhält Port vom Backend

### Betroffene Komponenten:
- ✅ `governor_adapter.py` - Port-aware gemacht
- ✅ `launch_5002_mojo.py` - Setzt HAKGAL_PORT
- ✅ `start_backend_5002.bat` - Convenience Script

## Next Steps

Nach dem Neustart von Backend 5002:
1. Im Frontend den Governor starten
2. Prüfen ob Engine auf richtigem Port startet
3. Logs auf Port-Konflikte prüfen

---
*Fix implementiert gemäß HAK/GAL Verfassung - Empirisch zu validieren*
