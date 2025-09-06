# Refactoring Plan: Dynamic Trust System

**Datum:** 26. August 2025

## 1. Problembeschreibung

Die "Trust Analysis"-Anzeige im Frontend ist bei einem statischen Wert von ~64% eingefroren. Die Ursache ist, dass die Frontend-Komponente (`frontend/src/pages/ProUnifiedQuery.tsx`) die Vertrauens-Metriken mit hartcodierten Platzhalterwerten berechnet, anstatt sie dynamisch vom Backend zu beziehen.

## 2. Ziel

Das Vertrauens-System soll vollständig dynamisch und Backend-gesteuert werden. Das Frontend soll eine vom Backend berechnete, realistische Vertrauensanalyse für jede Anfrage anzeigen.

## 3. High-Level Plan

Das Refactoring wird in zwei Hauptphasen durchgeführt:

*   **Phase 1: Backend-Erweiterung:** Der API-Server wird so erweitert, dass er eine echte Vertrauensanalyse durchführt und ein strukturiertes `TrustComponents`-Objekt an das Frontend zurückgibt.
*   **Phase 2: Frontend-Anpassung:** Die Frontend-Komponente wird so umgebaut, dass sie das dynamische `TrustComponents`-Objekt vom Backend empfängt und die Platzhalterlogik entfernt wird.

## 4. Detaillierter Implementierungsplan

### Sicherheitsvorkehrung: Backups

Vor der Bearbeitung **jeder** Datei wird eine direkte Kopie mit der Endung `.bak` erstellt, um ein sofortiges Rollback zu ermöglichen.

### Phase 1: Backend-Erweiterung (`hexagonal_api_enhanced_clean.py`)

1.  **Backup erstellen:** Kopiere `hexagonal_api_enhanced_clean.py` nach `hexagonal_api_enhanced_clean.py.bak_trust_refactor`.
2.  **Endpoint anpassen:** Die Funktion, die den `/api/llm/get-explanation`-Endpoint bedient, wird modifiziert.
3.  **Logik implementieren:** Eine neue private Methode `_calculate_trust_components(llm_response, facts)` wird erstellt. Diese Methode wird Heuristiken zur Berechnung der Vertrauenswerte verwenden:
    *   `factualAccuracy`: Verhältnis der Anzahl gefundener Fakten zur Länge der generierten Antwort.
    *   `sourceQuality`: Wird vorerst auf Basis der Anzahl der Quellen berechnet.
    *   `consensus`: Wird vorerst auf einen statischen Wert gesetzt (z.B. 0.7), als Platzhalter für eine zukünftige Multi-LLM-Prüfung.
    *   `ethicalAlignment`: Wird ebenfalls vorerst statisch gesetzt.
4.  **Rückgabewert erweitern:** Der JSON-Rückgabewert des Endpoints wird um das `trustComponents`-Objekt erweitert.

### Phase 2: Frontend-Anpassung (`frontend/src/pages/ProUnifiedQuery.tsx`)

1.  **Backup erstellen:** Kopiere `ProUnifiedQuery.tsx` nach `ProUnifiedQuery.tsx.bak_trust_refactor`.
2.  **State-Management anpassen:** Die `handleSubmit`-Funktion wird angepasst.
3.  **Platzhalter entfernen:** Die manuelle Erstellung des `trustComponents`-Objekts im Frontend wird vollständig entfernt.
4.  **Daten-Extraktion:** Das `trustComponents`-Objekt wird aus der Antwort des `/api/llm/get-explanation`-API-Aufrufs extrahiert.
5.  **State aktualisieren:** Das aus dem Backend empfangene `trustComponents`-Objekt wird im React-State (`results`) gespeichert und an die `TrustScoreCard`-Komponente übergeben.

## 5. Verifizierung

Nach Abschluss beider Phasen wird eine Test-Anfrage im Frontend ausgeführt. Es wird erwartet, dass die "Trust Analysis"-Anzeige einen dynamischen Wert anzeigt, der sich je nach Anfrage und Antwort ändert.
