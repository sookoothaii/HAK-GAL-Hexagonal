"""
Pragmatic Governance v3.0 - Production Ready
Author: HAK/GAL Team  
Date: 2025-09-10
"""

import os
import json
import logging
import hashlib
import time
from typing import Dict, Any, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk levels based on empirical testing"""
    MINIMAL = 0.001   # Read-only operations
    LOW = 0.01        # Simple additions
    MEDIUM = 0.05     # Modifications
    HIGH = 0.10       # Deletions
    CRITICAL = 0.50   # System changes
    

class OperationType(Enum):
    """Categorized operation types"""
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    SYSTEM = "system"


@dataclass
class GovernanceDecision:
    """Structured governance decision"""
    allowed: bool
    risk_score: float
    confidence: float
    reasons: list
    recommendations: list
    bypass_available: bool
    

class PragmaticGovernance:
    """
    Redesigned governance with:
    - Context-aware risk assessment
    - Graduated responses
    - Clear bypass mechanisms
    - Empirical thresholds
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.bypass_enabled = False
        self.metrics_cache = {}
        
        # Empirically determined thresholds
        self.thresholds = {
            'risk_max': {
                'default': 0.05,      # 5% risk acceptable for most ops
                'trusted': 0.10,      # 10% for trusted sources
                'admin': 0.20,        # 20% for admin operations
                'emergency': 0.50     # 50% in emergency mode
            },
            'confidence_min': 0.60    # 60% confidence required
        }
        
        # Operation risk mapping (based on empirical data)
        self.operation_risks = {
            'read': RiskLevel.MINIMAL,
            'list': RiskLevel.MINIMAL,
            'search': RiskLevel.MINIMAL,
            'add_facts': RiskLevel.LOW,
            'add': RiskLevel.LOW,
            'create': RiskLevel.LOW,
            'update': RiskLevel.MEDIUM,
            'delete': RiskLevel.HIGH,
            'execute': RiskLevel.HIGH,
            'bulk': RiskLevel.HIGH,
            'system': RiskLevel.CRITICAL
        }
        
        logger.info(f"PragmaticGovernance v3 initialized - mode: {self.config['mode']}")
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration with sensible defaults"""
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")
        
        return {
            'mode': 'balanced',  # balanced, strict, permissive
            'bypass_key': 'GOVERNANCE_BYPASS',
            'audit_enabled': True
        }
        
    def classify_operation(self, action: str) -> OperationType:
        """Classify operation type from action string"""
        action_lower = action.lower()
        
        if any(x in action_lower for x in ['read', 'get', 'list', 'search', 'query']):
            return OperationType.READ
        elif any(x in action_lower for x in ['add', 'create', 'insert']):
            return OperationType.CREATE
        elif any(x in action_lower for x in ['update', 'modify', 'edit']):
            return OperationType.UPDATE
        elif any(x in action_lower for x in ['delete', 'remove', 'clear']):
            return OperationType.DELETE
        elif any(x in action_lower for x in ['execute', 'run', 'eval']):
            return OperationType.EXECUTE
        elif any(x in action_lower for x in ['system', 'config', 'admin']):
            return OperationType.SYSTEM
        else:
            return OperationType.UPDATE  # Default to medium risk
            
    def assess_risk(self, action: str, context: Dict[str, Any]) -> Tuple[float, float]:
        """
        Assess risk based on operation type and context
        Returns: (risk_score, confidence)
        """
        op_type = self.classify_operation(action)
        
        # Base risk from operation type
        action_key = action.split('_')[0].lower()
        if action_key in self.operation_risks:
            base_risk = self.operation_risks[action_key].value
        else:
            base_risk = RiskLevel.MEDIUM.value
        
        # Context modifiers
        risk_multiplier = 1.0
        confidence = 0.8  # Base confidence
        
        # Trusted source reduces risk
        if context.get('source') == 'trusted_system':
            risk_multiplier *= 0.5
            confidence += 0.1
            
        # Admin context reduces perceived risk
        if context.get('user_role') == 'admin':
            risk_multiplier *= 0.7
            confidence += 0.05
            
        # Bulk operations increase risk
        if context.get('bulk_operation'):
            risk_multiplier *= 1.5
            confidence -= 0.1
            
        # Emergency mode
        if context.get('emergency_mode'):
            risk_multiplier *= 0.3  # More permissive in emergency
            confidence -= 0.2
            
        final_risk = min(base_risk * risk_multiplier, 1.0)
        final_confidence = max(min(confidence, 1.0), 0.0)
        
        return final_risk, final_confidence
        
    def evaluate_universalizability(self, action: str, context: Dict[str, Any]) -> float:
        """
        Graduated universalizability score (0.0 - 1.0)
        Not binary anymore!
        """
        op_type = self.classify_operation(action)
        
        # Base scores by operation type
        base_scores = {
            OperationType.READ: 1.0,      # Always universalizable
            OperationType.CREATE: 0.8,    # Usually fine
            OperationType.UPDATE: 0.6,    # Context-dependent
            OperationType.DELETE: 0.4,    # Rarely universalizable
            OperationType.EXECUTE: 0.3,   # Dangerous if universal
            OperationType.SYSTEM: 0.1     # Almost never universal
        }
        
        score = base_scores.get(op_type, 0.5)
        
        # Context adjustments
        if context.get('reversible'):
            score += 0.2
        if context.get('idempotent'):
            score += 0.1
        if context.get('validated'):
            score += 0.1
            
        return min(score, 1.0)
        
    def check_bypass(self, context: Dict[str, Any]) -> bool:
        """Check if bypass is requested and valid"""
        
        # Environmental bypass (for testing/emergency)
        if os.environ.get(self.config['bypass_key'], '').lower() == 'true':
            logger.warning("GOVERNANCE BYPASS ACTIVE (environment)")
            return True
            
        # Context bypass with proper authorization
        if context.get('bypass_governance'):
            if context.get('bypass_authorization'):
                logger.warning(f"GOVERNANCE BYPASS ACTIVE (authorized: {context['bypass_authorization']})")
                return True
            else:
                logger.error("GOVERNANCE BYPASS REQUESTED BUT NOT AUTHORIZED")
                
        return False
        
    def decide(self, action: str, context: Dict[str, Any]) -> GovernanceDecision:
        """
        Main decision function - pragmatic and transparent
        """
        # Check bypass first
        if self.check_bypass(context):
            return GovernanceDecision(
                allowed=True,
                risk_score=0.0,
                confidence=1.0,
                reasons=["Governance bypassed"],
                recommendations=[],
                bypass_available=True
            )
            
        # Assess risk and universalizability
        risk_score, confidence = self.assess_risk(action, context)
        universalizability = self.evaluate_universalizability(action, context)
        
        # Determine threshold based on context
        if context.get('emergency_mode'):
            threshold = self.thresholds['risk_max']['emergency']
        elif context.get('user_role') == 'admin':
            threshold = self.thresholds['risk_max']['admin']
        elif context.get('source') == 'trusted_system':
            threshold = self.thresholds['risk_max']['trusted']
        else:
            threshold = self.thresholds['risk_max']['default']
            
        # Decision logic
        allowed = (
            risk_score <= threshold and 
            confidence >= self.thresholds['confidence_min'] and
            universalizability >= 0.3  # Relaxed from binary check
        )
        
        # Build detailed response
        reasons = []
        recommendations = []
        
        if not allowed:
            if risk_score > threshold:
                reasons.append(f"Risk score {risk_score:.3f} exceeds threshold {threshold:.3f}")
                recommendations.append(f"Consider reducing operation scope or adding safety checks")
            if confidence < self.thresholds['confidence_min']:
                reasons.append(f"Confidence {confidence:.2f} below minimum {self.thresholds['confidence_min']:.2f}")
                recommendations.append("Provide more context or validation")
            if universalizability < 0.3:
                reasons.append(f"Universalizability score {universalizability:.2f} too low")
                recommendations.append("This operation type has limited universal applicability")
        else:
            reasons.append(f"Risk acceptable ({risk_score:.3f} <= {threshold:.3f})")
            reasons.append(f"Confidence sufficient ({confidence:.2f})")
            
        return GovernanceDecision(
            allowed=allowed,
            risk_score=risk_score,
            confidence=confidence,
            reasons=reasons,
            recommendations=recommendations,
            bypass_available=True
        )
        
    def explain_decision(self, decision: GovernanceDecision) -> str:
        """Human-readable explanation of decision"""
        explanation = []
        
        if decision.allowed:
            explanation.append("OPERATION ALLOWED")
        else:
            explanation.append("OPERATION BLOCKED")
            
        explanation.append(f"Risk Score: {decision.risk_score:.3f}")
        explanation.append(f"Confidence: {decision.confidence:.2%}")
        
        if decision.reasons:
            explanation.append("\nReasons:")
            for reason in decision.reasons:
                explanation.append(f"  - {reason}")
                
        if decision.recommendations:
            explanation.append("\nRecommendations:")
            for rec in decision.recommendations:
                explanation.append(f"  -> {rec}")
                
        if decision.bypass_available:
            explanation.append("\nBypass available: Set GOVERNANCE_BYPASS=true or use context bypass")
            
        return "\n".join(explanation)


# Convenience function for backward compatibility
def check_governance(action: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Drop-in replacement for old governance check"""
    gov = PragmaticGovernance()
    decision = gov.decide(action, context)
    
    return {
        'allowed': decision.allowed,
        'risk_score': decision.risk_score,
        'confidence': decision.confidence,
        'reasons': decision.reasons,
        'bypass_available': decision.bypass_available
    }
                