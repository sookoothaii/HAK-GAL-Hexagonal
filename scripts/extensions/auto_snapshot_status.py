from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict
import urllib.request


def http_get_json(url: str, timeout: float = 8.0) -> Dict[str, Any]:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
            data = resp.read().decode("utf-8", errors="ignore")
        return json.loads(data)
    except Exception:
        return {"error": "unreachable"}


def snapshot(api: str) -> Dict[str, Any]:
    base = api.rstrip('/')
    return {
        "health": http_get_json(f"{base}/health"),
        "status_light": http_get_json(f"{base}/api/status?light=1"),
        "facts_count": http_get_json(f"{base}/api/facts/count"),
        "quality": http_get_json(f"{base}/api/quality/metrics?sample_limit=5000"),
        "mojo": http_get_json(f"{base}/api/mojo/status"),
        "ts": time.strftime('%Y-%m-%d %H:%M:%S'),
        "api": base,
    }


def write_markdown(out: Path, data: Dict[str, Any]) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# Auto Snapshot – {data['api']} ({data['ts']})", ""]
    for key in ("health", "status_light", "facts_count", "quality", "mojo"):
        lines.append(f"## {key}")
        lines.append("```")
        lines.append(json.dumps(data.get(key), ensure_ascii=False, indent=2))
        lines.append("```")
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--api', required=True)
    p.add_argument('--out', required=True)
    args = p.parse_args()

    data = snapshot(args.api)
    write_markdown(Path(args.out), data)
    print(json.dumps({"ok": True, "out": args.out}, ensure_ascii=False))


if __name__ == '__main__':
    main()


