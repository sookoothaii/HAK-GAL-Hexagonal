#!/usr/bin/env python3
"""
V6 SAFE BOOST (V5-Style) - Shadow-Mode, Guardrails, Episoden, Combined Scoring
==============================================================================
- V5-nahe Bedienung (optional: --v5 für Ausgabe-Stil wie V5)
- Episoden-Limit wählbar (Standard 20; z.B. --episodes 40)
- Shadow-Mode standardmäßig AN (keine direkten Writes)
- Strikte Validierung: Predicate(Entity1, Entity2).
- Entitäten-Normalisierung: Leerzeichen → Unterstrich, nur [A-Za-z0-9_]
- Kombinierter Score: 0.5*HRM + 0.3*LLM + 0.2*KB (Fallback ohne LLM)
- Logging: logs/v6_boost_log_*.jsonl
- Optionales Auto-Add (Rate-Limit), nur wenn Shadow-Mode aus
"""

import os
import re
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
# LLM Activation
USE_LLM = os.environ.get('V6_USE_LLM', 'false').lower() == 'true'


# Pfad für lokalen Import
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src_hexagonal'))

try:
	from core.reasoning.hrm_system import get_hrm_instance  # type: ignore
except Exception:
	get_hrm_instance = None  # API-Fallback

try:
	import requests  # type: ignore
except Exception:
	requests = None

API_BASE = os.environ.get('V6_API_BASE', 'http://127.0.0.1:5002')
MODEL_PATH = os.environ.get('HRM_MODEL_PATH', 'models/hrm_model_v2.pth')

# Flags / Schwellen
SHADOW_MODE = (os.environ.get('V6_SHADOW_ENABLED', 'true').lower() in ('1', 'true', 'yes', 'on'))
MIN_COMBINED = float(os.environ.get('V6_MIN_COMBINED', '0.7'))
MAX_AUTO_ADDS = int(os.environ.get('V6_MAX_AUTO_ADDS', '5'))
TIMEOUT = int(os.environ.get('V6_HTTP_TIMEOUT', '5'))
DEFAULT_EPISODES = int(os.environ.get('V6_EPISODES', '20'))
V5_STYLE_DEFAULT = (os.environ.get('V6_V5_STYLE', 'false').lower() in ('1', 'true', 'yes', 'on'))

LOG_DIR = Path('logs')
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / f"v6_boost_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

PRED_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
ENTITY_CLEAN_RE = re.compile(r"[^A-Za-z0-9_]")
FACT_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\(([^,]+),\s*([^\)]+)\)\.$")


def normalize_entity(entity: str) -> str:
	text = ' '.join(entity.strip().split())
	text = text.replace(' ', '_')
	text = ENTITY_CLEAN_RE.sub('_', text)
	text = re.sub(r"_+", "_", text).strip('_')
	return text if text else 'Unknown'


def normalize_statement(stmt: str) -> Optional[str]:
	stmt = (stmt or '').strip()
	if not stmt:
		return None
	if not stmt.endswith('.'):
		stmt += '.'
	m = FACT_RE.match(stmt)
	if not m:
		# Weiches Parsing: "Pred A, B." → "Pred(A, B)."
		try:
			core = stmt[:-1] if stmt.endswith('.') else stmt
			if '(' not in core and ',' in core:
				parts = core.split(',', 1)
				pred_and_a = parts[0].strip().split(None, 1)
				if len(pred_and_a) == 2:
					pred, a = pred_and_a
					b = parts[1].strip()
					pred = pred.strip()
					a = normalize_entity(a)
					b = normalize_entity(b)
					if PRED_RE.match(pred):
						return f"{pred}({a}, {b})."
		except Exception:
			return None
		return None
	pred, a, b = m.group(1), m.group(2).strip(), m.group(3).strip()
	if not PRED_RE.match(pred):
		return None
	a_n = normalize_entity(a)
	b_n = normalize_entity(b)
	return f"{pred}({a_n}, {b_n})."


