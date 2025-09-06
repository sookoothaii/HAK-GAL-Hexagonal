#!/usr/bin/env python3
"""
V6 AUTOPILOT (Minimal UX)
=========================
- Start: python v6_autopilot.py
- Eine Handvoll verständlicher Auswahlen direkt nach Start (ohne Fachjargon):
  1) Ziel: Prüfen (Shadow) oder Einspielen (Auto)
  2) Dauer: 15 Minuten / 1 Stunde / 2 Stunden
  3) Episoden pro Runde: 20 / 40 / 100
  4) Quelle: Aus Datenbank / Aus bisherigen Boost-Logs / Beispiel (kleines Demo-Set)
- Danach läuft der Lernkreislauf vollautomatisch:
  - Pro Runde: Kandidaten prüfen/einspielen (ruhige V5-Style Ausgabe), Dauer + Netto-Zuwachs anzeigen
  - Am Ende: Netto-Zuwachs (Facts), JSON-Summary in logs/
- Keine Pfadeingaben nötig (DB/Logs werden automatisch genutzt). Optionales LLM‑Boosting wirkt automatisch, wenn API‑Keys vorhanden sind.
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

try:
	import requests  # type: ignore
except Exception:
	raise SystemExit("requests nicht installiert. Bitte in der venv installieren.")

try:
	import v6_safe_boost as v6  # type: ignore
except Exception as e:
	raise SystemExit(f"v6_safe_boost konnte nicht importiert werden: {e}")

API_BASE = os.environ.get('V6_API_BASE', 'http://127.0.0.1:5002')
LOG_DIR = ROOT / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
SUMMARY_PATH = LOG_DIR / f"v6_autopilot_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

HELP_TEXT = """
Was bedeuten die Einstellungen?
- Ziel:
  • Prüfen (empfohlen): nichts wird eingespielt – es wird nur bewertet.
  • Einspielen: geprüfte, starke Kandidaten werden in die Wissensbasis übernommen.
- Dauer: wie lange der Kreislauf laufen soll.
- Episoden pro Runde: wie viele Kandidaten pro Runde geprüft/eingespielt werden.
- Quelle:
  • Aus Datenbank: nimmt echte Fakten aus der aktiven DB (sinnvoll zum Checken von Qualität/Recall).
  • Aus Boost-Logs: nutzt vorherige Boost‑Ergebnisse als Kandidaten.
  • Beispiel: kleines, internes Demo‑Set (für einen schnellen Test).
