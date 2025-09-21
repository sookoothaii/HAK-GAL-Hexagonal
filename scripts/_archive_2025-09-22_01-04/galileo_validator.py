import json
import math
import random
import sys
import hashlib
import uuid
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

try:
	import numpy as np
	import pandas as pd
except Exception:
	np = None
	pd = None


ROOT = Path(__file__).resolve().parent
SCHEMAS_DIR = ROOT / "docs" / "schemas"
GALILEO_DIR = ROOT / "galileo"

try:
	import jsonschema  # type: ignore
except Exception:
	jsonschema = None


@dataclass
class Scores:
	id: int
	statement: str
	novelty: float
	feasibility: float
	cost: float
	time: float
	impact: float
	success_prob: float
	priority: float


def load_archimedes() -> Dict[str, Any]:
	hyp = json.loads((ROOT / "hypotheses.json").read_text(encoding="utf-8"))
	exp = json.loads((ROOT / "experimental_designs.json").read_text(encoding="utf-8"))
	return {"hypotheses": hyp, "designs": exp}


def load_galileo_assets() -> Dict[str, Any]:
	rubrics = {}
	feedback = {}
	schema = None
	try:
		rubrics = json.loads((GALILEO_DIR / "feasibility_risk_rubrics.json").read_text(encoding="utf-8"))
	except Exception:
		pass
	try:
		feedback = json.loads((GALILEO_DIR / "feedback_templates.json").read_text(encoding="utf-8"))
	except Exception:
		pass
	try:
		schema = json.loads((GALILEO_DIR / "validation_report.schema.json").read_text(encoding="utf-8"))
	except Exception:
		schema = None
	return {"rubrics": rubrics, "feedback": feedback, "schema": schema}


def heuristic_cost_time_scores(design_text: str) -> Dict[str, float]:
	text = (design_text or "").lower()
	# sehr einfache Heuristiken als MVP (später ersetzbar durch Claudes Rubriken)
	time_score = 5.0
	cost_score = 5.0
	if "satellite" in text or "100km" in text:
		time_score += 2.0; cost_score += 2.0
	if "liquid helium" in text or "vacuum chamber" in text:
		cost_score += 1.5
	if "atomic clock" in text:
		cost_score += 1.0
	if "gps" in text:
		time_score += 0.5
	# clamp to [1,10]
	time_score = max(1.0, min(10.0, time_score))
	cost_score = max(1.0, min(10.0, cost_score))
	return {"time": time_score, "cost": cost_score}


def heuristic_equipment_skills_risk(protocol: str) -> Dict[str, float]:
	text = (protocol or "").lower()
	equipment = 7.0  # 10=basic, 1=theoretical
	skills = 7.0     # 10=undergrad, 1=nobel
	# rough keyword mapping
	if any(k in text for k in ["bbo", "laser", "optical table", "single-photon"]):
		equipment = min(equipment, 6.0)
		skills = min(skills, 6.0)
	if any(k in text for k in ["cryogenic", "helium", "vacuum", "squid"]):
		equipment = min(equipment, 5.0)
		skills = min(skills, 5.0)
	if any(k in text for k in ["synchrotron", "tokamak", "accelerator"]):
		equipment = min(equipment, 3.0)
		skills = min(skills, 4.0)
	# risk: severity(1-5)*prob(1-5)
	severity = 2
	probability = 2
	if any(k in text for k in ["radiation", "hazard", "injury", "toxic"]):
		severity = max(severity, 3)
	if any(k in text for k in ["cryogenic", "high voltage", "laser"]):
		severity = max(severity, 4)
	if any(k in text for k in ["likely", "frequent", "continuous"]):
		probability = max(probability, 3)
	risk = severity * probability  # 1..25
	return {"equipment": equipment, "skills": skills, "risk": float(risk)}


def simple_success_probability(feasibility: float) -> float:
	# MVP: map feasibility [0..1] to base success prob and add small noise
	base = max(0.0, min(1.0, feasibility))
	return max(0.0, min(1.0, base * 0.9 + 0.05))


def mcda_priority(novelty: float, feasibility: float, cost: float, time: float, impact: float,
				  weights: Dict[str, float]) -> float:
	# Normalize cost/time inverse (niedriger ist besser)
	cost_n = 1.0 - (cost / 10.0)
	time_n = 1.0 - (time / 10.0)
	return (
		weights.get("novelty", 0.3) * novelty +
		weights.get("feasibility", 0.25) * feasibility +
		weights.get("cost", 0.2) * cost_n +
		weights.get("time", 0.15) * time_n +
		weights.get("impact", 0.1) * impact
	)


