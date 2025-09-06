# WORKFLOW PRO - ANLEITUNG FÜR EINSTEIGER

## **WIE VERBINDE ICH NODES?**

### **1. NODES VERBINDEN:**
```
Von Node A → zu Node B:

1. Hover über den RECHTEN Rand von Node A
   → Ein kleiner Punkt erscheint (Output Port)

2. KLICKEN und HALTEN auf diesem Punkt

3. ZIEHEN Sie die Linie zum LINKEN Rand von Node B
   → Ein Punkt erscheint dort (Input Port)

4. LOSLASSEN über dem Input Port
   → Verbindung wird erstellt (animierte Linie)
```

### **2. PRAKTISCHES BEISPIEL - "Knowledge Analysis Workflow"**

**Was wir bauen:** Ein Workflow der:
1. Zählt wie viele Fakten in der DB sind
2. Sucht nach bestimmten Themen
3. Lässt eine AI die Ergebnisse analysieren
4. Speichert die Analyse (optional)

### **SCHRITT-FÜR-SCHRITT ANLEITUNG:**

#### **Schritt 1: Canvas vorbereiten**
- Klicke "Clear" Button (oben rechts)
- Bestätige mit OK

#### **Schritt 2: Ersten Node hinzufügen**
- Links in der Palette: **Knowledge Base** Kategorie
- Klicke auf **"Get Facts Count"**
- Node erscheint auf Canvas

#### **Schritt 3: Zweiten Node hinzufügen**
- Wieder Knowledge Base Kategorie
- Klicke auf **"Search Knowledge"**
- Node erscheint auf Canvas

#### **Schritt 4: Nodes positionieren**
- Klicke und ziehe Nodes an gewünschte Position
- Arrangiere sie nebeneinander mit etwas Abstand

#### **Schritt 5: VERBINDEN (wichtig!)**
```
Get Facts Count -----> Search Knowledge

1. Hover über RECHTEN Rand von "Get Facts Count"
2. Kleiner Kreis erscheint
3. KLICK und HALTE gedrückt
4. ZIEHE zum LINKEN Rand von "Search Knowledge"
5. LOSLASSEN wenn der Kreis dort erscheint
```

#### **Schritt 6: AI Node hinzufügen**
- Palette: **AI Agents** Kategorie (lila)
- Klicke **"Delegate to AI"**
- Verbinde "Search Knowledge" → "Delegate to AI"

#### **Schritt 7: Parameter anpassen**
- Klicke auf "Search Knowledge" Node
- Rechts erscheinen Properties
- Ändere "query" zu einem Thema (z.B. "workflow")

#### **Schritt 8: Workflow ausführen**
- Klicke **"Execute"** Button (oben)
- Beobachte:
  - Nodes leuchten während Execution
  - Logs erscheinen rechts
  - Results zeigen Output

---

## **VOLLSTÄNDIGES PRAXIS-BEISPIEL**

### **"System Health & Knowledge Report"**

Dieser Workflow:
1. Prüft System-Gesundheit
2. Zählt Fakten in Knowledge Base
3. Sucht nach wichtigen Themen
4. Generiert AI-Report
5. (Optional) Speichert Ergebnis

### **NODES SETUP:**

```
[Health Check] ─┐
                ├─→ [AI Analysis] ─→ [Save Result?]
[Facts Count] ──┤
                │
[Search] ────────┘
```

### **DETAILLIERTE SCHRITTE:**

1. **Clear Canvas**
2. **Add Nodes:**
   - Execution → Health Check
   - Knowledge Base → Get Facts Count  
   - Knowledge Base → Search Knowledge
   - AI Agents → Delegate to AI
   - Knowledge Base → Add Fact (optional)

3. **Connect:**
   - Health Check → AI Analysis
   - Facts Count → AI Analysis
   - Search → AI Analysis
   - AI Analysis → Add Fact

4. **Configure:**
   - Search: query = "HAK_GAL"
   - AI: task = "Create system health report"
   - Add Fact: Requires approval!

5. **Execute:**
   - Start with Dry Run (default)
   - Watch execution flow
   - Check results

---

## **TIPPS & TRICKS:**

### **Verbindungen:**
- ✅ Output (rechts) → Input (links)
- ✅ Ein Output kann zu mehreren Inputs
- ✅ Mehrere Outputs können zu einem Input
- ❌ Keine Schleifen (DAG only)

### **Execution:**
- **Dry Run:** Testet ohne echte Aktionen
- **Live Mode:** Führt aus (aber Write Protection)
- **Write Enabled:** Vorsicht! Macht echte Änderungen

### **Node-Farben:**
- 🟢 Grün = Lesen (sicher)
- 🟣 Lila = AI Agents
- 🔵 Blau = Berechnungen
- 🔴 Rot = Schreiben (gefährlich!)
- ⚪ Grau = Flow Control

### **Häufige Probleme:**

**"Ich kann nicht verbinden"**
→ Hover genau über den Rand
→ Warten bis Punkt erscheint
→ Click & Drag, nicht nur Click

**"Nodes überlappen sich"**
→ Drag Nodes auseinander
→ Nutze Zoom (Scrollrad)
→ Clear und neu anfangen

**"Execution failed"**
→ Check Logs Panel rechts
→ Prüfe Node-Parameter
→ Stelle sicher dass Verbindungen richtig sind

---

## **JETZT AUSPROBIEREN:**

1. Clear Canvas
2. Baue den "System Health Report" nach
3. Execute im Dry Run
4. Experimentiere mit verschiedenen Nodes

**Das System ist wie LEGO:**
- Nodes = Bausteine
- Verbindungen = wie sie zusammenpassen
- Execute = das Ganze laufen lassen

**Fangen Sie einfach an und experimentieren Sie!**