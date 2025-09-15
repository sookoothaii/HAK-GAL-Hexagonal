---
title: "Hak Gal Engines Governance Complex Facts Analysis 2025-09-27"
created: "2025-09-15T00:08:00.994662Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# HAK/GAL Engines + Governor + KB Complex Facts — Analysis & Upgrade Plan

**Timestamp (UTC):** 2025-09-09T19:05:00Z
**Plan\_ID:** engines\_governance\_db\_upgrade\_fa93c7

---

## 1) Context & Scope

* Analyse von **Aethelred** (Fact Generation) und **Thesis** (Meta-Analysis) Engines.
* Prüfung: KB unterstützt **komplexe Fakten** (mehrere Argumente, Formeln, JSON).
* Integration: **Governance (PolicyGuard + AuditLogger)** als Write-Gate.
* Ziel: Qualität, Sicherheit, Auditierbarkeit und Erweiterbarkeit.

---

## 2) Key Findings

* **KB `complex_facts`**: unterstützt komplexe Argumentlisten, Formeln, JSON.
  Beispiele:

  * `CalculatesVelocity(Physics, Distance, Time, "v = d/t")`
  * `FinancialRiskModel(Portfolio, AssetClass, Volatility, TimeHorizon, "VaR = μ - σ * Φ⁻¹(α)", 0.95)`
  * `MachineLearningPipeline(..., {"epochs":100,"batch_size":32})`
* Faktenzahl: ca. 6.713 (vorher 6.631), DB \~7.4 MB.
* **Aethelred**: aktuell keine Governance, zufällige Themen, einfache Extraktion.
* **Thesis**: gute Pattern-Erkennung, aber keine Konfliktprüfung, teils redundante Meta-Fakten.
* **Governance**: PolicyGuard + AuditLogger vorhanden, aber Engines **nutzen sie noch nicht**.

---

## 3) DB Schema – `complex_facts`

Wichtige Spalten: `id`, `statement`, `predicate`, `arg_count`, `arg1..arg5`, `args_json`, `fact_type`, `domain`, `complexity`, `confidence`, `created_at`, `source`.
➡ Ermöglicht hybride Speicherung: klassische FOL-Fakten + komplexe Strukturen.

---

## 4) Governance Integration (Write-Gate)

Minimaler Ansatz: **Mixin** zwischen Engine und DB.

```python
class GovernedEngineMixin:
    def _init_governance(self):
        self._policy = PolicyGuard()
        self._audit = AuditLogger()

    def governed_add_facts(self, facts, context):
        decision = self._policy.check(
            action=f"{self.name}.add_facts",
            context=context,
            externally_legal=True,
            sensitivity="write"
        )
        self._audit.log(event=f"{self.name}.policy_check",
                        payload={"decision": decision, "context": context})
        if self._policy.should_block(decision, sensitivity="write"):
            self.logger.warning(f"{self.name}: blocked by PolicyGuard")
            return 0
        added = self.add_facts_batch(facts)
        self._audit.log(event=f"{self.name}.facts_added",
                        payload={"count": added, "facts_sample": facts[:5]})
        return added
```

**Kontextfelder (Beispiel):**

```json
{
  "engine": "Aethelred",
  "batch_size": 24,
  "predicates_set": ["IsA","DependsOn","CalculatesVelocity"],
  "max_arg_count": 6,
  "has_json_args": true,
  "has_formula": true
}
```

---

## 5) Aethelred — Verbesserungsplan

1. Governance-Gate einbauen.
2. Provenienz speichern (`source_id`, `topic`, `agent`).
3. Extraktion robuster machen (Negationen, Satz-Parser, Deduplikation).
4. Topics nach **Score** statt Zufall wählen.
5. Rate-Limits & Cache.
6. Strikte Validierung: Predicate-Whitelist, Argument-Caps, Meta-Facts optional.

---

## 6) Thesis — Verbesserungsplan

1. Governance-Gate einbauen.
2. Meta-Fakten nur idempotent emittieren.
3. Graph-Heuristiken erweitern (common neighbor ≥ k, cautious IsA).
4. Konfliktprüfung (z. B. `Causes` vs. `Prevents`).
5. Batching + Telemetrie: facts\_generated, blocked\_by\_policy, Latenzen.

---

## 7) Komplexe Fakten – Emission Guidelines

* `arg1..arg5` für Kernargumente, Rest in `args_json`.
* `arg_count` = gesamte Arity.
* `fact_type`, `domain`, `confidence`, `source` verpflichtend setzen.
* Formeln als Klartext (LaTeX erlaubt) in `args_json.formula`.

---

## 8) Tests & KPIs

* **Unit-Tests:** Entity-Canon, Extraktor-Regeln, Validatoren.
* **Integration:** Gate blockiert korrekt in `strict`-Mode.
* **KPIs:** Precision\@k, Policy-Rejects %, Facts/min, Cache-Hit-Rate.

---

## 9) Rolloutplan

* **Phase 1:** Mixin + Gate; Dev `observe`, Stage `strict`.
* **Phase 2:** Neue Extraktoren/Heuristiken hinter Feature-Flags.
* **Phase 3:** Optionale SMT-Prüfung für sensible Predicates.

---

## 10) Next Steps (Checklist)

* [ ] `engine_governance.py` implementieren
* [ ] Aethelred → `governed_add_facts`
* [ ] Thesis → `governed_add_facts`
* [ ] ENV Defaults + Telemetrie
* [ ] Tests hinzufügen
* [ ] Stage-Run mit `strict` für 48h, danach Prod

---

👉 Damit liegt jetzt eine **klare Roadmap** für **Governance-Integration**, **Engine-Verbesserung** und **komplexe Faktennutzung** vor.