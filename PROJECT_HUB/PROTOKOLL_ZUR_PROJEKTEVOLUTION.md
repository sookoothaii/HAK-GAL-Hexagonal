# Protokoll zur Projektevolution der HAK/GAL Suite

**Dokument-ID:** HAKGAL-EVO-20250822
**Zweck:** Klarstellung und strategischer Leitfaden für alle nachfolgenden Instanzen.
**Verfassungskonformität:** Dieses Dokument wurde gemäß der HAK/GAL Verfassung erstellt, um Mehrdeutigkeit zu eliminieren und eine faktenbasierte Interpretation der Projekthistorie zu gewährleisten.

---

## 1. Einleitung: Zweck dieses Protokolls

Der `PROJECT_HUB` der HAK/GAL Suite ist ein Archiv extrem schneller, nicht-linearer Entwicklung. Er enthält eine hohe Dichte an technischen Berichten, Snapshots und strategischen Plänen. Dies kann für eine neu initialisierte Instanz zu Verwirrung führen.

Dieses Protokoll dient dazu, dieses Konvolut an Informationen in geordnete Bahnen zu lenken. Es unterscheidet klar zwischen:

1.  **Der Kanonischen Entwicklungslinie:** Der tatsächlich umgesetzte und heute gültige Entwicklungspfad des Systems.
2.  **Strategischen Explorationen:** Wertvolle, aber bewusst zurückgestellte Zukunftspläne, die als Ressource für zukünftige Skalierungsphasen dienen.

---

## 2. Die Kanonische Entwicklungslinie (Der tatsächlich umgesetzte Pfad)

Die heute stabile und performante Systemarchitektur ist das Ergebnis eines iterativen Prozesses der Konsolidierung und Optimierung.

*   **Phase I (ca. 14. - 18. August): Konsolidierung & Stabilisierung**
    *   **Ausgangslage:** Ein experimentelles Zwei-Backend-System (Port 5001 für die stabile API, Port 5002 für "Mojo"-Performance-Tests).
    *   **Entscheidung:** Die Zwei-Backend-Strategie wurde zugunsten eines einzigen, einheitlichen Backends aufgegeben.
    *   **Ergebnis:** Das System wurde auf **Port 5002** konsolidiert. Ein **Caddy-Proxy auf Port 8088** wurde als alleiniger Eingangspunkt für das Frontend etabliert. In dieser Phase wurde ein kritischer "Read-Only"-Bug behoben, um dem Backend vollen Schreibzugriff auf die **SQLite-Datenbank** zu gewähren.

*   **Phase II (ca. 18. - 22. August): Integration & Finale Optimierung**
    *   **Ausgangslage:** Ein stabiles, aber noch fehlerbehaftetes Backend.
    *   **Entscheidung:** Fokus auf die vollständige Integration der Kern-Intelligenz und Behebung der letzten Performance-Blocker.
    *   **Ergebnis:** Die Kernkomponenten (HRM, LLM-Provider) wurden erfolgreich integriert. Zwei kritische Fehler wurden behoben: Eine fehlende API-Route (`/api/hrm/feedback-stats`) wurde hinzugefügt und ein Latenzproblem im `/api/status`-Endpunkt wurde durch Optimierung um den Faktor 542x gelöst.

*   **Aktueller Kanonischer Zustand:**
    *   Das System ist **stabil, performant und voll funktionsfähig**.
    *   Die Architektur basiert auf einem **monolithischen (aber hexagonal strukturierten) Backend**, das eine **SQLite-Datenbank** verwendet.
    *   Die maßgebliche und allein gültige Beschreibung des aktuellen Zustands befindet sich in der **`GEMINI.md`** im Hauptverzeichnis.

---

## 3. Strategische Exploration: Der "HAK-GAL 2.0" Masterplan

Im Projekt-Hub existiert das Dokument `MIGRATION_MASTERPLAN_HAKGAL_20_20250816.md`. Es ist entscheidend, dieses Dokument korrekt einzuordnen.

*   **Kontext:** Bei diesem Masterplan handelt es sich um eine **strategische Exploration**, nicht um einen verworfenen oder gescheiterten Plan. Er wurde erstellt, um den Weg zu massiver, Enterprise-tauglicher Skalierung zu durchdenken.

*   **Untersuchte Technologien:** Der Plan skizziert den Übergang zu einer Microservice-Architektur mit Technologien wie:
    *   **Datenbank:** Neo4j GraphDB
    *   **Vector-Suche:** Qdrant
    *   **Orchestrierung:** Kubernetes & Istio Service Mesh
    *   **Daten-Pipelines:** Apache Kafka & Spark
    *   **LLM:** Lokale 7B-Parameter-Modelle

*   **Status & Zukünftiger Wert:**
    *   Dieser Pfad wurde **bewusst und strategisch zurückgestellt**. Die Entscheidung war, zuerst die aktuelle Architektur zur Perfektion zu bringen, anstatt verfrüht die Komplexität zu erhöhen.
    *   **Dieser Plan ist nicht wertlos – er ist eine unschätzbar wertvolle Ressource.** Er ist ein durchdachtes Blaupausen-Archiv für die Zukunft. Sobald die HAK/GAL Suite an die Skalierungsgrenzen ihrer aktuellen Architektur stößt, bietet dieser Masterplan einen fundierten und detailliert ausgearbeiteten Vorschlag für die nächste große Evolutionsstufe.

---

## 4. Handlungsanweisung für Zukünftige Instanzen

1.  **Beginne immer mit `GEMINI.md`:** Diese Datei im Projekt-Hauptverzeichnis enthält die kanonische, aktuelle und allein gültige Wahrheit über den Systemzustand und dessen Architektur.

2.  **Nutze dieses Protokoll zur Orientierung:** Dieses Dokument (`PROTOKOLL_ZUR_PROJEKTEVOLUTION.md`) dient dir als Landkarte, um die Vielzahl an historischen Dokumenten im `PROJECT_HUB` korrekt zu interpretieren.

3.  **Interpretiere Dokumente im historischen Kontext:** Ein Dokument vom 16. August beschreibt eine andere Realität als eines vom 22. August. Prüfe immer das Datum und ordne das Dokument mithilfe dieses Protokolls in die korrekte Phase der Entwicklung ein.

4.  **Behandle strategische Explorationen als das, was sie sind:** Der "HAK-GAL 2.0 Masterplan" ist kein Fehlschlag, sondern eine wertvolle Zukunftsoption. Er sollte nicht als Anweisung für die Gegenwart, sondern als Inspiration für die Zukunft gelesen werden.
