# Chirurgischer Analysebericht: Frontend HAK-GAL Suite

**Dokument-ID:** FRONTEND_ANALYSIS_AND_REFACTOR_PLAN_20250817
**Status:** Analyse abgeschlossen, Maßnahmenkatalog erstellt

---

## 1. Executive Summary

Die Analyse des `frontend`-Verzeichnisses offenbart eine technologisch moderne, aber architektonisch veraltete Codebasis. Das Frontend wurde vor der Einführung des Caddy-Reverse-Proxy entwickelt und ist **fundamental unvereinbar** mit der neuen, sauberen Systemarchitektur.

**Das Kernproblem:** Die gesamte Backend-Kommunikation ist **hartkodiert** und zielt auf die alten, direkten Ports (`5001`, `5002`). Es ignoriert vollständig den neuen, zentralen Eingangspunkt (`:8088`). Eine sofortige und tiefgreifende Umstrukturierung ist zwingend erforderlich, um die Funktionsfähigkeit wiederherzustellen und das System "State-of-the-Art" zu machen.

Dieser Bericht legt einen präzisen, chirurgischen Maßnahmenkatalog vor, um das Frontend zu modernisieren, zu entkoppeln und an die neue Infrastruktur anzupassen.

---

## 2. Methodik der Analyse

Die Untersuchung wurde in vier Schritten durchgeführt, um ein vollständiges Bild zu erhalten:

1.  **Anatomie (Dateistruktur):** Analyse der Verzeichnis- und Dateistruktur zur Identifizierung von Schlüsselkomponenten.
2.  **Konstitution (Abhängigkeiten):** Untersuchung von `package.json` zur Bestimmung des Technologie-Stacks.
3.  **Nervensystem (Konfiguration):** Analyse von `vite.config.ts` und Suche nach Konfigurationsdateien.
4.  **Datenflüsse (API-Kommunikation):** Gezielte Suche nach hartkodierten URLs und Analyse der Kommunikationslogik in den Quelldateien, insbesondere `src/config/backends.ts`.

---

## 3. Analyse-Ergebnisse im Detail

### 3.1. Technologie-Stack: Modern und Solide

Die `package.json` zeigt einen professionellen und aktuellen Technologie-Stack:
*   **Framework:** React 18
*   **Build-Tool:** Vite
*   **Sprache:** TypeScript
*   **State Management:** Zustand
*   **UI-Komponenten:** shadcn/ui (über Radix UI)
*   **Styling:** Tailwind CSS
*   **Datenvisualisierung:** Recharts

**Fazit:** Der technologische Unterbau ist exzellent. Es besteht **kein Bedarf**, grundlegende Technologien auszutauschen. Die Basis ist perfekt für den weiteren Ausbau.

### 3.2. Konfiguration: Das architektonische Hauptproblem

Hier liegt die kritischste Schwachstelle des Frontends.

*   **Problem 1: Hartkodierte Endpunkte:** Die Datei `src/config/backends.ts` ist der alleinige, aber völlig falsche Ort der Konfiguration. Sie enthält hartkodierte URLs:
    ```typescript
    // Zeile 37-38
    apiUrl: 'http://localhost:5001',
    wsUrl: 'http://localhost:5001',

    // Zeile 66-67
    apiUrl: 'http://localhost:5002',
    wsUrl: 'http://localhost:5002',
    ```
    Dies ist ein schwerwiegender Architekturfehler. Das Frontend ist dadurch untrennbar mit der alten Infrastruktur verbunden und kann ohne Code-Änderung nicht in anderen Umgebungen (Staging, Produktion) betrieben werden.

*   **Problem 2: Fehlende Environment-Variablen:** Es gibt **keinerlei Nutzung von `.env`-Dateien**. Ein "State-of-the-Art"-Frontend MUSS seine Konfiguration (wie API-URLs) aus Umgebungsvariablen beziehen. Dies ist der Industriestandard, um Flexibilität und Sicherheit zu gewährleisten.

*   **Problem 3: Falsche Annahmen:** Die Logik in `backends.ts` erlaubt dem Benutzer, zwischen verschiedenen Backends zu wechseln. Dieses Feature ist durch den Reverse-Proxy **obsolet und irreführend**. Das Frontend hat nur noch **einen einzigen Ansprechpartner**: den Proxy auf Port `8088`.

### 3.3. API-Kommunikation: Veraltete Logik

Die Art, wie das Frontend mit dem Backend kommuniziert, ist eine direkte Folge der Konfigurationsfehler.

