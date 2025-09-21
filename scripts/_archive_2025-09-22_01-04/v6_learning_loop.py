#!/usr/bin/env python3
"""
V6 LEARNING LOOP (Interactive)
===============================
- Einfache Ausführung: python v6_learning_loop.py
- Fragt nach: Dauer (Stunden), Episoden/Zyklus (20/40/custom), Threshold, Modus (Shadow/Auto), Kandidaten-Datei
- Läuft in Zyklen (minütlich einstellbar) über die gewählte Gesamtdauer
- Nutzt v6_safe_boost intern; misst Netto-Zuwachs an Facts über /api/facts/count
- Schreibt Session-Summary in logs/v6_learning_summary_*.json
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

# Projektpfad
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


def prompt_int(question: str, default: int, choices: Optional[list[int]] = None) -> int:
	while True:
		val = input(f"{question} [{default}]: ").strip()
		if not val:
			return default
		try:
			num = int(val)
			if choices and num not in choices:
				print(f"Bitte eine der Optionen {choices} wählen.")
				continue
			return num
		except ValueError:
			print("Bitte eine ganze Zahl eingeben.")


def prompt_float(question: str, default: float) -> float:
	while True:
		val = input(f"{question} [{default}]: ").strip()
		if not val:
			return default
		try:
			num = float(val)
			if not (0.0 <= num <= 1.0):
				print("Bitte einen Wert zwischen 0.0 und 1.0 eingeben.")
				continue
			return num
		except ValueError:
			print("Bitte eine Zahl (0..1) eingeben.")


def prompt_choice(question: str, options: Dict[str, str], default_key: str) -> str:
	keys = "/".join(options.keys())
	while True:
		val = input(f"{question} ({keys}) [{default_key}]: ").strip().lower()
		if not val:
			return default_key
		if val in options:
			return val
		print(f"Bitte eine der Optionen eingeben: {keys}")


def get_fact_count() -> Optional[int]:
	try:
		r = requests.get(f"{API_BASE}/api/facts/count", timeout=5)
		if r.status_code == 200:
			return int(r.json().get('count')) if r.json().get('count') is not None else None
		return None
	except Exception:
		return None


def run_cycle(episodes: int, threshold: float, auto: bool, candidates_path: Optional[str]) -> Dict[str, Any]:
	# v6-Parameter setzen
	v6.MIN_COMBINED = float(threshold)
	v6.SHADOW_MODE = (not auto)
	facts = v6.load_input(candidates_path)
	start = time.time()
	# ruhiger Lauf: keine Einzelitems, nur Summary in Konsole
	v6.process_statements(facts, episodes=episodes, v5_style=True, quiet_items=True, json_summary=False)
	dur = time.time() - start
	return {"duration_sec": dur}


def main() -> None:
	print("\n================= V6 LEARNING LOOP (Interactive) =================")
	print("Dieser Assistent richtet eine Lernsession ein und führt sie aus.\n")

	# Eingaben
	hours = prompt_int("Dauer in Stunden", 1)
	ep_choice = prompt_choice("Episoden pro Zyklus", {"20": "20", "40": "40", "c": "custom"}, "20")
	if ep_choice in ("20", "40"):
		episodes = int(ep_choice)
	else:
		episodes = prompt_int("Episoden (Zahl)", 20)
	threshold = prompt_float("Threshold (Combined 0..1)", v6.MIN_COMBINED)
	mode = prompt_choice("Modus (shadow=prüfen / auto=einspielen)", {"shadow": "Shadow", "auto": "Auto-Add"}, "shadow")
	interval_min = prompt_int("Zyklus-Intervall in Minuten", 5)
	cand_path = input("Pfad zur Kandidaten-Datei (Enter für Default): ").strip() or None

	# Ausgangszustand
	count_start = get_fact_count()
	if count_start is None:
		print("[WARN] Konnte Facts-Count nicht lesen. Netto-Zuwachs wird aus Endstand abgeleitet.")
	else:
		print(f"Start-Fact-Count: {count_start}")

	end_time = datetime.now() + timedelta(hours=hours)
	session_stats = {
		"started": datetime.now().isoformat(),
		"hours": hours,
		"episodes_per_cycle": episodes,
		"threshold": threshold,
		"mode": mode,
		"interval_min": interval_min,
		"candidates": cand_path or "<default>",
		"cycles": []
	}

	cycle_idx = 0
	while datetime.now() < end_time:
		cycle_idx += 1
		print(f"\n--- Zyklus {cycle_idx} ---")
		cycle_before = get_fact_count()
		info = run_cycle(episodes, threshold, auto=(mode == 'auto'), candidates_path=cand_path)
		cycle_after = get_fact_count()
		delta = None
		if cycle_before is not None and cycle_after is not None:
			delta = cycle_after - cycle_before
			print(f"Zyklus-Differenz (Facts): {delta:+d}")
		print(f"Zyklus-Dauer: {info['duration_sec']:.1f}s")
		session_stats["cycles"].append({
			"idx": cycle_idx,
			"before": cycle_before,
			"after": cycle_after,
			"delta": delta,
			"duration_sec": info["duration_sec"]
		})
		# Warten bis nächster Zyklus oder Ende
		if datetime.now() >= end_time:
			break
		sleep_sec = max(0, interval_min * 60)
		print(f"Warte {sleep_sec}s bis zum nächsten Zyklus ... (Strg+C zum Abbrechen)")
		try:
			time.sleep(sleep_sec)
		except KeyboardInterrupt:
			print("\nAbbruch durch Benutzer.")
			break

	# Abschluss
	count_end = get_fact_count()
	netto = None
	if count_start is not None and count_end is not None:
		netto = count_end - count_start
	print("\n================= SESSION SUMMARY =================")
	print(f"Zyklen: {len(session_stats['cycles'])} | Stunden: {hours} | Modus: {mode.upper()} | Episoden/Zyklus: {episodes} | Threshold: {threshold}")
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