def hrm_score(statement: str) -> Optional[float]:
	try:
		if get_hrm_instance is not None:
			hrm = get_hrm_instance(MODEL_PATH)
			res = hrm.reason(statement)
			return float(res.get('confidence', 0.0))
		if requests is not None:
			resp = requests.post(f"{API_BASE}/api/reason", json={"query": statement}, timeout=TIMEOUT)
			if resp.status_code == 200:
				return float(resp.json().get('confidence', 0.0))
	except Exception:
		return None
	return None


def kb_evidence_score(statement: str) -> float:
	if requests is None:
		return 0.0
	score = 0.0
	try:
		# Direkte Suche
		r = requests.post(f"{API_BASE}/api/search", json={"query": statement, "limit": 5, "min_confidence": 0.0}, timeout=TIMEOUT)
		if r.status_code == 200 and r.json().get('count', 0) > 0:
			return 1.0
		# Fallback: Prädikat in Topliste
		m = FACT_RE.match(statement)
		if m:
			pred = m.group(1)
			p = requests.get(f"{API_BASE}/api/predicates/top?limit=50", timeout=TIMEOUT)
			if p.status_code == 200:
				items = [x.get('predicate') for x in p.json().get('top_predicates', [])]
				if pred in (items or []):
					score = 0.5
	except Exception:
		return 0.0
	return score


def llm_score(statement: str, context_facts: List[str]) -> Optional[float]:
	if requests is None:
		return None
	try:
		payload = {"topic": statement, "context_facts": context_facts[:10]}
		r = requests.post(f"{API_BASE}/api/llm/get-explanation", json=payload, timeout=TIMEOUT)
		if r.status_code != 200:
			return None
		data = r.json()
		suggested = data.get('suggested_facts') or []
		found = any((s == statement) or (isinstance(s, dict) and s.get('fact') == statement) for s in suggested)
		return 0.9 if found else 0.0
	except Exception:
		return None


def combined_score(hrm: Optional[float], llm: Optional[float], kb: float) -> float:
	if hrm is None and llm is None:
		return kb
	if llm is None:
		return 0.7 * float(hrm or 0.0) + 0.3 * kb
	return 0.5 * float(hrm or 0.0) + 0.3 * float(llm or 0.0) + 0.2 * kb


def log_result(item: Dict[str, Any]) -> None:
	with LOG_PATH.open('a', encoding='utf-8') as f:
		f.write(json.dumps(item, ensure_ascii=False) + '\n')


def try_auto_add(statement: str) -> Tuple[bool, str]:
	if SHADOW_MODE or requests is None:
		return False, 'shadow_mode'
	try:
		r = requests.post(f"{API_BASE}/api/facts", json={"statement": statement}, timeout=TIMEOUT)
		if r.status_code in (200, 201):
			return True, 'added'
		if r.status_code == 409:
			return False, 'exists'
		return False, f"status_{r.status_code}"
	except Exception as e:
		return False, f"error_{e.__class__.__name__}"


def collect_context(statement: str) -> List[str]:
	if requests is None:
		return []
	try:
		r = requests.post(f"{API_BASE}/api/search", json={"query": statement, "limit": 10, "min_confidence": 0.0}, timeout=TIMEOUT)
		if r.status_code == 200:
			return [x.get('statement', '') for x in r.json().get('results', []) if x.get('statement')]
	except Exception:
		return []
	return []


def header_v5(episodes: int) -> None:
	print("\n============================================================")
	print("🤖 V6 SAFE BOOST - Guardrails + Combined Scoring")
	print("============================================================")
	print("Features:\n✅ Shadow-Mode (Standard)\n✅ Strikte Validierung\n✅ Kombinierter Score (HRM/LLM/KB)\n✅ Logging & Rate-Limit\n============================================================")
	print("\n============================================================")
	print(f"🚀 V6 TEST - Episoden: {episodes} | Mode: {'SHADOW' if SHADOW_MODE else 'AUTO-ADD'} | Threshold: {MIN_COMBINED}")
	print("============================================================")