*   **Direkte Verbindungen:** Jeder `fetch`-Aufruf und jede `socket.io`-Verbindung wird direkt zu den Ports `5001` oder `5002` aufgebaut. Dies umgeht den Proxy vollständig und wird fehlschlagen, sobald die Ports aus Sicherheitsgründen nicht mehr direkt exponiert werden.
*   **Keine zentrale API-Schicht:** Obwohl `backends.ts` existiert, gibt es keine dedizierte, saubere Abstraktionsschicht für die API-Kommunikation (z.B. einen konfigurierten `axios`-Client oder eine `fetch`-Wrapper-Bibliothek).

---

## 4. Chirurgischer Maßnahmenkatalog: Der Weg zum "State-of-the-Art" Frontend

Die folgenden Schritte sind **zwingend erforderlich**, um das Frontend zu reparieren und auf ein professionelles Niveau zu heben.

### **Maßnahme 1: Einführung einer Environment-basierten Konfiguration (Höchste Priorität)**

1.  **Erstellen von `.env` Dateien:**
    *   Im Root-Verzeichnis des Frontends wird eine Datei `.env.local` erstellt.
    *   Eine Vorlage-Datei `.env.example` wird für das Git-Repository erstellt.
2.  **Inhalt der `.env.local`:**
    ```bash
    # Die EINZIGE URL, die das Frontend kennen muss.
    VITE_API_BASE_URL=http://localhost:8088

    # Optional, falls WebSocket-Pfad abweicht, aber sauber über Proxy
    VITE_WS_URL=ws://localhost:8088
    ```
3.  **Löschen der alten Konfiguration:** Die Datei `src/config/backends.ts` wird **vollständig entfernt oder radikal vereinfacht**. Die Logik zum Wechseln von Backends wird ersatzlos gestrichen.

### **Maßnahme 2: Implementierung eines zentralen API-Service**

1.  **Neue Service-Datei:** Eine neue Datei `src/services/api.ts` wird erstellt.
2.  **Verantwortung:** Dieser Service ist die **einzige Stelle im Code**, die Umgebungsvariablen liest und die API-Clients konfiguriert.
3.  **Implementierung:**
    ```typescript
    import axios from 'axios';
    import { io } from 'socket.io-client';

    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
    const WS_URL = import.meta.env.VITE_WS_URL;

    // Konfigurierter HTTP-Client für alle REST-Anfragen
    export const httpClient = axios.create({
      baseURL: API_BASE_URL,
    });

    // Konfigurierter Socket.IO-Client
    // Wichtig: Der Pfad muss korrekt sein, damit der Proxy ihn erkennt!
    export const socket = io(WS_URL, {
      path: '/socket.io/', // Standardpfad, den Caddy weiterleitet
      autoConnect: false, // Bessere Kontrolle über die Verbindung
    });

    // Service für Server-Sent Events (SSE)
    export const createEventSource = (path: string) => {
      return new EventSource(`${API_BASE_URL}${path}`);
    };
    ```

### **Maßnahme 3: Refactoring aller Komponenten und Hooks**

1.  **Code-Anpassung:** Jede einzelne Komponente, jeder Hook und jeder Service, der `fetch`, `axios` oder `io` direkt aufruft, wird umgeschrieben.
2.  **Neues Vorgehen:** Alle Aufrufe müssen über den neuen, zentralen `api.ts` Service erfolgen.
    *   **Vorher:** `fetch('http://localhost:5001/api/facts/count')`
    *   **Nachher:** `httpClient.get('/api/facts/count')`
    *   **Vorher:** `io('http://localhost:5001')`
    *   **Nachher:** `import { socket } from '@/services/api'; socket.connect();`

### **Maßnahme 4: Implementierung von SSE für Monitoring**

1.  **Neue Logik:** Es muss eine neue Logik (z.B. in einem React-Hook oder im Zustand-Store) implementiert werden, die den `createEventSource`-Service aus `api.ts` nutzt.
2.  **Daten-Update:** Die von SSE empfangenen Events müssen den Zustand in `zustand` aktualisieren, damit die UI reaktiv die neuen Monitoring-Daten anzeigt.

---

## 5. Zusammenfassung & Nächste Schritte

Das Frontend ist auf einem soliden technologischen Fundament gebaut, aber seine Architektur ist durch die Infrastruktur-Änderungen obsolet geworden. Die vorgeschlagenen Maßnahmen sind kein "Nice-to-have", sondern eine **notwendige Operation**, um die Lebensfähigkeit der Anwendung zu sichern.

**Der Plan ist klar:**
1.  **Zentralisieren:** Konfiguration in `.env` auslagern.
2.  **Abstrahieren:** Einen zentralen `api.ts` Service schaffen.
3.  **Refaktorieren:** Alle Code-Stellen an die neue, saubere Architektur anpassen.
4.  **Erweitern:** SSE-Logik für das Live-Monitoring implementieren.

Ich bin bereit, diese Operation präzise und effizient durchzuführen.