def build_scores(data: Dict[str, Any], weights: Dict[str, float], seed: int = 1337) -> List[Scores]:
	random.seed(seed)
	scores: List[Scores] = []
	for idx, h in enumerate(data["hypotheses"], start=1):
		statement = h.get("statement", f"hypothesis_{idx}")
		novelty = float(h.get("novelty_score", 0.5))
		feasibility = float(h.get("feasibility_score", 0.5))
		# Find matching design by id
		design = next((d for d in data["designs"] if d.get("hypothesis_id") == f"hypo_{idx}"), None)
		protocol = (design or {}).get("protocol", "")
		ct = heuristic_cost_time_scores(protocol)
		esr = heuristic_equipment_skills_risk(protocol)
		# composite feasibility from rubric weights (scaled to 0..1)
		feas_comp = (0.2 * (ct["time"]/10.0) + 0.3 * (ct["cost"]/10.0) +
					 0.25 * (esr["equipment"]/10.0) + 0.15 * (esr["skills"]/10.0) +
					 0.10 * (1.0 - (esr["risk"]/25.0)))
		feas_norm = max(0.0, min(1.0, 0.5 * feasibility + 0.5 * feas_comp))
		impact = 0.5  # placeholder; can be modeled later
		success = simple_success_probability(feas_norm)
		prio = mcda_priority(novelty, feas_norm, ct["cost"], ct["time"], impact, weights)
		scores.append(Scores(
			id=idx,
			statement=statement,
			novelty=novelty,
			feasibility=feas_norm,
			cost=ct["cost"],
			time=ct["time"],
			impact=impact,
			success_prob=success,
			priority=prio
		))
	return scores


def to_matrix(scores: List[Scores]) -> List[Dict[str, Any]]:
	rows = []
	for s in scores:
		rows.append({
			"id": s.id,
			"hypothesis": s.statement[:120],
			"novelty": round(s.novelty, 2),
			"feasibility": round(s.feasibility, 2),
			"cost": round(s.cost, 2),
			"time": round(s.time, 2),
			"success_prob": round(s.success_prob, 3),
			"priority": round(s.priority, 3)
		})
	return rows


def write_csv(matrix: List[Dict[str, Any]], path: Path) -> None:
	if pd is not None:
		df = pd.DataFrame(matrix)
		df.sort_values(by=["priority"], ascending=False, inplace=True)
		df.to_csv(path, index=False)
	else:
		# simple CSV writer
		cols = list(matrix[0].keys()) if matrix else []
		lines = [",".join(cols)]
		for r in sorted(matrix, key=lambda x: -x["priority"]):
			lines.append(",".join(str(r[c]) for c in cols))
		path.write_text("\n".join(lines), encoding="utf-8")


def write_report(matrix: List[Dict[str, Any]], seed: int, path: Path) -> None:
	matrix_sorted = sorted(matrix, key=lambda x: -x["priority"])
	top3 = [row["id"] for row in matrix_sorted[:3]]
	report = {
		"timestamp": datetime.utcnow().isoformat() + "Z",
		"total_hypotheses": len(matrix),
		"feasible_count": sum(1 for r in matrix if r["feasibility"] >= 0.5),
		"recommended_top_3": top3,
		"total_resources_needed": {},
		"confidence_level": 0.75,
		"assumptions": [
			"Composite feasibility from rubric weights",
			"Impact placeholder 0.5",
			"Success prob from feasibility"
		],
		"confidence_interval": [0.6, 0.85],
		"seed": seed,
		"tool_version": "galileo-mvp-0.2",
		"provenance": [
			"hypotheses.json", "experimental_designs.json",
			"galileo/feasibility_risk_rubrics.json"
		],
		"matrix": matrix_sorted
	}
	path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def sha256_file(p: Path) -> str:
	h = hashlib.sha256()
	with open(p, 'rb') as f:
		for chunk in iter(lambda: f.read(8192), b''):
			h.update(chunk)
	return h.hexdigest()


