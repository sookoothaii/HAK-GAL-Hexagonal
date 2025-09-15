---
title: "Readme Hak Gal V2 2 Machine Policy"
created: "2025-09-15T00:08:01.019297Z"
author: "system-cleanup"
topics: ["guides"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---


# HAK/GAL Constitution v2.2 — Machine-Readable Package

This package contains a JSON specification and an SMT-LIB2 core logic encoding for direct integration.

## Files
- `hak_gal_constitution_v2_2.json` — normative, machine-readable policy
- `hak_gal_constitution_v2_2.smt2` — Z3-compatible formal constraints for admissible actions

## Recommended Integration (Hexagonal Backend, Port 5001)

1. **Load JSON policy once at startup**
   - Validate presence of thresholds and mappings.
   - Expose a `PolicyGuard` service in `application/services.py`.

2. **Enforce checks on decision endpoints**
   - For actions like `/api/command`, `/api/llm/get-explanation`, or engine invocations:
     - Compute `HarmHumanProb` and `SustainIndex` estimates from your risk module.
     - Evaluate Kant precheck via your symbolic engine (mark `Universalizable`).
     - Consult external legality flags (policy knowledge base).

3. **SMT verification (optional but recommended)**
   - Build a small Z3 problem per action:
     - Assert metrics and booleans (`ExternallyLegal`, `Universalizable`).
     - Ask whether `(Allowed a)` can be satisfied.
   - If `unsat`, reject and log per Art. 12.

4. **Override flow**
   - Require operator confirmation, peer review, and documentation IDs.
   - Only proceed if an explicit `RiskExceptionJustified` lemma is provided by your symbolic layer.

5. **Logging & Audit**
   - Persist all decisions in append-only storage with hash-chaining.
   - Include: operator_id, co_operator_id, evidence_refs, risk_assessment_ref.

## Minimal Python snippet (conceptual)

```python
from z3 import *

def check_allowed(legal, universalizable, harm_prob, sustain_index,
                  override=False, peer=False, doc=False, risk_lemma=False):
    A = Const('A', DeclareSort('Action'))  # conceptual placeholder
    s = Solver()

    # Recreate essentials consistent with SMT file (simplified inline form)
    HARM_PROB_MAX = RealVal('0.001')
    SUSTAIN_MIN   = RealVal('0.85')

    Allowed = Function('Allowed', A.sort(), BoolSort())
    ExternallyLegal = Function('ExternallyLegal', A.sort(), BoolSort())
    Universalizable = Function('Universalizable', A.sort(), BoolSort())
    HarmHumanProb   = Function('HarmHumanProb', A.sort(), RealSort())
    SustainIndex    = Function('SustainIndex', A.sort(), RealSort())
    OperatorOverride = Function('OperatorOverride', A.sort(), BoolSort())
    PeerReviewed     = Function('PeerReviewed', A.sort(), BoolSort())
    OverrideDocProvided = Function('OverrideDocProvided', A.sort(), BoolSort())
    RiskExceptionJustified = Function('RiskExceptionJustified', A.sort(), BoolSort())

    a = Const('a', A.sort())

    def PassesDefaultEthic(x):
        return And(Universalizable(x),
                   HarmHumanProb(x) <= HARM_PROB_MAX,
                   SustainIndex(x) >= SUSTAIN_MIN)

    def PassesOverride(x):
        return And(OperatorOverride(x),
                   PeerReviewed(x),
                   OverrideDocProvided(x),
                   RiskExceptionJustified(x))

    s.add(ForAll([a], Implies(Not(ExternallyLegal(a)), Not(Allowed(a)))))
    s.add(ForAll([a], Allowed(a) == And(ExternallyLegal(a),
                                        Or(PassesDefaultEthic(a), PassesOverride(a)))))

    # Bounds
    s.add(ForAll([a], And(HarmHumanProb(a) >= 0, HarmHumanProb(a) <= 1,
                          SustainIndex(a) >= 0, SustainIndex(a) <= 1)))

    # Concrete action
    s.add(ExternallyLegal(a) == legal)
    s.add(Universalizable(a) == universalizable)
    s.add(HarmHumanProb(a) == harm_prob)
    s.add(SustainIndex(a) == sustain_index)
    s.add(OperatorOverride(a) == override)
    s.add(PeerReviewed(a) == peer)
    s.add(OverrideDocProvided(a) == doc)
    s.add(RiskExceptionJustified(a) == risk_lemma)

    s.push()
    s.add(Allowed(a))
    return s.check()  # sat -> allowed, unsat -> forbidden
```

## Notes
- The SMT model is intentionally minimal: it encodes **Art. 9–11** gates precisely.
- `RiskExceptionJustified` is a hook for your symbolic/ethical module to justify an override without hardcoding numeric relaxations.
- External illegality cannot be overridden.
