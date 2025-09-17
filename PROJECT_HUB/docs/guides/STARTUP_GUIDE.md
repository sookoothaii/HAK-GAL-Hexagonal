---
title: "Startup Guide"
created: "2025-09-15T00:08:01.022300Z"
author: "system-cleanup"
topics: ["guides"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# 🚀 HAK-GAL HEXAGONAL - STARTUP GUIDE
**Stand: 21. August 2025**

## ✅ EMPFOHLENER START

### Verwenden Sie diesen Launcher:
```batch
.\START_FINAL.bat
```

Dies ist der **finale, optimierte Launcher** mit allen Fixes!

---

## 📋 SCHRITT-FÜR-SCHRITT ANLEITUNG

### 1. System komplett stoppen
- Schließen Sie ALLE Terminal-Fenster (Backend, Proxy, Frontend)
- Warten Sie 3 Sekunden

### 2. System Check (Optional)
```batch
.\CHECK_SYSTEM.bat
```
Zeigt ob alles richtig konfiguriert ist.

### 3. System starten
```batch
.\START_FINAL.bat
```

### 4. Warten auf Startmeldungen
- "✅ SYSTEM FULLY OPERATIONAL!"
- Browser öffnet sich automatisch

### 5. Frontend separat (falls nötig)
Falls das Frontend nicht läuft, in einem neuen Terminal:
```batch
cd frontend
npm run dev
```

---

## 🎯 WAS FUNKTIONIERT

| Feature | Status | Performance |
|---------|--------|-------------|
| WebSocket | ✅ | Real-time |
| HRM Neural | ✅ | <10ms |
| KB Search | ✅ | ~30ms |
| LLM Gemini | ✅ | ~7s |
| LLM DeepSeek | ✅ | ~30s (fallback) |
| Database Write | ✅ | Mit API Key |
| Governor | ✅ | Ready |

---

## 🔧 TROUBLESHOOTING

### Problem: 403 Forbidden beim Fakten hinzufügen
**Lösung:**
1. Frontend neu starten (Ctrl+C → npm run dev)
2. Browser-Cache leeren (Ctrl+Shift+R)

### Problem: LLM braucht 30s statt 7s
**Lösung:**
1. `ULTIMATE_GEMINI_FIX.bat` ausführen
2. System neu starten

### Problem: "FORCING DeepSeek" in Console
**Lösung:**
1. Backend beenden
2. `complete_gemini_fix.py` ausführen
3. Mit `START_FINAL.bat` neu starten

---

## 📁 WICHTIGE LAUNCHER

| Datei | Zweck |
|-------|-------|
| `START_FINAL.bat` | **✅ HAUPTLAUNCHER** - Alle Fixes, optimiert |
| `ULTIMATE_GEMINI_FIX.bat` | Repariert Gemini-Integration |
| `FIX_DATABASE_403.bat` | Repariert Datenbank-Schreibrechte |
| `CHECK_SYSTEM.bat` | Überprüft Konfiguration |

---

## 🔑 API KEYS

- **Gemini:** <YOUR_GOOGLE_API_KEY_HERE>
- **DeepSeek:** sk-${HAKGAL_AUTH_TOKEN}  
- **HAK-GAL:** hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d

---

## ✅ ZUSAMMENFASSUNG

**Verwenden Sie `START_FINAL.bat` - das ist der beste Launcher!**

Er enthält:
- Alle Gemini-Fixes (7s Antworten)
- Alle API-Keys korrekt gesetzt
- Database Write Access
- WebSocket Support
- Alle Optimierungen