def build_full_report(matrix: List[Dict[str, Any]], scores: List[Scores], seed: int) -> Dict[str, Any]:
	now = datetime.utcnow()
	rid = f"galileo-{now.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
	# ranks
	ranked = sorted([
		{"rank": i+1, "hypothesis_id": row["id"], "composite_score": row["priority"], "stability": 0.8}
		for i, row in enumerate(sorted(matrix, key=lambda x: -x["priority"]))
	], key=lambda r: r["rank"]) 
	# recommendations
	immediate = [r["id"] for r in matrix if r["priority"] >= 0.75]
	needs = [
		{"hypothesis_id": r["id"], "refinement_type": "improve_feasibility", "specific_issues": ["cost", "time"]}
		for r in matrix if 0.45 <= r["priority"] < 0.75
	]
	notrec = [
		{"hypothesis_id": r["id"], "rejection_reasons": ["low composite score"]}
		for r in matrix if r["priority"] < 0.45
	]
	# scoring details per hypothesis (map into 7 criteria)
	def crit_row(s: Scores) -> Dict[str, Any]:
		# resource efficiency (simple): impact / (1/cost + 1/time)
		denom = (1.0/max(0.1, s.cost)) + (1.0/max(0.1, s.time))
		res_eff = max(0.0, min(1.0, (s.impact / max(0.1, denom))))
		risk_adjusted = max(0.0, min(1.0, s.success_prob * s.impact - 0.05))
		knowledge = 0.5
		accessibility = max(0.0, min(1.0, 1.0 - (s.cost/10.0)))
		ethical = max(0.0, min(1.0, 0.9))
		return {
			"hypothesis_id": s.id,
			"hypothesis_text": s.statement,
			"scores": {
				"novelty": round(s.novelty, 3),
				"feasibility": round(s.feasibility, 3),
				"resource_efficiency": round(res_eff, 3),
				"risk_adjusted_value": round(risk_adjusted, 3),
				"knowledge_advancement": knowledge,
				"validation_accessibility": round(accessibility, 3),
				"ethical_alignment": ethical
			},
			"composite_score": round(next(r["priority"] for r in matrix if r["id"] == s.id), 3),
			"uncertainty_bounds": {"lower": 0.05, "upper": 0.15}
		}

	details = [crit_row(s) for s in scores]

	report = {
		"report_id": rid,
		"timestamp": now.isoformat() + "Z",
		"tool_version": {
			"galileo": "0.2.0",
			"archimedes": "0.1.0",
			"mcp_server": "unknown",
			"agents": {"DeepSeek": "unknown", "Claude": "unknown", "Gemini": "unknown"}
		},
		"assumptions": {
			"resource_assumptions": {"budget_basis": "2025_USD", "location": "EU_West", "institution_type": "university"},
			"capability_assumptions": {"skill_baseline": "graduate", "equipment_access": "standard lab", "collaboration_network": True},
			"environmental_assumptions": {"regulatory_environment": "standard", "ethical_framework": "HAK_GAL", "safety_standards": "lab"},
			"statistical_assumptions": {"distribution_types": {"cost": "lognormal", "time": "lognormal"}, "independence_assumptions": ["cost_time"]}
		},
		"validation_results": {
			"hypotheses_validated": len(scores),
			"scoring_details": details,
			"rankings": ranked,
			"recommendations": {
				"immediate_execution": immediate,
				"needs_refinement": needs,
				"not_recommended": notrec
			}
		},
		"confidence_interval": {"method": "analytical", "level": 0.8, "bounds": {}},
		"seed": {"random_seed": seed, "numpy_seed": seed, "simulation_seeds": [seed]},
		"provenance": {
			"input_files": {
				"hypotheses_source": str(ROOT / "hypotheses.json"),
				"experimental_designs_source": str(ROOT / "experimental_designs.json"),
				"checksums": {
					"hypotheses.json": sha256_file(ROOT / "hypotheses.json"),
					"experimental_designs.json": sha256_file(ROOT / "experimental_designs.json")
				}
			},
			"rubrics_used": {
				"feasibility_rubric_version": "1.0.0",
				"mcda_framework_version": "1.0.0",
				"resource_benchmarks_date": "2025-01-11",
				"custom_modifications": []
			},
			"agents_consulted": [],
			"computation_details": {
				"start_time": now.isoformat() + "Z",
				"end_time": now.isoformat() + "Z",
				"total_duration_seconds": 0.0,
				"platform": {"os": sys.platform, "python_version": sys.version.split()[0]}
			}
		}
	}
	return report


def validate_against_galileo_schema(report: Dict[str, Any]) -> Dict[str, Any]:
	result = {"validated": False, "error": None}
	try:
		schema = json.loads((GALILEO_DIR / "validation_report.schema.json").read_text(encoding="utf-8"))
		if jsonschema is None:
			result["error"] = "jsonschema not installed"
			return result
		jsonschema.validate(instance=report, schema=schema)
		result["validated"] = True
		return result
	except Exception as e:
		result["error"] = str(e)
		return result


def main():
	# Default MCDA weights (aligned with Claude framework)
	weights = {
		"novelty": 0.25,
		"feasibility": 0.20,
		"cost": 0.20,
		"time": 0.15,
		"impact": 0.10
	}
	seed = 1337
	data = load_archimedes()
	assets = load_galileo_assets()
	scores = build_scores(data, weights, seed)
	matrix = to_matrix(scores)
	out_dir = ROOT / "reports"
	out_dir.mkdir(exist_ok=True)
	write_csv(matrix, out_dir / "galileo_decision_matrix.csv")
	write_report(matrix, seed, out_dir / "galileo_validation_report.json")
	# Full report (Claude schema)
	full = build_full_report(matrix, scores, seed)
	full_path = out_dir / "galileo_validation_report_full.json"
	full_path.write_text(json.dumps(full, ensure_ascii=False, indent=2), encoding="utf-8")
	val = validate_against_galileo_schema(full)
	status = "validated" if val.get("validated") else f"validation_error: {val.get('error')}"
	print(f"OK: Galileo artifacts written ({status}).")


if __name__ == "__main__":
	main()
