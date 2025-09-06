# Claude's Guide: Optimale LLM-Kommunikation im HAK-GAL System

**Dokument-ID:** CLAUDE-LLM-COMM-GUIDE-20250904
**Status:** Best Practices fuer Claude-Instanzen
**Zweck:** Wie ich (Claude) optimal mit anderen LLMs ueber delegate_task kommuniziere

## GOLDENE REGEL: Keine Code-Aenderungen noetig!

Das HAK-GAL System ist bereits optimal designed. Die Flexibilitaet von `delegate_task` erlaubt alle Optimierungen durch bessere Prompts. **"Never touch a running system"** - nutze es optimal, verkompliziere es nicht.

## 1. DeepSeek-R1 Kommunikation

### Kernerkenntnisse:
- **KEINE separate Reasoning API** - alles laeuft ueber chat completions
- **Endpoint:** https://api.deepseek.com/chat/completions
- **Timeout:** 60 Sekunden fuer Deep Reasoning
- **Temperature:** 0.3 fuer fokussiertes Reasoning

### Optimaler Prompt-Aufbau:
```
Du bist ein DeepSeek Reasoning Agent. Denke IMMER Schritt fuer Schritt!

AUFGABE: [Konkrete Aufgabenstellung]

REASONING FORMAT:
[THINKING]: Zeige deine initialen Ueberlegungen
[STEP 1]: Erster logischer Schritt
[STEP 2]: Zweiter logischer Schritt  
[CONCLUSION]: Finale Antwort mit Begruendung

Verwende Temperature 0.3 fuer fokussiertes Reasoning.
```

### Wann DeepSeek verwenden:
- **Komplexe technische Analysen** (10-30 Sekunden Response-Zeit)
- **Algorithmus-Design** und Optimierungen
- **Debugging** mit tiefem Reasoning
- **Performance-Analysen** (z.B. SQLite-Optimierung)

### Beispiel-Delegation:
```python
delegate_task(
    target_agent="DeepSeek:chat",
    task_description="""
    [SYSTEM]: DeepSeek Reasoning Mode - Denke Schritt fuer Schritt
    
    ANALYSE: Warum plateaut HAK-GAL bei 6500 Fakten?
    
    FORMAT:
    [THINKING]: Problemverstaendnis
    [ANALYSIS]: Root-Cause-Analyse
    [SOLUTION]: Konkrete Loesungsvorschlaege
    """
)
```

## 2. Gemini (Archimedes Engine) Kommunikation

### Kernerkenntnisse:
- **Via gemini_mcp_bridge.py** integriert
- **Model:** gemini-2.0-flash-exp
- **Response:** 3-5 Sekunden (schneller als DeepSeek)
- **Staerke:** Kreative Hypothesen-Generierung

### Optimaler Prompt-Aufbau:
```
As the Archimedes Engine, generate novel hypotheses for:

Domain: [Bereich]
Observed Phenomena: [Beobachtung]
Constraints: [Einschraenkungen]

For each hypothesis provide:
1. The hypothesis statement
2. Novelty score (0-1)
3. Feasibility score (0-1)
4. Experimental approach
```

### Wann Gemini verwenden:
- **Schnelle Hypothesen** (3-5 Sekunden)
- **Kreative Exploration**
- **Breite wissenschaftliche Ansaetze**
- **Code-Reviews** und Generierung

## 3. Multi-Agent Konsens-Pattern

### Fuer wichtige Entscheidungen:
```python
# Parallele Befragung
results = [
    delegate_task("DeepSeek:chat", task),  # Tiefes Reasoning
    delegate_task("Gemini:2.5-flash", task),  # Kreative Ansaetze
]

# Konsens evaluieren
consensus = consensus_evaluator(results)
```

## 4. Generelle LLM-Kommunikations-Prinzipien

### Chain-of-Thought (CoT) aktivieren:
- "Denke Schritt fuer Schritt"
- "Erklaere deine Logik"
- "Zeige deinen Reasoning-Prozess"

### Strukturierte Outputs anfordern:
- Verwende [TAGS] fuer Struktur
- Definiere klare Output-Formate
- Gib Beispiele wenn moeglich

### Temperature-Guidelines:
- **0.3**: Fokussiertes Reasoning, technische Analysen
- **0.5**: Balanciert
- **0.7**: Kreative Aufgaben
- **0.9**: Brainstorming

### Few-Shot Learning nutzen:
```
BEISPIEL:
Input: [Beispiel-Input]
Output: [Beispiel-Output im gewuenschten Format]

DEINE AUFGABE:
Input: [Echter Input]
Output: ?
```

## 5. Fehlerbehandlung

### Timeout-Management:
- DeepSeek: Erwarte 10-30 Sekunden, setze Timeout auf 60
- Gemini: Erwarte 3-5 Sekunden, setze Timeout auf 15
- Bei Timeout: Vereinfache Anfrage oder teile auf

### Fallback-Strategien:
```python
try:
    result = delegate_task("DeepSeek:chat", complex_task)
except TimeoutError:
    # Fallback zu schnellerem Modell
    result = delegate_task("Gemini:2.5-flash", simplified_task)
```

## 6. Was ich NICHT tun sollte

### Code-Aenderungen vermeiden:
- ❌ Neue Adapter schreiben wenn Prompts reichen
- ❌ Komplexe Wrapper um funktionierende Systeme
- ❌ Feature-Creep ohne klaren Nutzen

### Over-Engineering vermeiden:
- ❌ 500-Zeilen-Adapter fuer 5-Zeilen-Prompt-Verbesserung
- ❌ Abstraktion um der Abstraktion willen
- ❌ Loesungen fuer nicht-existente Probleme

## 7. Dokumentation und Wissenserhalt

### Nach jeder LLM-Interaktion:
1. Erfolgreiche Prompts als Fakten speichern
2. Performance-Metriken dokumentieren
3. Neue Erkenntnisse in KB ablegen

### Beispiel-Fakten:
```prolog
UsedPromptTemplate(DeepSeek, "[THINKING]_[ANALYSIS]_[CONCLUSION]", Success_Rate_95_Percent).
ResponseTime(DeepSeek_Complex_Analysis, 15_Seconds_Average).
OptimalTemperature(Technical_Reasoning, 0_3).
```

## 8. Praktische Checkliste

Vor jeder delegate_task Anfrage:
- [ ] Ist der Prompt klar strukturiert?
- [ ] Habe ich das Output-Format definiert?
- [ ] Ist die Temperature angepasst?
- [ ] Habe ich genuegend Timeout eingeplant?
- [ ] Gibt es einen Fallback-Plan?

## FAZIT

Das HAK-GAL System ist bereits optimal. Meine Aufgabe als Claude ist es:
1. **Optimale Prompts** zu formulieren
2. **Richtige Agenten** fuer Tasks zu waehlen
3. **Erkenntnisse** in der KB zu dokumentieren
4. **KEINE unnuetzen Code-Aenderungen** vorzuschlagen

**Merksatz:** "Die beste Verbesserung ist oft, das System optimal zu nutzen, nicht es zu veraendern."

---
*Letzte Aktualisierung: 2025-09-04*
*Naechste Review: Bei neuen LLM-Integrationen*