""".strip()


def choice(prompt: str, options: Dict[str, str], default_key: str) -> str:
	keys = "/".join(options.keys())
	while True:
		val = input(f"{prompt} ({keys}) [{default_key}]: ").strip().lower()
		if not val:
			return default_key
		if val in options:
			return val
		print(f"Bitte {keys} eingeben.")


def get_fact_count() -> Optional[int]:
	try:
		r = requests.get(f"{API_BASE}/api/facts/count", timeout=5)
		if r.status_code == 200:
			js = r.json()
			return int(js.get('count')) if js.get('count') is not None else None
		return None
	except Exception:
		return None


def fetch_candidates_from_db(limit: int) -> List[str]:
	# nutzt /api/facts/export?limit=N&format=json
	try:
		r = requests.get(f"{API_BASE}/api/facts/export?limit={limit}&format=json", timeout=10)
		if r.status_code == 200:
			facts = r.json().get('facts', [])
			stmts = [x.get('statement') for x in facts if x.get('statement')]
			# Einfache Normalisierung/Einzigartigkeit
			seen = set()
			out: List[str] = []
			for s in stmts:
				if s not in seen:
					seen.add(s)
					out.append(s)
					if len(out) >= limit:
						break
			return out
	except Exception:
		return []
	return []


def fetch_candidates_from_logs(limit: int) -> List[str]:
	candidates: List[str] = []
	seen = set()
	try:
		for p in sorted(LOG_DIR.glob('v6_boost_log_*.jsonl'), reverse=True):
			for line in p.read_text(encoding='utf-8', errors='ignore').splitlines():
				try:
					obj = json.loads(line)
					stmt = obj.get('normalized') or obj.get('original')
					if isinstance(stmt, str) and stmt and stmt not in seen:
						seen.add(stmt)
						candidates.append(stmt)
						if len(candidates) >= limit:
							return candidates
				except Exception:
					continue
	except Exception:
		return candidates
	return candidates


def fetch_candidates_example(limit: int) -> List[str]:
	base = [
		"IsA(Socrates, Philosopher).",
		"HasPart(Computer, CPU).",
		"Prevents(ProperNutrition, Deficiencies).",
		"SubfieldOf(Biotechnology, LifeSciences).",
	]
	# Wiederhole bis Limit
	out: List[str] = []
	while len(out) < limit:
		for s in base:
			out.append(s)
			if len(out) >= limit:
				break
	return out


def plan_to_text(cfg: Dict[str, Any]) -> None:
	print("\nGEWÄHLTER PLAN:")
	print(f"  Ziel         : {'EINspielen' if cfg['mode']=='auto' else 'PRÜFen (Shadow)'}")
	print(f"  Dauer        : {cfg['hours']}h")
	print(f"  Episoden/Rd. : {cfg['episodes']}")
	print(f"  Threshold    : {cfg['threshold']}")
	print(f"  Intervall    : {cfg['interval_min']}m zwischen Runden")
	print(f"  Quelle       : {cfg['source_desc']}")


def run_cycle(candidates: List[str], episodes: int, threshold: float, auto: bool) -> Dict[str, Any]:
	# V6 konfigurieren
	v6.MIN_COMBINED = float(threshold)
	v6.SHADOW_MODE = (not auto)
	start = time.time()
	v6.process_statements(candidates, episodes=episodes, v5_style=True, quiet_items=True, json_summary=False)
	dur = time.time() - start
	return {"duration_sec": dur}


def main() -> None:
	print("\n================= V6 AUTOPILOT =================")
	print(HELP_TEXT)
	print("================================================")
	# 1) Ziel
	mode = choice("Ziel", {"shadow": "prüfen", "auto": "einspielen"}, "shadow")
	# 2) Dauer
	dur_key = choice("Dauer", {"15m": "15 Minuten", "1h": "1 Stunde", "2h": "2 Stunden"}, "15m")
	if dur_key == '15m':
		hours = 0.25
	elif dur_key == '1h':
		hours = 1
	else:
		hours = 2
	# 3) Episoden
	epi_key = choice("Episoden pro Runde", {"20": "20", "40": "40", "100": "100"}, "20")
	episodes = int(epi_key)
	# 4) Quelle
	src_key = choice("Quelle", {"db": "Datenbank", "logs": "Boost-Logs", "demo": "Beispiel"}, "db")
	# Threshold (ohne Zahleneingabe: konservativ)
	threshold = 0.75 if mode == 'auto' else 0.70
	interval_min = 1  # kurze Pause standard

	cfg = {
		"mode": mode,
		"hours": hours,
		"episodes": episodes,
		"threshold": threshold,
		"interval_min": interval_min,
		"source": src_key,
		"source_desc": {"db": "Aus Datenbank", "logs": "Aus Boost-Logs", "demo": "Beispiel-Set"}[src_key]
	}
	plan_to_text(cfg)

	# Kandidaten beziehen (einmalig pro Session; in Runden wird gesliced)
	total_needed = max(episodes * 2, 200)  # etwas Puffer
	if src_key == 'db':
		candidates = fetch_candidates_from_db(total_needed)
	elif src_key == 'logs':
		candidates = fetch_candidates_from_logs(total_needed)
	else:
		candidates = fetch_candidates_example(total_needed)
	if not candidates:
		print("[WARN] Keine Kandidaten gefunden – es wird das Beispiel-Set verwendet.")
		candidates = fetch_candidates_example(total_needed)

	start_count = get_fact_count()
	if start_count is not None:
		print(f"Start-Fact-Count: {start_count}")

	end_time = datetime.now() + timedelta(hours=cfg['hours'])
	session = {
		"started": datetime.now().isoformat(),
		"config": cfg,
		"cycles": []
	}

	idx_start = 0
	cycle_no = 0
	while datetime.now() < end_time:
		cycle_no += 1
		print(f"\n--- Runde {cycle_no} ---")
		before = get_fact_count()
		batch = candidates[idx_start: idx_start + episodes]
		if not batch:
			print("[INFO] Kandidaten aufgebraucht – Session endet frühzeitig.")
			break
		info = run_cycle(batch, episodes=episodes, threshold=threshold, auto=(mode == 'auto'))
		after = get_fact_count()
		delta = None
		if before is not None and after is not None:
			delta = after - before
			print(f"Runden-Differenz (Facts): {delta:+d}")
		print(f"Runden-Dauer: {info['duration_sec']:.1f}s")
		session["cycles"].append({
			"idx": cycle_no,
			"before": before,
			"after": after,
			"delta": delta,
			"duration_sec": info["duration_sec"]
		})
		idx_start += episodes
		if datetime.now() >= end_time:
			break
		try:
			time.sleep(max(0, cfg['interval_min'] * 60))
		except KeyboardInterrupt:
			print("\nAbbruch durch Benutzer.")
			break

	end_count = get_fact_count()
	net = None
	if start_count is not None and end_count is not None:
		net = end_count - start_count
	print("\n================= SESSION SUMMARY =================")
	print(f"Runden: {len(session['cycles'])} | Modus: {cfg['mode'].upper()} | Episoden/Runde: {cfg['episodes']} | Threshold: {cfg['threshold']}")
	if start_count is not None:
		print(f"Start: {start_count}")
	if end_count is not None:
		print(f"Ende : {end_count}")
	if net is not None:
		print(f"Netto-Zuwachs (Facts): {net:+d}")

	session.update({
		"finished": datetime.now().isoformat(),
		"start_count": start_count,
		"end_count": end_count,
		"net_gain": net
	})
	SUMMARY_PATH.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding='utf-8')
	print(f"Summary gespeichert: {SUMMARY_PATH}")


if __name__ == '__main__':
	main()