def print_item_v5(orig: str, norm: Optional[str], h: Optional[float], l: Optional[float], comb: float, decision: str, would_add: bool) -> None:
	print(f"\n📝 Original: {orig}")
	if norm and norm != orig:
		print(f"   ✏️ Fixed: {norm}")
	print(f"   HRM: {((h or 0.0)*100):.1f}%" if isinstance(h, float) else "   HRM: N/A")
	print(f"   🤖 LLM: {((l or 0.0)*100):.1f}%" if isinstance(l, float) else "   🤖 LLM: N/A")
	print(f"   ➡️ COMBINED: {(comb*100):.1f}%")
	if decision.startswith('added'):
		print("   ✅ GERETTET! Zur KB hinzugefügt!")
	elif SHADOW_MODE and would_add:
		print("   ✅ GERETTET! Würde zur KB hinzugefügt (Shadow).")
	elif decision.startswith('blocked_exists'):
		print("   ⚠️ Bereits vorhanden. Übersprungen.")
	else:
		print("   ⛔ BLOCKIERT (unter Threshold oder Policy).")


def process_statements(statements: List[str], episodes: int, v5_style: bool, quiet_items: bool = False, json_summary: bool = False) -> None:
	items = statements[: max(0, episodes)] if episodes and episodes > 0 else statements
	if v5_style:
		header_v5(len(items))
	else:
		print("\n============================================================")
		print("V6 SAFE BOOST - Shadow Mode" if SHADOW_MODE else "V6 SAFE BOOST - Auto Add Enabled")
		print("============================================================")

	start_ts = time.time()
	adds = 0
	# Metrics
	count_processed = 0
	count_invalid = 0
	count_dupes = 0
	count_added = 0
	count_shadow_would_add = 0
	count_below_threshold = 0
	count_other_block = 0
	values_hrm: List[float] = []
	values_llm: List[float] = []
	values_kb: List[float] = []
	values_comb: List[float] = []
	results_preview: List[Dict[str, Any]] = []

	for idx, raw in enumerate(items, start=1):
		orig = raw.strip()
		if not orig:
			continue
		norm = normalize_statement(orig)
		if not norm:
			log_result({'original': orig, 'normalized': None, 'valid': False, 'reason': 'invalid_format'})
			count_invalid += 1
			if not quiet_items:
				if v5_style:
					print(f"\n📝 Original: {orig}\n   ❌ INVALID FORMAT")
				else:
					print(f"❌ INVALID: {orig}")
			continue
		ctx = collect_context(norm)
		h = hrm_score(norm)
		kb = kb_evidence_score(norm)
		l = llm_score(norm, ctx)
		comb = combined_score(h, l, kb)
		would_add = comb >= MIN_COMBINED
		decision = 'keep_shadow'
		add_result = 'shadow'
		if would_add and adds < MAX_AUTO_ADDS:
			ok, msg = try_auto_add(norm)
			decision = ('added' if ok else f'blocked_{msg}')
			if ok:
				adds += 1
			add_result = msg
		# metrics aggregation
		count_processed += 1
		if isinstance(h, float):
			values_hrm.append(h)
		if isinstance(l, float):
			values_llm.append(l)
		values_kb.append(kb)
		values_comb.append(comb)
		if decision.startswith('added'):
			count_added += 1
		elif decision.startswith('blocked_exists'):
			count_dupes += 1
		elif SHADOW_MODE and would_add:
			count_shadow_would_add += 1
		elif not would_add:
			count_below_threshold += 1
		else:
			count_other_block += 1
		results_preview.append({'norm': norm, 'combined': comb, 'decision': decision})
		log_result({
			'timestamp': datetime.now().isoformat(),
			'original': orig,
			'normalized': norm,
			'valid': True,
			'hrm': h,
			'llm': l,
			'kb': kb,
			'combined': comb,
			'threshold': MIN_COMBINED,
			'shadow_mode': SHADOW_MODE,
			'decision': decision,
			'add_result': add_result,
			'context_preview': ctx[:5],
		})
		if not quiet_items:
			if v5_style:
				print_item_v5(orig, norm, h, l, comb, decision, would_add)
			else:
				flag = "✅" if decision.startswith('added') or (SHADOW_MODE and would_add) else ("⚠️" if decision.startswith('blocked_exists') else "⛔")
				print(f"{flag} [{idx}/{len(items)}] {norm} → HRM={h if h is not None else 'NA'} LLM={l if l is not None else 'NA'} KB={kb:.2f} | COMB={comb:.3f} [{decision}]")

	# summary metrics
	dur_ms = (time.time() - start_ts) * 1000.0
	avg = lambda arr: (sum(arr)/len(arr) if arr else 0.0)
	avg_hrm, avg_llm, avg_kb, avg_comb = avg(values_hrm), avg(values_llm), avg(values_kb), avg(values_comb)

	if json_summary:
		out = {
			'processed': count_processed,
			'invalid': count_invalid,
			'added': count_added,
			'duplicates': count_dupes,
			'would_add_shadow': count_shadow_would_add,
			'below_threshold': count_below_threshold,
			'other_block': count_other_block,
			'avg': {'hrm': avg_hrm, 'llm': avg_llm, 'kb': avg_kb, 'combined': avg_comb},
			'duration_ms': dur_ms,
			'log': str(LOG_PATH),
		}
		print(json.dumps(out, ensure_ascii=False, indent=2))
		return

	def bar(val: float, width: int = 20) -> str:
		filled = int(max(0.0, min(1.0, val)) * width)
		return '█' * filled + '░' * (width - filled)

	print("\n============================================================")
	print(f"SUMMARY: shadow={SHADOW_MODE} threshold={MIN_COMBINED} max_auto_adds={MAX_AUTO_ADDS}")
	print(f"Episoden verarbeitet: {len(items)} | Dauer: {dur_ms:.1f} ms")
	print(f"Ergebnisse: added={count_added} dupes={count_dupes} invalid={count_invalid} below_thr={count_below_threshold} shadow_would_add={count_shadow_would_add}")
	print(f"Durchschnittswerte:")
	print(f"  HRM: {avg_hrm:.3f} {bar(avg_hrm)}  | LLM: {avg_llm:.3f} {bar(avg_llm)}")
	print(f"  KB : {avg_kb:.3f} {bar(avg_kb)}  | COMB:{avg_comb:.3f} {bar(avg_comb)}")
	# Top 5 nach Combined
	try:
		preview_sorted = sorted(results_preview, key=lambda x: x.get('combined', 0.0), reverse=True)[:5]
		if preview_sorted:
			print("Top Kandidaten (Combined):")
			for r in preview_sorted:
				print(f"  {r['norm']:<60} {r['combined']:.3f} [{r['decision']}]")
	except Exception:
		pass
	print(f"Log: {LOG_PATH}")
	print("============================================================")


