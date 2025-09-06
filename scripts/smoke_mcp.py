import json
import os
import time
import sys
from pathlib import Path

# Stelle sicher, dass das Projekt-Root im sys.path ist, damit 'scripts.slack' importierbar ist,
# auch wenn dieses Skript aus dem Unterordner 'scripts' gestartet wird.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.slack.mcp_client import default_client


def main() -> int:
    # Environment: bevorzugt Werte wie in .cursor/mcp.json
    os.environ.setdefault("HAKGAL_API_BASE_URL", "http://127.0.0.1:5001")
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("HAKGAL_WRITE_ENABLED", "false")
    if "HAKGAL_HUB_PATH" not in os.environ:
        os.environ["HAKGAL_HUB_PATH"] = os.path.join(os.getcwd(), "PROJECT_HUB")

    client = default_client()
    client.start()

    # Versuche die in start() gesendete tools/list Antwort (id==2) einzusammeln
    tools_count = None
    tool_names_preview: list[str] = []
    deadline = time.time() + 3.0
    while time.time() < deadline:
        line = client._readline(timeout=0.05)
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if obj.get("id") == 2 and "result" in obj:
            tools = obj.get("result", {}).get("tools", [])
            tools_count = len(tools)
            tool_names_preview = [t.get("name", "?") for t in tools[:10]]
            break

    print(f"tools/list -> count={tools_count} preview={tool_names_preview}")

    # Kern-Tools durchprobieren
    tests = [
        ("health_check", {}),
        ("kb_stats", {}),
        ("get_system_status", {}),
        ("search_knowledge", {"query": "system", "limit": 3}),
    ]

    for name, args in tests:
        try:
            out = str(client.call_tool(name, args))
            print(f"{name}: {out[:500]}")
        except Exception as e:
            print(f"{name} ERROR: {e}")

    client.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


