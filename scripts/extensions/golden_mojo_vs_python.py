"""
Golden Test – Mojo vs Python Fallback (READ-ONLY)
=================================================

Vergleicht Ergebnisgleichheit zwischen Mojo-Pfad und Python-Fallback für:
- validate_facts_batch (vollständige Liste)
- find_duplicates (Sample max 2000; threshold 0.95)

Quelle der Statements: /api/facts/export (GET, read-only)
Ergebnis: Markdown-Report im PROJECT_HUB
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple, Set

import urllib.request


def http_get_json(url: str, timeout: float = 15.0) -> Dict[str, Any]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
        data = resp.read().decode("utf-8", errors="ignore")
    try:
        return json.loads(data)
    except Exception:
        return {}


def fetch_statements(api_base: str, limit: int) -> List[str]:
    url = f"{api_base.rstrip('/')}/api/facts/export?limit={int(limit)}&format=json"
    payload = http_get_json(url)
    facts = payload.get("facts") or []
    return [str(item.get("statement") or "").strip() for item in facts if isinstance(item, dict)]


def load_adapter(flag_enabled: bool):
    # Isoliere Flag-Wert pro Adapter-Instanz
    env_before = os.environ.get("MOJO_ENABLED")
    try:
        os.environ["MOJO_ENABLED"] = "true" if flag_enabled else "false"
        # Projektpfad hinzufügen
        hex_root = Path(__file__).resolve().parents[2]
        sys.path.insert(0, str(hex_root / "src_hexagonal"))
        from adapters.mojo_kernels_adapter import MojoKernelsAdapter  # type: ignore
        return MojoKernelsAdapter()
    finally:
        if env_before is None:
            os.environ.pop("MOJO_ENABLED", None)
        else:
            os.environ["MOJO_ENABLED"] = env_before


def compare_validate(a: List[bool], b: List[bool]) -> Tuple[int, List[int]]:
    mismatches = [i for i, (x, y) in enumerate(zip(a, b)) if bool(x) != bool(y)]
    return len(mismatches), mismatches[:50]


def to_pair_set(pairs: List[Tuple[int, int, float]]) -> Set[Tuple[int, int]]:
    return {(min(i, j), max(i, j)) for i, j, _ in pairs}


def run_golden(statements: List[str], threshold: float = 0.95) -> Dict[str, Any]:
    # Adapter A: Fallback (Python)
    adapter_py = load_adapter(flag_enabled=False)
    # Adapter B: Mojo aktiviert (kann stub/native sein)
    adapter_mojo = load_adapter(flag_enabled=True)

    # validate
    v_py = adapter_py.validate_facts_batch(statements)
    v_mj = adapter_mojo.validate_facts_batch(statements)
    mis_cnt, mis_list = compare_validate(v_py, v_mj)

    # dedupe auf Sample
    sample = statements[: min(2000, len(statements))]
    d_py = adapter_py.find_duplicates(sample, threshold)
    d_mj = adapter_mojo.find_duplicates(sample, threshold)
    s_py, s_mj = to_pair_set(d_py), to_pair_set(d_mj)
    # Metriken
    only_py = list(s_py - s_mj)[:50]
    only_mj = list(s_mj - s_py)[:50]

    return {
        "validate": {
            "total": len(statements),
            "mismatches": mis_cnt,
            "mismatch_indices_preview": mis_list,
        },
        "duplicates": {
            "sample": len(sample),
            "pairs_python": len(s_py),
            "pairs_mojo": len(s_mj),
            "only_python_preview": only_py,
            "only_mojo_preview": only_mj,
            "threshold": threshold,
        },
        "adapters": {
            "python": {
                "flag_enabled": adapter_py.is_flag_enabled(),
                "available": adapter_py.is_available(),
                "backend": adapter_py.backend_name(),
            },
            "mojo": {
                "flag_enabled": adapter_mojo.is_flag_enabled(),
                "available": adapter_mojo.is_available(),
                "backend": adapter_mojo.backend_name(),
            },
        },
    }


def write_report(path: Path, api_base: str, limit: int, result: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    lines.append(f"# MOJO Golden Test – Python vs Mojo (Read-Only)")
    lines.append("")
    lines.append(f"Zeitpunkt: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"API Base: {api_base}")
    lines.append(f"Limit: {limit}")
    lines.append("")
    lines.append("## Ergebnis")
    lines.append("```")
    lines.append(json.dumps(result, ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("- Ziel ist 0 Mismatches bei validate und sehr ähnliche Dupe-Pair-Sets.")
    lines.append("- Kleinere Abweichungen bei Dedupe sind durch Gleichstand/Tokenisierung möglich – prüfen, ob akzeptabel.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description="Golden comparison Mojo vs Python (read-only)")
    p.add_argument("--api", default="http://127.0.0.1:5001")
    p.add_argument("--limit", type=int, default=5000)
    p.add_argument("--out", default=str(Path("PROJECT_HUB") / "REPORT_MOJO_GOLDEN.md"))
    args = p.parse_args()

    stmts = fetch_statements(args.api, args.limit)
    result = run_golden(stmts)
    out_path = Path(__file__).resolve().parents[2] / args.out
    write_report(out_path, args.api, args.limit, result)
    print(json.dumps({
        "validate_mismatches": result["validate"]["mismatches"],
        "dupes_python": result["duplicates"]["pairs_python"],
        "dupes_mojo": result["duplicates"]["pairs_mojo"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()


