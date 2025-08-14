#!/usr/bin/env python3
"""
Generate an integrity report for HAK_GAL_HEXAGONAL and write it to PROJECT_HUB/reports.
- Queries the Hexagonal API (port 5001) for: facts/count, predicates/top, quality/metrics, status
- Produces a timestamped Markdown report summarizing data health and actionable checks
- Safe, read-only; no mutations.

Usage (Windows PowerShell):
  .\.venv_hexa\Scripts\python.exe scripts\generate_integrity_report.py

Environment:
  HAKGAL_API_BASE_URL (optional) default: http://127.0.0.1:5001
"""
from __future__ import annotations

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import urllib.request
import urllib.error

API_BASE = os.environ.get("HAKGAL_API_BASE_URL", "http://127.0.0.1:5001")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
HUB_DIR = PROJECT_ROOT / "PROJECT_HUB"
REPORTS_DIR = HUB_DIR / "reports"


def fetch_json(url: str, timeout: float = 10.0) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        try:
            return json.loads(data.decode("utf-8", errors="replace"))
        except Exception:
            return {}


def main() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = REPORTS_DIR / f"knowledge_integrity_{ts}.md"

    errors: list[str] = []

    def safe_fetch(path: str) -> Dict[str, Any]:
        url = f"{API_BASE}{path}"
        try:
            return fetch_json(url)
        except urllib.error.URLError as e:
            errors.append(f"Fetch error {path}: {e}")
            return {}
        except Exception as e:
            errors.append(f"Fetch error {path}: {e}")
            return {}

    status = safe_fetch("/api/status?light=1")
    facts_count = safe_fetch("/api/facts/count")
    preds_top = safe_fetch("/api/predicates/top?limit=15&sample_limit=5000")
    quality = safe_fetch("/api/quality/metrics?sample_limit=5000")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines: list[str] = []
    lines.append(f"# Knowledge Integrity Report — {now}")
    lines.append("")
    lines.append(f"API Base: `{API_BASE}`")
    lines.append("")

    # Status
    lines.append("## System Status (light)")
    if status:
        lines.append("```")
        lines.append(json.dumps(status, indent=2))
        lines.append("```")
    else:
        lines.append("Status: <unavailable>")
    lines.append("")

    # Facts Count
    lines.append("## Facts Count")
    if facts_count:
        cnt = facts_count.get("count")
        cached = facts_count.get("cached")
        lines.append(f"- count: **{cnt}**  (cached={cached})")
    else:
        lines.append("- <unavailable>")
    lines.append("")

    # Predicates Top
    lines.append("## Top Predicates (sample)")
    if preds_top and preds_top.get("top_predicates"):
        lines.append("| Predicate | Count |")
        lines.append("|---|---:|")
        for item in preds_top["top_predicates"]:
            lines.append(f"| {item.get('predicate')} | {item.get('count')} |")
    else:
        lines.append("<unavailable>")
    lines.append("")

    # Quality metrics
    lines.append("## Quality Metrics (sample)")
    if quality:
        total = quality.get("total")
        checked = quality.get("checked")
        invalid = quality.get("invalid")
        duplicates = quality.get("duplicates")
        isolated = quality.get("isolated")
        contradictions = quality.get("contradictions")
        lines.append(f"- total: **{total}**")
        lines.append(f"- checked: **{checked}**")
        lines.append(f"- invalid: **{invalid}**")
        lines.append(f"- duplicates: **{duplicates}**")
        lines.append(f"- isolated: **{isolated}**")
        lines.append(f"- contradictions: **{contradictions}**")
        lines.append("")
        tp = quality.get("top_predicates") or []
        if tp:
            lines.append("### Quality: Top Predicates (sample)")
            lines.append("| Predicate | Count |")
            lines.append("|---|---:|")
            for item in tp:
                lines.append(f"| {item.get('predicate')} | {item.get('count')} |")
            lines.append("")
    else:
        lines.append("<unavailable>")
        lines.append("")

    # Actionable checks
    lines.append("## Actionable Checks")
    lines.append("- Ensure adapter is SQLite (writable) in status; if JSONL, write ops may be no-op.")
    lines.append("- If invalid/duplicates/contradictions are non-zero, schedule clean-up runs and human verification.")
    lines.append("- Track trends by comparing this report against previous days.")
    lines.append("")

    if errors:
        lines.append("## Collector Notes")
        lines.append("```")
        for e in errors[:20]:
            lines.append(e)
        lines.append("```")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written: {out_path}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
