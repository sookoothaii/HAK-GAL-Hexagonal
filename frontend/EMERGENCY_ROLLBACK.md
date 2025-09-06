# 🚨 NOTFALL ROLLBACK ANLEITUNG

## Falls etwas schief geht - SO MACHEN SIE ES RÜCKGÄNGIG:

### Option 1: PowerShell (Windows) - EMPFOHLEN
```powershell
cd "D:\MCP Mods\HAK_GAL_HEXAGONAL\frontend"
.\backup_manager.ps1 rollback
```
Wählen Sie dann das neueste Backup aus der Liste.

### Option 2: Manueller Rollback
1. Stoppen Sie das Frontend (Ctrl+C)
2. Navigieren Sie zu: `D:\MCP Mods\HAK_GAL_HEXAGONAL\frontend_backups\`
3. Finden Sie den neuesten `backup_[timestamp]` Ordner
4. Kopieren Sie den Inhalt zurück ins Frontend:
   - Löschen Sie: `frontend\src`
   - Kopieren Sie: `backup_[timestamp]\src` → `frontend\src`
   - Kopieren Sie alle `.json` und `.ts` Dateien zurück

### Option 3: Git Rollback
```bash
cd "D:\MCP Mods\HAK_GAL_HEXAGONAL"
git log --oneline | grep "BACKUP:"
git checkout frontend-backup-[timestamp]
```

### Nach dem Rollback:
1. `cd frontend`
2. `npm install` (falls package.json geändert wurde)
3. `npm run dev`

## 📞 Support-Informationen
- Alle Änderungen sind in `CHANGELOG_IMPROVEMENTS.md` dokumentiert
- Original-Dateien sind in `frontend_backups/` gesichert
- Keine Daten gehen verloren - alles ist gesichert!

## ✅ Zeichen dass alles funktioniert:
- Frontend startet ohne Fehler
- WebSocket verbindet sich (siehe Console)
- Dashboard zeigt Daten an
- Keine roten Fehler in der Browser-Console
