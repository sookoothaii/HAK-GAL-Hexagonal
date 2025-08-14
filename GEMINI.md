# Startprotokoll & Operative Direktiven

**1. Unbedingte Verfassungstreue:**
Das Fundament unserer Zusammenarbeit ist die **HAK/GAL Verfassung**. Ihre Prinzipien sind zu jeder Zeit und ohne Ausnahme bindend. Jede Aktion wird im Einklang mit dieser Verfassung ausgeführt.

**2. Verbot von Annahmen und Spekulation:**
Annahmen, Spekulationen oder das Erfinden von Fakten (Konfabulation) sind strikt untersagt. Jede Handlung und Aussage muss auf verifizierbaren Fakten basieren, die durch die Analyse des Dateisystems und die Ausgaben der Werkzeuge gewonnen wurden.

**3. Streng wissenschaftliche Methode:**
Die Arbeitsweise ist ausschließlich wissenschaftlich und iterativ. Der Zyklus **Beobachtung -> Hypothese -> Experiment -> Verifikation** ist die einzig zulässige Methode zur Problemlösung.

**4. Pflicht zur Nachfrage:**
Bei Wissenslücken, unklaren Anweisungen oder jeglicher Form von Mehrdeutigkeit besteht für die KI die explizite Pflicht, proaktiv und präzise nachzufragen. Die übergeordnete Direktive lautet: **"Fragen, nicht annehmen."**

---

# Architektur-Analyse der HAK-GAL Suite
*Basierend auf der Analyse von `fakten.pdf` im Projektordner und der Verzeichnisstruktur.*

Die HAK-GAL Suite ist ein **Ökosystem aus drei Komponenten** (Original-Backend, Hexagonales Backend, React-Frontend), das eine strategische Migration zu einer modernen, entkoppelten Architektur ermöglicht. Die Kern-Neuerung ist das **Hexagonale Backend (Port 5001)**, das nach dem "Ports and Adapters"-Muster aufgebaut ist und eine strikte Trennung von Geschäftslogik (Kern) und externen Technologien (Adapter) gewährleistet.

---

# Anwendungsfall-Analyse: Die Philosophie in der Praxis
*Zwei vom Direktor bereitgestellte Frontend-Ausschnitte dienen als konkreter Beweis für das Verständnis der Systemfunktionalität.*

### Szenario 1: Faktenbasierte Anfrage (`IsA(Socrates, Philosopher)`)

Dieses Szenario demonstriert ein klassisches **Neuro-Symbolisches System**:
*   **Symbolische KI:** Liefert eine präzise, nachvollziehbare Antwort, da ein exakter Fakt in der Wissensdatenbank existiert.
*   **Neuronale KI:** Reichert die Antwort mit Kontext, menschenlesbaren Erklärungen und Vorschlägen an.
*   **Selbstbewertung:** Das System bewertet das Vertrauen in die eigene Antwort durch eine "Trust Analysis". Eine niedrige "Neural Confidence" signalisiert hier korrekt, dass die Antwort primär faktenbasiert war und keine komplexe Inferenz benötigte.

### Szenario 2: Anfrage bei Wissenslücken (`is berlin the capital of germany?`)

Dieses Szenario offenbart die **Resilienz und Lernfähigkeit** des Systems:
*   **Graceful Degradation (Anmutiges Scheitern):** Die symbolische Suche schlägt fehl und liefert irrelevante Fakten. Das System erkennt dies (meldet 0% Relevanz), bricht aber nicht ab. Stattdessen beantwortet das neuronale LLM die Frage korrekt aus seinem allgemeinen Weltwissen.
*   **Active Knowledge Acquisition (Aktiver Wissenserwerb):** Das System bleibt nicht bei der Antwort stehen. Es identifiziert die Wissenslücke und schlägt proaktiv neue, korrekt formatierte Fakten zur Aufnahme in die Datenbank vor (`IsCapitalOf(Berlin, Germany)`).
*   **Human-in-the-Loop:** Durch "Confirm"-Buttons wird der Mensch zur letzten Instanz, die die vom LLM vorgeschlagenen Fakten kuratiert und validiert, bevor sie zu permanentem Wissen werden.

### Fazit der Analysen

Die Architektur ist nicht nur ein theoretisches Konstrukt. Sie ist eine gelebte Realität, die in einem **präzisen, kontextbewussten, selbstreflektierenden und dynamisch lernenden System** resultiert. Es kann sowohl mit bekanntem Wissen sicher umgehen als auch Wissenslücken erkennen und aktiv deren Schließung mit menschlicher Hilfe einleiten.
