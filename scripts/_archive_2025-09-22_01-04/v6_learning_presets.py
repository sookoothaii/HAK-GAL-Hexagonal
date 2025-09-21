#!/usr/bin/env python3
"""
V6 LEARNING PRESETS (One-Question UX)
=====================================
- Start: python v6_learning_presets.py
- Eine Frage: Preset A/B/C oder D (Custom)
- Erklärt kurz die Auswirkungen (Dauer, Episoden/Zyklus, Modus, Threshold)
- Läuft in Zyklen und zeigt pro Zyklus Netto-Zuwachs (Facts) + Dauer
- Am Ende: kompakte Session-Summary + JSON-Datei unter logs/
- Nutzt v6_safe_boost intern (ruhig, ohne Item-Spam)
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

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
SUMMARY_PATH = LOG_DIR / f"v6_learning_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

PRESETS = {
	"A": {"hours": 1, "episodes": 20, "threshold": 0.75, "mode": "shadow", "interval_min": 5,
		"desc": "Sicher (Prüfen), 1h, 20 Episoden/Zyklus, konservativ"},
	"B": {"hours": 2, "episodes": 40, "threshold": 0.70, "mode": "shadow", "interval_min": 5,
		"desc": "Mehr Abdeckung (Prüfen), 2h, 40 Episoden/Zyklus"},
	"C": {"hours": 1, "episodes": 20, "threshold": 0.80, "mode": "auto", "interval_min": 5,
		"desc": "Produktiv (Einspielen), 1h, 20 Episoden/Zyklus, strenger"},
	"D": "custom"
}

HELP_TEXT = """
Erläuterungen:
- Episoden/Zyklus: wie viele Kandidaten pro Runde geprüft werden
- Mode shadow: nur prüfen (nichts einspielen), auto: geprüfte Kandidaten einspielen
- Threshold: Mindestwert für Combined Score (HRM/LLM/KB) von 0..1
- Intervall: Wartezeit zwischen den Runden in Minuten
""".strip()


def get_fact_count() -> Optional[int]:
	try:
		r = requests.get(f"{API_BASE}/api/facts/count", timeout=5)
		if r.status_code == 200:
			return int(r.json().get('count')) if r.json().get('count') is not None else None
		return None
	except Exception:
		return None


def run_cycle(episodes: int, threshold: float, auto: bool, candidates_path: Optional[str]) -> Dict[str, Any]:
	v6.MIN_COMBINED = float(threshold)
	v6.SHADOW_MODE = (not auto)
	facts = v6.load_input(candidates_path)
	start = time.time()
	# ruhiger V5-Stil, keine Einzelitems
	v6.process_statements(facts, episodes=episodes, v5_style=True, quiet_items=True, json_summary=False)
	dur = time.time() - start
	return {"duration_sec": dur}


def choose_preset() -> Dict[str, Any]:
	print("\n================= V6 LEARNING PRESETS =================")
	for key in ("A", "B", "C", "D"):
		if key == "D":
			print(" D) Custom – eigene Werte eingeben")
			continue
		p = PRESETS[key]
		print(f" {key}) {p['desc']}  | Dauer={p['hours']}h, Episoden/Zyklus={p['episodes']}, Mode={p['mode']}, Threshold={p['threshold']}, Intervall={p['interval_min']}m")
	print("=======================================================")
	print(HELP_TEXT)
	print("=======================================================")
	choice = input("Wähle Preset (A/B/C/D) [A]: ").strip().upper() or "A"
	if choice not in PRESETS:
		choice = "A"
	if PRESETS[choice] == "custom":
		return custom_preset()
	return PRESETS[choice]


def custom_preset() -> Dict[str, Any]:
	print("\nCustom-Einstellungen (Enter = Vorschlag nutzen)")
	hours = prompt_int("Dauer in Stunden", 1)
	episodes = prompt_int("Episoden/Zyklus", 20)
	threshold = prompt_float("Threshold (0..1)", 0.75)
	mode = prompt_choice("Modus", {"shadow": "prüfen", "auto": "einspielen"}, "shadow")
	interval_min = prompt_int("Intervall in Minuten", 5)
	cand_path = input("Pfad zur Kandidaten-Datei (Enter für Default): ").strip() or None
	return {"hours": hours, "episodes": episodes, "threshold": threshold, "mode": mode, "interval_min": interval_min, "candidates": cand_path}


def prompt_int(question: str, default: int) -> int:
	while True:
		val = input(f"{question} [{default}]: ").strip()
		if not val:
			return default
		try:
			return int(val)
		except ValueError:
			print("Bitte eine ganze Zahl eingeben.")


def prompt_float(question: str, default: float) -> float:
	while True:
		val = input(f"{question} [{default}]: ").strip()
		if not val:
			return default
		try:
			x = float(val)
			if 0.0 <= x <= 1.0:
				return x
			print("Bitte 0..1 eingeben.")
		except ValueError:
			print("Bitte eine Zahl eingeben.")


def prompt_choice(question: str, options: Dict[str, str], default_key: str) -> str:
	keys = "/".join(options.keys())
	while True:
		val = input(f"{question} ({keys}) [{default_key}]: ").strip().lower()
		if not val:
			return default_key
		if val in options:
			return val
		print(f"Bitte {keys} eingeben.")


def main() -> None:
	preset = choose_preset()
	# Ergänze Candidates optional
	cand_path = preset.get('candidates') if isinstance(preset.get('candidates', None), (str, type(None))) else None
	print("\nSTARTE LERNSESSION …")
	print(f"Modus: {preset['mode'].upper()} | Dauer: {preset['hours']}h | Episoden/Zyklus: {preset['episodes']} | Threshold: {preset['threshold']} | Intervall: {preset['interval_min']}m")
	print("(Strg+C beendet vorzeitig)\n")

	count_start = get_fact_count()
	if count_start is not None:
		print(f"Start-Fact-Count: {count_start}")

	end_time = datetime.now() + timedelta(hours=preset['hours'])
	session_stats = {
		"started": datetime.now().isoformat(),
		"hours": preset['hours'],
		"episodes_per_cycle": preset['episodes'],
		"threshold": preset['threshold'],
		"mode": preset['mode'],
		"interval_min": preset['interval_min'],
		"candidates": cand_path or "<default>",
		"cycles": []
	}

	cycle_idx = 0
	while datetime.now() < end_time:
		cycle_idx += 1
		print(f"\n--- Zyklus {cycle_idx} ---")
		before = get_fact_count()
		info = run_cycle(
			episodes=preset['episodes'],
			threshold=preset['threshold'],
			auto=(preset['mode'] == 'auto'),
			candidates_path=cand_path
		)
		after = get_fact_count()
		delta = None
		if before is not None and after is not None:
			delta = after - before
			print(f"Zyklus-Differenz (Facts): {delta:+d}")
		print(f"Zyklus-Dauer: {info['duration_sec']:.1f}s")
		session_stats["cycles"].append({
			"idx": cycle_idx,
			"before": before,
			"after": after,
			"delta": delta,
			"duration_sec": info["duration_sec"]
		})
		if datetime.now() >= end_time:
			break
		try:
			time.sleep(max(0, preset['interval_min'] * 60))
		except KeyboardInterrupt:
			print("\nAbbruch durch Benutzer.")
			break

	count_end = get_fact_count()
	netto = None
	if count_start is not None and count_end is not None:
		netto = count_end - count_start

	print("\n================= SESSION SUMMARY =================")
	print(f"Zyklen: {len(session_stats['cycles'])} | Modus: {preset['mode'].upper()} | Episoden/Zyklus: {preset['episodes']} | Threshold: {preset['threshold']}")
	if count_start is not None:
		print(f"Start: {count_start}")
	if count_end is not None:
		print(f"Ende : {count_end}")
	if netto is not None:
		print(f"Netto-Zuwachs (Facts): {netto:+d}")

	session_stats.update({
		"finished": datetime.now().isoformat(),
		"start_count": count_start,
		"end_count": count_end,
		"net_gain": netto
	})
	SUMMARY_PATH.write_text(json.dumps(session_stats, ensure_ascii=False, indent=2), encoding='utf-8')
	print(f"Summary gespeichert: {SUMMARY_PATH}")


if __name__ == '__main__':
	main()

