import os
import sys
import time
from pathlib import Path


def _import_mcp_client():
    # MCP-Client aus scripts/slack nutzen
    here = Path(__file__).resolve()
    slack_dir = here.parent.parent / 'slack'
    sys.path.append(str(slack_dir))
    from mcp_client import default_client  # type: ignore
    return default_client


def build_screenshot_text():
    default_client = _import_mcp_client()
    client = default_client()
    client.start()
    try:
        health = client.call_tool("health_check", {})
        stats = client.call_tool("kb_stats", {})
        system = client.call_tool("get_system_status", {})
        preds = client.call_tool("get_predicates_stats", {})
        growth = client.call_tool("growth_stats", {"days": 7})
        recent = client.call_tool("list_recent_facts", {"count": 5})
        audit = client.call_tool("list_audit", {"limit": 10})
        snaps = client.call_tool("project_list_snapshots", {"hub_path": "PROJECT_HUB", "limit": 8})

        lines = []
        lines.append("### HAK‑GAL MCP – System Screenshot (auto)")
        lines.append("")
        lines.append(f"Zeitpunkt: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("#### Health\n````\n" + health.strip() + "\n````")
        lines.append("#### Systemstatus\n````\n" + system.strip() + "\n````")
        lines.append("#### KB‑Stats\n````\n" + stats.strip() + "\n````")
        top10 = "\n".join([ln for ln in preds.splitlines() if ln.strip()][:10])
        lines.append("#### Top‑Predicates (Top 10)\n````\n" + top10 + "\n````")
        lines.append("#### Growth (7 Tage)\n````\n" + growth.strip() + "\n````")
        # Extract just statements for recent facts
        lines.append("#### Recent Facts (5)\n````\n" + "\n".join([ln for ln in recent.splitlines() if ln.strip() and not ln.lower().startswith('recent')]) + "\n````")
        lines.append("#### Letzte Audit‑Einträge (10)\n````\n" + audit.strip() + "\n````")
        lines.append("#### Snapshots (neueste zuerst)\n````\n" + snaps.strip() + "\n````")
        return "\n\n".join(lines)
    finally:
        client.stop()


def main():
    project_root = Path(__file__).resolve().parents[2]
    hub = project_root / 'PROJECT_HUB'
    hub.mkdir(exist_ok=True)
    ts = time.strftime('%Y%m%d_%H%M%S')
    out_path = hub / f"MCP_SCREENSHOT_{ts}.md"
    text = build_screenshot_text()
    out_path.write_text(text, encoding='utf-8')
    print(str(out_path))


if __name__ == '__main__':
    main()


