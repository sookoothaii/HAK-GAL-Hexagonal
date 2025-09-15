---
title: "MCP Tools Inventory — Port 3006"
created: "2025-09-15T09:05:00Z"
author: "GPT-5 Thinking"
topics: ["meta"]
tags: ["tools","inventory","port-3006","mcp"]
privacy: "internal"
summary_200: |
  Inventar-Datei für alle registrierten/aktivierten Tools des MCP-Servers
  auf Port 3006. Dient als Single Source of Truth für Tool-Mapping und
  spätere Automatisierung. Wird bei Bedarf automatisiert aktualisiert.
---

# MCP Tools Inventory — Port **3006**

> Quelle: Laufende MCP-Instanz (Port 3006). Dieses Dokument erfasst die aktuell
> verfügbaren Tools (Name, Kurzbeschreibung, Kategorie).  
> Gesamtzahl über beide Server lt. Validierung: **119** Tools (Ports 3006/3007).

## Status

- **Server-Port:** 3006  
- **Inventar-Quelle:** Laufzeitserver / Logauswertung (geplant)  
- **Letzte Aktualisierung:** _init_ (wird automatisiert ergänzt)  

---

## Tool-Liste (wird befüllt)

> Platzhalter — diese Sektion wird bei der nächsten Synchronisation mit dem
> Laufzeitserver aktualisiert.

- _Noch keine Items erfasst_

---

## Geplante Automatisierung (Kurznotiz)

- Exporte und Diffs gegenüber Port 3007
- Regelmäßige Validierung (Namenskonflikte, Duplikate, verwaiste Tools)
- Ableitung: **TOOLS_3007.md** und **TOOLS_DIFF_3006_3007.md**

---

## Hinweise

- Diese Datei ist Teil des Compliance- und Transparenz-Stacks für Tooling.
- Änderungen an Toolnamen/-beschreibungen bitte atomar dokumentieren.