# Screenshot – KB-Beschleunigung (Integritätsreport + Kandidaten-Generator)

Datum: 2025-08-14
Autor: GPT-5

```mermaid
flowchart TB
  subgraph "Ziel: Schnelleres, verlässliches KB-Wachstum"
    Z1["Integritätsreport (täglich)"]
    Z2["Kandidaten-Generator (Themen → Fakten)"]
  end

  subgraph "Integritätsreport"
    I1["/api/status?light=1"]
    I2["/api/facts/count"]
    I3["/api/predicates/top"]
    I4["/api/quality/metrics"]
  end

  subgraph "Kandidaten-Generator"
    K1["topics.txt"]
    K2["/api/llm/get-explanation"]
    K3["Regex & /api/logicalize"]
    K4["candidates_<ts>.md (Review)"]
  end

  Z1 --> I1
  Z1 --> I2
  Z1 --> I3
  Z1 --> I4
  Z2 --> K1
  K1 --> K2
  K2 --> K3
  K3 --> K4
```

Kurzüberblick:
- `scripts/generate_integrity_report.py`: schreibt nach `PROJECT_HUB/reports/knowledge_integrity_<ts>.md` (Status, Counts, Top-Predicates, Quality).
- `scripts/generate_candidates_from_topics.py`: liest `PROJECT_HUB/topics.txt`, erzeugt `PROJECT_HUB/reports/candidates_<ts>.md` zur Human-Review.

Empfohlener Tagesablauf:
1. Themenliste pflegen: `PROJECT_HUB/topics.txt`
2. Kandidaten erzeugen:
   - ` .\.venv_hexa\Scripts\python.exe scripts\generate_candidates_from_topics.py`
3. Review & Freigabe in `candidates_<ts>.md`, dann sichere Aufnahme (MCP/REST) mit Kontextquelle (z. B. `human_verified`).
