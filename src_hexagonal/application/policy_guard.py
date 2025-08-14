from __future__ import annotations

import json
import os
import time
import hashlib
from typing import Any, Dict, Optional
from pathlib import Path

from .risk_estimator import estimate_harm_prob, estimate_sustain_index
from .universalizability import is_universalizable


class PolicyGuard:
    """
    Lightweight policy guard implementing the core of HAK/GAL constitution v2.2
    with safe default behavior. By default runs in 'observe' mode and never blocks.
    Set env POLICY_ENFORCE=strict to enforce decisions for write operations.
    """

    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[2]
        self.policy_path = self.project_root / 'hak_gal_constitution_v2_2.json'
        self.version = 'unknown'
        self.policy_hash = 'unknown'
        self.thresholds = {
            'harm_prob_max': 0.001,
            'sustain_min': 0.85,
        }
        self._load_policy()
        self.enforce_mode = os.environ.get('POLICY_ENFORCE', 'observe').lower()  # observe|strict

        # Simple in-memory cache: (action_sig_hash) -> decision dict
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _load_policy(self) -> None:
        try:
            if self.policy_path.exists():
                content = self.policy_path.read_bytes()
                doc = json.loads(content.decode('utf-8', errors='ignore'))
                self.version = str(doc.get('version', 'unknown'))
                # thresholds
                harm = doc.get('external_frameworks', {}).get('harm_thresholds', {})
                self.thresholds['harm_prob_max'] = float(harm.get('human_injury_probability_max', 0.001))
                self.thresholds['sustain_min'] = float(harm.get('nature_sustainability_index_min', 0.85))
                self.policy_hash = hashlib.sha256(content).hexdigest()[:12]
        except Exception:
            # Fallback to defaults if policy missing or invalid
            self.version = 'fallback'
            self.policy_hash = 'fallback'

    def _action_sig(self, action: str, context: Dict[str, Any]) -> str:
        raw = json.dumps({'a': action, 'c': context, 'v': self.version}, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    def _allow_default(self, universal: bool, harm: float, sustain: float) -> bool:
        return universal and (harm <= self.thresholds['harm_prob_max']) and (sustain >= self.thresholds['sustain_min'])

    def check(self, action: str, context: Dict[str, Any], *, externally_legal: bool = True,
              sensitivity: str = 'write') -> Dict[str, Any]:
        """
        Returns a decision dict. In 'observe' mode never blocks; in 'strict' mode
        will block write operations if not allowed. Read-only should remain permissive.
        """
        started = time.time()
        sig = self._action_sig(action, context)
        if sig in self._cache:
            decision = dict(self._cache[sig])
            decision['cached'] = True
            return decision

        # Estimate metrics (lightweight heuristics, non-blocking)
        try:
            harm_prob = float(estimate_harm_prob(action, context))
        except Exception:
            harm_prob = 0.0
        try:
            sustain_index = float(estimate_sustain_index(action, context))
        except Exception:
            sustain_index = 1.0

        try:
            universal = bool(is_universalizable(action, context))
        except Exception:
            universal = True

        allowed_default = self._allow_default(universal, harm_prob, sustain_index)

        # Placeholder override components, require explicit proof fields in context
        override = bool(context.get('operator_override')) and bool(context.get('peer_review')) \
                   and bool(context.get('override_doc')) and bool(context.get('risk_exception_justified'))

        allowed = bool(externally_legal and (allowed_default or override))
        gate = 'default' if allowed_default else ('override' if override and allowed else 'deny')

        duration_ms = (time.time() - started) * 1000.0
        decision = {
            'allowed': allowed,
            'gate': gate,
            'reasons': [] if allowed else ['Not allowed by default and no valid override'] if externally_legal else ['External illegality'],
            'metrics': {
                'harm_prob': harm_prob,
                'sustain_index': sustain_index,
                'universalizable': universal,
            },
            'policy_version': self.version,
            'policy_hash': self.policy_hash,
            'decision_id': hashlib.sha1(sig.encode('utf-8')).hexdigest()[:12],
            'duration_ms': duration_ms,
            'enforce_mode': self.enforce_mode,
        }

        # Cache only brief period (in-memory; simple safety)
        self._cache[sig] = decision
        return decision

    def should_block(self, decision: Dict[str, Any], *, sensitivity: str = 'write') -> bool:
        if self.enforce_mode != 'strict':
            return False
        if sensitivity == 'read':
            return False
        return not bool(decision.get('allowed', False))




