import os
import json
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Lokaler Import des MCP-Clients
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.append(str(SCRIPT_DIR))
from mcp_client import default_client  # noqa: E402


def post_to_slack(webhook_url: str, text: str) -> None:
    payload = {"text": text}
    data = json.dumps(payload).encode("utf-8")
    req = Request(webhook_url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=10) as resp:
            if resp.status not in (200, 204):
                raise RuntimeError(f"Slack webhook returned status {resp.status}")
    except HTTPError as e:
        raise RuntimeError(f"Slack webhook HTTPError: {e.code} {e.reason}") from e
    except URLError as e:
        raise RuntimeError(f"Slack webhook URLError: {e.reason}") from e


def build_status_text() -> str:
    client = default_client()
    client.start()
    try:
        health = client.call_tool("health_check", {})
        stats = client.call_tool("kb_stats", {})
        preds = client.call_tool("get_predicates_stats", {})
        growth = client.call_tool("growth_stats", {"days": 7})
        # Kurzer, gut lesbarer Block
        lines = []
        lines.append("*HAK-GAL Status* (MCP)")
        lines.append(f"Zeit: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("\n*Health*\n" + "```\n" + health.strip() + "\n```")
        lines.append("*KB Stats*\n" + "```\n" + stats.strip() + "\n```")
        # Predicates: nur Top-10 Zeilen
        pred_lines = [ln for ln in preds.splitlines() if ln.strip()][:10]
        lines.append("*Top Predicates*\n" + "```\n" + "\n".join(pred_lines) + "\n```")
        lines.append("*Growth (7d)*\n" + "```\n" + growth.strip() + "\n```")
        return "\n".join(lines)
    finally:
        client.stop()


def main() -> None:
    webhook = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if not webhook:
        raise SystemExit("SLACK_WEBHOOK_URL ist nicht gesetzt. Bitte als ENV konfigurieren.")
    text = build_status_text()
    post_to_slack(webhook, text)
    print("OK: Slack-Status gesendet.")


if __name__ == "__main__":
    main()