def load_input(path: Optional[str]) -> List[str]:
	if path and Path(path).exists():
		return [line.rstrip('\n') for line in Path(path).read_text(encoding='utf-8', errors='ignore').splitlines()]
	return [
		"IsA(Socrates, Philosopher).",
		"Prevents(ProperNutrition, Deficiencies).",
		"SubfieldOf(Biotechnology, LifeSciences).",
		"HasPart(Computer, CPU).",
	]


def main():
	global SHADOW_MODE, MIN_COMBINED
	parser = argparse.ArgumentParser(description='V6 SAFE BOOST (V5-Style)')
	parser.add_argument('-i', '--input', help='Pfad zu Kandidaten (eine Zeile pro Fact)')
	parser.add_argument('-e', '--episodes', type=int, default=DEFAULT_EPISODES, help='Anzahl Episoden/Fakten (z.B. 20, 40)')
	parser.add_argument('--min', dest='min_combined', type=float, default=MIN_COMBINED, help='Threshold für Combined Score (0..1)')
	parser.add_argument('--auto', action='store_true', help='Auto-Add aktivieren (Shadow-Mode aus)')
	parser.add_argument('--v5', action='store_true', help='V5-ähnliche Ausgabe aktivieren')
	parser.add_argument('--quiet', action='store_true', help='Keine Einzelitems ausgeben (nur Summary)')
	parser.add_argument('--json', dest='json_summary', action='store_true', help='Nur JSON-Summary ausgeben')
	args = parser.parse_args()

	# Overrides aus CLI
	if args.auto:
		SHADOW_MODE = False
	MIN_COMBINED = float(args.min_combined)

	facts = load_input(args.input)
	process_statements(facts, episodes=args.episodes, v5_style=(args.v5 or V5_STYLE_DEFAULT), quiet_items=args.quiet, json_summary=args.json_summary)


if __name__ == '__main__':
	main()
