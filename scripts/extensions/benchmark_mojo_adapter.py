"""
Benchmark Mojo Adapter (READ-ONLY)
==================================

Zweck:
- Read-only Benchmark der Adapter-Funktionen gegen Live-API-Daten (nur GET)
- Misst Zeit für Batch-Validierung und einfache Dedupe-Heuristik
- Schreibt optional einen Markdown-Report in PROJECT_HUB

Aufruf (im Hex venv):
    python scripts/extensions/benchmark_mojo_adapter.py --limit 2000 --out PROJECT_HUB/REPORT_MOJO_BENCHMARK.md

Hinweis:
- Keine Schreib-APIs werden aufgerufen. Sicher für laufenden Betrieb.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import urllib.request


def http_get_json(url: str, timeout: float = 10.0) -> Dict[str, Any]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
        data = resp.read().decode("utf-8", errors="ignore")
    try:
        return json.loads(data)
    except Exception:
        return {}


def fetch_statements(api_base: str, limit: int) -> List[str]:
    """Read-only Export der ersten N Facts als JSON (kein Schreibzugriff)."""
    url = f"{api_base.rstrip('/')}/api/facts/export?limit={int(limit)}&format=json"
    payload = http_get_json(url)
    facts = payload.get("facts") or []
    return [str(item.get("statement") or "").strip() for item in facts if isinstance(item, dict)]


def run_benchmark(statements: List[str]) -> Dict[str, Any]:
    """Führt Messungen für validate_facts_batch und find_duplicates aus.

    Nutzt den MojoKernelsAdapter, der Feature-Flag- und Fallback-gesteuert ist.
    """
    # Import adapter aus Projektpfad
    hex_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(hex_root / "src_hexagonal"))

    try:
        from adapters.mojo_kernels_adapter import MojoKernelsAdapter  # type: ignore
    except Exception as exc:  # pragma: no cover
        return {
            "error": f"failed_to_import_adapter: {exc}",
            "sample_size": len(statements),
        }

    adapter = MojoKernelsAdapter()
    info = {
        "flag_enabled": bool(adapter.is_flag_enabled()),
        "available": bool(adapter.is_available()),
        "backend": adapter.backend_name(),
    }

    # validate_facts_batch
    t0 = time.perf_counter()
    valid = adapter.validate_facts_batch(statements)
    t1 = time.perf_counter()
    num_valid = int(sum(1 for x in valid if x))

    # find_duplicates (auf kleiner Probe, um Quadratik zu begrenzen)
    sample_for_dupe = statements[: min(2000, len(statements))]
    t2 = time.perf_counter()
    dupes: List[Tuple[int, int, float]] = adapter.find_duplicates(sample_for_dupe, threshold=0.95)
    t3 = time.perf_counter()

    return {
        "adapter": info,
        "sample_size": len(statements),
        "validate": {
            "valid_true": num_valid,
            "valid_false": len(statements) - num_valid,
            "duration_ms": round((t1 - t0) * 1000.0, 3),
        },
        "duplicates": {
            "checked_sample": len(sample_for_dupe),
            "pairs": len(dupes),
            "duration_ms": round((t3 - t2) * 1000.0, 3),
            "threshold": 0.95,
        },
    }


def write_report_markdown(path: Path, api_base: str, limit: int, result: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    lines.append(f"# Mojo Adapter Benchmark (Read-Only)")
    lines.append("")
    lines.append(f"Zeitpunkt: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"API Base: {api_base}")
    lines.append(f"Limit: {limit}")
    lines.append("")
    lines.append("## Adapter")
    adapter = result.get("adapter", {})
    lines.append(f"- flag_enabled: {adapter.get('flag_enabled')}")
    lines.append(f"- available: {adapter.get('available')}")
    lines.append(f"- backend: {adapter.get('backend')}")
    lines.append("")
    lines.append("## Ergebnisse")
    lines.append("```")
    lines.append(json.dumps(result, ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")
    lines.append("## Hinweise")
    lines.append("- Nur GET-Aufrufe; keine Schreiboperationen.")
    lines.append("- Dedupe-Sample begrenzt (max 2000) zur Laufzeitbegrenzung.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only benchmark for Mojo adapter")
    parser.add_argument("--api", default="http://127.0.0.1:5001", help="Hex API base URL")
    parser.add_argument("--limit", type=int, default=2000, help="Number of facts to sample via export")
    parser.add_argument("--out", default=str(Path("PROJECT_HUB") / "REPORT_MOJO_BENCHMARK.md"), help="Output markdown report path")
    args = parser.parse_args()

    statements = fetch_statements(args.api, args.limit)
    result = run_benchmark(statements)

    out_path = Path(__file__).resolve().parents[2] / args.out
    write_report_markdown(out_path, args.api, args.limit, result)

    # Kurzresultat auf STDOUT
    print(json.dumps({
        "adapter": result.get("adapter", {}),
        "sample_size": result.get("sample_size"),
        "validate_ms": result.get("validate", {}).get("duration_ms"),
        "dupes_ms": result.get("duplicates", {}).get("duration_ms"),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()


