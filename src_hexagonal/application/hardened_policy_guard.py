"""
Hardened PolicyGuard - No silent failures, strict enforcement
"""

from __future__ import annotations

import json
import os
import time
import hashlib
import logging
from typing import Any, Dict, Optional
from pathlib import Path

from .risk_estimator import estimate_harm_prob, estimate_sustain_index
from .universalizability import is_universalizable
from .kill_switch import KillSwitch

logger = logging.getLogger(__name__)


class HardenedPolicyGuard:
    """
    Hardened policy guard with NO silent failures.
    Implements HAK/GAL constitution v2.2 with strict error handling.
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
        self.kill_switch = KillSwitch()
        
        # Load policy with strict error handling
        if not self._load_policy():
            error_msg = f"Failed to load policy from {self.policy_path}"
            logger.critical(error_msg)
            self.kill_switch.activate(reason=error_msg, severity="CRITICAL")
            raise RuntimeError(error_msg)
        
        self.enforce_mode = os.environ.get('POLICY_ENFORCE', 'strict').lower()
        
        # Validate enforce mode
        if self.enforce_mode not in ['observe', 'strict']:
            logger.warning(f"Invalid POLICY_ENFORCE mode: {self.enforce_mode}, defaulting to strict")
            self.enforce_mode = 'strict'
        
        # Simple in-memory cache
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"HardenedPolicyGuard initialized: version={self.version}, mode={self.enforce_mode}")

    def _load_policy(self) -> bool:
        """Load policy with explicit error handling"""
        try:
            if not self.policy_path.exists():
                logger.error(f"Policy file not found: {self.policy_path}")
                return False
            
            content = self.policy_path.read_bytes()
            
            # Validate JSON
            try:
                doc = json.loads(content.decode('utf-8'))
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in policy file: {e}")
                return False
            
            # Extract version
            self.version = str(doc.get('version', 'unknown'))
            if self.version == 'unknown':
                logger.warning("Policy version not specified")
            
            # Extract thresholds with validation
            harm = doc.get('external_frameworks', {}).get('harm_thresholds', {})
            
            harm_max = harm.get('human_injury_probability_max')
            if harm_max is not None:
                try:
                    self.thresholds['harm_prob_max'] = float(harm_max)
                    if not 0 <= self.thresholds['harm_prob_max'] <= 1:
                        logger.warning(f"Invalid harm_prob_max: {harm_max}, using default")
                        self.thresholds['harm_prob_max'] = 0.001
                except (ValueError, TypeError):
                    logger.warning(f"Invalid harm_prob_max format: {harm_max}")
            
            sustain_min = harm.get('nature_sustainability_index_min')
            if sustain_min is not None:
                try:
                    self.thresholds['sustain_min'] = float(sustain_min)
                    if not 0 <= self.thresholds['sustain_min'] <= 1:
                        logger.warning(f"Invalid sustain_min: {sustain_min}, using default")
                        self.thresholds['sustain_min'] = 0.85
                except (ValueError, TypeError):
                    logger.warning(f"Invalid sustain_min format: {sustain_min}")
            
            # Compute policy hash
            self.policy_hash = hashlib.sha256(content).hexdigest()[:12]
            
            logger.info(f"Policy loaded: v{self.version}, hash={self.policy_hash}")
            return True
            
        except IOError as e:
            logger.error(f"Failed to read policy file: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error loading policy: {e}")
            return False

    def _action_sig(self, action: str, context: Dict[str, Any]) -> str:
        """Generate action signature with error handling"""
        try:
            raw = json.dumps(
                {'a': action, 'c': context, 'v': self.version}, 
                sort_keys=True, 
                ensure_ascii=False
            )
            return hashlib.sha256(raw.encode('utf-8')).hexdigest()
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to generate action signature: {e}")
            # Use a fallback signature
            fallback = f"{action}:{time.time()}:{id(context)}"
            return hashlib.sha256(fallback.encode('utf-8')).hexdigest()

    def _allow_default(self, universal: bool, harm: float, sustain: float) -> bool:
        """Check default allowance with validation"""
        return (
            universal and 
            (0 <= harm <= self.thresholds['harm_prob_max']) and 
            (sustain >= self.thresholds['sustain_min'])
        )

    def check(self, 
              action: str, 
              context: Dict[str, Any], 
              *, 
              externally_legal: bool = True,
              sensitivity: str = 'write') -> Dict[str, Any]:
        """
        Check policy with strict error handling.
        Never fails silently - errors are logged and decisions default to DENY.
        """
        started = time.time()
        
        # Input validation
        if not action:
            logger.error("Empty action provided to policy check")
            return self._deny_decision("Empty action", started)
        
        if not isinstance(context, dict):
            logger.error(f"Invalid context type: {type(context)}")
            return self._deny_decision("Invalid context", started)
        
        # Check cache
        sig = self._action_sig(action, context)
        if sig in self._cache:
            decision = dict(self._cache[sig])
            decision['cached'] = True
            return decision

        # Estimate metrics with explicit error handling
        harm_prob = 0.0
        sustain_index = 1.0
        universal = True
        
        try:
            harm_prob = float(estimate_harm_prob(action, context))
            if not 0 <= harm_prob <= 1:
                logger.warning(f"Invalid harm_prob: {harm_prob}, using 0.0")
                harm_prob = 0.0
        except Exception as e:
            logger.error(f"Failed to estimate harm probability: {e}")
            harm_prob = 0.5  # Conservative default
        
        try:
            sustain_index = float(estimate_sustain_index(action, context))
            if not 0 <= sustain_index <= 1:
                logger.warning(f"Invalid sustain_index: {sustain_index}, using 0.5")
                sustain_index = 0.5
        except Exception as e:
            logger.error(f"Failed to estimate sustain index: {e}")
            sustain_index = 0.5  # Conservative default

        try:
            universal = bool(is_universalizable(action, context))
        except Exception as e:
            logger.error(f"Failed to check universalizability: {e}")
            universal = False  # Conservative default

        # Check default allowance
        allowed_default = self._allow_default(universal, harm_prob, sustain_index)

        # Check override conditions
        override = (
            bool(context.get('operator_override')) and 
            bool(context.get('peer_review')) and
            bool(context.get('override_doc')) and 
            bool(context.get('risk_exception_justified'))
        )

        # Final decision
        allowed = bool(externally_legal and (allowed_default or override))
        
        if allowed_default:
            gate = 'default'
        elif override and allowed:
            gate = 'override'
        else:
            gate = 'deny'

        # Build decision
        duration_ms = (time.time() - started) * 1000.0
        
        reasons = []
        if not allowed:
            if not externally_legal:
                reasons.append('External illegality')
            elif not allowed_default and not override:
                reasons.append('Not allowed by default and no valid override')
                if harm_prob > self.thresholds['harm_prob_max']:
                    reasons.append(f'Harm probability {harm_prob:.4f} exceeds threshold')
                if sustain_index < self.thresholds['sustain_min']:
                    reasons.append(f'Sustain index {sustain_index:.4f} below threshold')
                if not universal:
                    reasons.append('Action not universalizable')
        
        decision = {
            'allowed': allowed,
            'gate': gate,
            'reasons': reasons,
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

        # Cache the decision
        self._cache[sig] = decision
        
        # Log decision if denied in strict mode
        if not allowed and self.enforce_mode == 'strict':
            logger.warning(f"Action denied: {action}, reasons: {reasons}")
        
        return decision
    
    def _deny_decision(self, reason: str, started: float) -> Dict[str, Any]:
        """Create a deny decision for error cases"""
        duration_ms = (time.time() - started) * 1000.0
        return {
            'allowed': False,
            'gate': 'deny',
            'reasons': [f'Policy check error: {reason}'],
            'metrics': {
                'harm_prob': 1.0,  # Conservative
                'sustain_index': 0.0,  # Conservative
                'universalizable': False,
            },
            'policy_version': self.version,
            'policy_hash': self.policy_hash,
            'decision_id': hashlib.sha1(f"error:{time.time()}".encode()).hexdigest()[:12],
            'duration_ms': duration_ms,
            'enforce_mode': self.enforce_mode,
            'error': True
        }

    def should_block(self, decision: Dict[str, Any], *, sensitivity: str = 'write') -> bool:
        """
        Determine if action should be blocked.
        In strict mode, blocks on any deny. Never silently fails.
        """
        if self.enforce_mode != 'strict':
            return False
        
        if sensitivity == 'read':
            return False
        
        # Block if not allowed or if there was an error
        should_block = not bool(decision.get('allowed', False)) or bool(decision.get('error', False))
        
        if should_block:
            logger.info(f"Blocking action: decision_id={decision.get('decision_id')}")
        
        return should_block
