### Frontend Fix Snapshot — React/Vite Fehler behoben

Zeitpunkt: 2025-08-14 13:15

---

### Symptome
- Build/Runtime-Fehler in Vite/React:
  - JSX: „Expected corresponding JSX closing tag for <FixedSizeList>“
  - Hooks: „Invalid hook call … useState … ThemeProvider“ (mehrmals im Log)
  - Dashboard: „apiService.reason is not a function“

---

### Ursachen
- `ProKnowledgeList.tsx`:
  - Falsches Prop: `overScanCount` statt `overscanCount`
  - Selbstschließendes `<FixedSizeList />` statt korrekt geschlossenem `</FixedSizeList>`
- `ProDashboard.tsx`:
  - `apiService` (Klasse) wie eine Instanz genutzt → `reason` nicht gefunden
- Die Hook-Warnung im `ThemeProvider` war ein Folgefehler durch obige Render-Abbrüche (kein echter Mehrfach-React-Bug).

---

### Edits
- Datei: `frontend/src/pages/ProKnowledgeList.tsx`
  - `overScanCount` → `overscanCount`
  - `<FixedSizeList … />` → Öffnendes/Schließendes Tag-Paar mit Render-Callback korrekt gekapselt
- Datei: `frontend/src/pages/ProDashboard.tsx`
  - Import: `ApiService` (Klasse) + `API_BASE_URL`
  - Instanzierung: `const api = useMemo(() => new ApiService(API_BASE_URL), [])`
  - Nutzung: `api.reason("test")`

---

### Ergebnis
- Frontend startet wieder; keine JSX/Hook-Laufzeitfehler mehr
- WebSocket verbindet: „✅ WebSocket connected to HAK-GAL Backend“
- Dashboard lädt; HRM-Check via `api.reason` funktioniert (mit Fallback auf „operational false“ bei Fehlern)

---

### Hinweise
- Bei React-Hook-Warnungen zuerst Render-Fehler im Baum beheben (JSX/Props), oft verschwinden die Hook-Warnungen im Anschluss.
- Services als Klassen/Singletons konsistent verwenden (Instanz vs. Default-Export beachten).


