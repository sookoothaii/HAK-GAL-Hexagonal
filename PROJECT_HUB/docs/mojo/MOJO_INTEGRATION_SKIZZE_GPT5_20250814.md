### Mojo-Integration für HAK‑GAL HEXAGONAL — Skizze (GPT‑5)

Datum: 2025‑08‑14

---

### Zielbild
- Mojo wird gezielt für Performance‑Hotspots genutzt, Python/MCP/Frontend bleiben unverändert.
- SQLite (Source of Truth), API auf Port 5001, MCP‑Tools kompatibel.
- Schrittweiser, risikoarmer Ersatz rechenintensiver Routinen durch Mojo‑Kerne.

---

### Geeignete Kandidaten (Priorität → Nutzen)
1. Fakten‑Parsing/Validierung (Syntax: `Predicate(Entity1, Entity2).`) – sehr häufig, CPU‑nah → 5–15×
2. Semantische Ähnlichkeit / Duplikaterkennung (Token‑Vektoren, Jaccard/Cosine) → 3–10×
3. Konsistenzprüfung (NichtX vs X) → 3–5×
4. JSONL⇄SQLite Bulk‑Konverter (Streaming, Zero‑Copy‑Parsing) → 3–8×
5. Aethelred‑Pipelines (Batch‑Vorverarbeitung, Confidence‑Filter) → 2–5×
6. Optional: HRM‑Kerne (z. B. RNN/GRU‑Kern in Mojo) → 2–4× (abhängig vom Backend/Device)

---

### Architektur‑Skizze (Hybrid)
```
React (Vite) ── REST/WebSocket ── Flask (Hexagonal API) ── MCP Server
                                           │
                                           │ (Python FFI)
                                           ▼
                                    Mojo Kernmodule (.so/.dll)
                                       ├─ parse_validate()
                                       ├─ similarity_batch()
                                       ├─ consistency_scan()
                                       └─ jsonl_to_sqlite()
```

---

### Interop‑Strategie
- Build: Mojo → native Lib (z. B. `libhakgal_mojo.{so|dll}`)
- FFI: Python über `ctypes`/`cffi`/pybind (präferiert: dünne C‑Wrapper für stabile ABI)
- Schnittstellen (Beispiele):
  - `parse_validate(lines: List[str]) -> List[ParsedFact]`
  - `similarity_batch(stmts: List[str], base: str, threshold: float) -> List[(score, idx)]`
  - `consistency_scan(stmts: List[str]) -> List[Conflict]`
  - `jsonl_to_sqlite(jsonl_path: str, sqlite_path: str, limit: int) -> Counts`

---

### API‑Anpassungen (nicht‑invasiv)
- Endpunkte behalten Semantik; Python‑Layer delegiert intern optional an Mojo.
- Fallback: bei FFI‑Fehlern automatische Rückkehr zur Python‑Implementierung.

---

### Minimaler Integrationspfad (3 Etappen)
1) Parsing/Validierung
   - Mojo‑Kern `parse_validate()` + Python‑Adapter `adapters/mojo_parser.py`
   - Wire‑up: `/api/facts/bulk` und Konsistenz-/Analyse‑Tools nutzen Mojo, wenn verfügbar.

2) Similarity/Dedupe
   - Mojo‑Kern `similarity_batch()`
   - MCP‑Tools `semantic_similarity`, `analyze_duplicates` schalten auf Mojo.

3) JSONL⇄SQLite Bulk
   - Mojo‑Streaming‑Konverter für Imports/Exports (Batch‑Jobs, Scripts‑Kategorie)

---

### Beispiel: Python‑Adapter (Pseudocode)
```python
# adapters/mojo_similarity.py
try:
    import ctypes
    _lib = ctypes.CDLL('libhakgal_mojo.so')
    _lib.similarity_batch.restype = ctypes.c_int
    HAS_MOJO = True
except Exception:
    HAS_MOJO = False

def similarity_batch_py(statements: list[str], base: str, threshold: float) -> list[tuple[float,int]]:
    if not HAS_MOJO:
        # Fallback: Python‑Pfad (bestehende Implementierung)
        from .py_similarity import similarity_batch
        return similarity_batch(statements, base, threshold)
    # TODO: Buffer/Marshalling und Aufruf _lib.similarity_batch(...)
    return []
```

---

### Build/Deploy
- Separate `scripts/build_mojo.bat`/`.sh` (Mojo → native Lib), Artefakt in `native/` ablegen
- CI optional: nur auf dev‑Maschinen mit Mojo‑Toolchain; sonst reine Python‑Fallbacks aktiv

---

### Metriken & Tests
- Benchmarks: vor/nach (Parsing, Similarity, Bulk‑Import) auf 1k/10k/100k Zeilen
- Korrektheit: Golden‑Files (gleiches Ergebnis zwischen Mojo/Python), Property‑Tests
- Observability: Timing in Logs (Mojo vs Python), MCP‑Tool `growth_stats`

---

### Risiken & Mitigation
- ABI/Interop‑Fehler → dünne C‑Wrapper + umfassende Unit‑Tests
- Plattform‑Unterschiede (Windows/Linux) → CI‑Matrix, prebuilt Artefakte
- Toolchain‑Verfügbarkeit → Feature‑Flag `MOJO_ENABLED`, sichere Defaults

---

### Roadmap (2–3 Wochen)
W1: Parser/Validator (Mojo) + Adapter + Benchmarks
W2: Similarity/Dedupe (Mojo) + MCP‑Tool‑Switch + Tests
W3: JSONL⇄SQLite (Mojo) + Scripts + End‑to‑End

---

### Deliverables
- `native/libhakgal_mojo.*` + Header/C‑Wrapper
- Python‑Adapter in `src_hexagonal/adapters/`
- Benchmarks/Reports im `PROJECT_HUB`
- Feature‑Flag + Fallback‑Logik (robust)


