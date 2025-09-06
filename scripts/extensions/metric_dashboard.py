import json
from pathlib import Path


def main():
    # Minimal Grafana JSON Dashboard (placeholder)
    dashboard = {
        "title": "HAK-GAL Metrics",
        "panels": [
            {"type": "stat", "title": "Facts", "targets": []},
            {"type": "stat", "title": "Growth (7d)", "targets": []}
        ]
    }
    out = Path("PROJECT_HUB/grafana_dashboard.json")
    out.write_text(json.dumps(dashboard, indent=2), encoding="utf-8")
    print(f"OK: {out}")


if __name__ == "__main__":
    main()


