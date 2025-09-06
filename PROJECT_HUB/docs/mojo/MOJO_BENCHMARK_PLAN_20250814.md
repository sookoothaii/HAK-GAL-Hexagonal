# Mojo Benchmark Plan (Read-Only, Safe)

Ziel: Messbare, gefahrlose Evaluation des Mojo-Adapters ohne Änderungen an Produktionspfaden.

## KPIs
- validate_facts_batch: Dauer (ms) für N Statements
- find_duplicates: Dauer (ms) für N (Sample max 2000)
- Korrektheit: Ergebnisgleichheit Stub/Fallback vs. später native Kernels

## Vorgehen
1. Read-only Export nutzen (`/api/facts/export?format=json&limit=N`).
2. `scripts/extensions/benchmark_mojo_adapter.py --limit N --out PROJECT_HUB/REPORT_MOJO_BENCHMARK.md` ausführen.
3. Ergebnis (Adapter-Status + Zeiten) im Hub reporten.
4. Später mit nativen Kernels wiederholen; Golden-Tests ergänzen.

## Sicherheit
- Nur GET-Requests; keine Schreibpfade.
- Flag bleibt steuernd; ohne native Kernels greift Stub/Fallback.
