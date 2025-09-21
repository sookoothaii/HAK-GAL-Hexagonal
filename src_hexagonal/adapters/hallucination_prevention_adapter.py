"""
Hallucination Prevention Adapter
Integriert Halluzinations-Prävention in das bestehende Backend-System
"""

import os
import sys
import json
import time
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from application.hallucination_prevention_service import (
    HallucinationPreventionService, 
    ValidationLevel, 
    ValidationResult,
    ValidationBatch,
    create_hallucination_prevention_service
)

logger = logging.getLogger(__name__)

class HallucinationPreventionAdapter:
    """
    Adapter für die Integration der Halluzinations-Prävention
    in das bestehende Backend-System
    """

    def __init__(self, db_path: str = "hexagonal_kb.db"):
        self.db_path = db_path
        self.service = create_hallucination_prevention_service(db_path)
        self.is_enabled = True
        self.auto_validation_enabled = False
        self.validation_threshold = 0.8  # Minimum confidence for auto-validation
        
        logger.info("Hallucination Prevention Adapter initialized")

    def validate_fact_before_insert(self, fact: str, fact_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Validiere einen Fakt vor dem Einfügen in die Datenbank
        
        Args:
            fact: Der zu validierende Fakt
            fact_id: Optional ID (für Updates)
            
        Returns:
            Dict mit Validierungsergebnis
        """
        if not self.is_enabled:
            return {"valid": True, "reason": "Validation disabled"}

        try:
            # Verwende temporäre ID wenn keine vorhanden
            temp_id = fact_id if fact_id else int(time.time() * 1000)
            
            # Führe umfassende Validierung durch
            result = self.service.validate_fact(fact, temp_id, ValidationLevel.COMPREHENSIVE)
            
            return {
                "valid": result.valid,
                "confidence": result.confidence,
                "issues": result.issues,
                "category": result.category,
                "correction": result.correction,
                "reasoning": result.reasoning,
                "validation_level": result.validation_level.value,
                "timestamp": result.timestamp
            }
            
        except Exception as e:
            logger.error(f"Fact validation failed: {e}")
            return {
                "valid": False,
                "confidence": 0.0,
                "issues": [f"Validation error: {str(e)}"],
                "error": str(e)
            }

    def validate_fact_after_insert(self, fact_id: int) -> Dict[str, Any]:
        """
        Validiere einen Fakt nach dem Einfügen (Post-Validation)
        
        Args:
            fact_id: ID des eingefügten Fakts
            
        Returns:
            Dict mit Validierungsergebnis
        """
        if not self.is_enabled or not self.auto_validation_enabled:
            return {"valid": True, "reason": "Auto-validation disabled"}

        try:
            # Hole Fakt aus Datenbank
            fact = self._get_fact_by_id(fact_id)
            if not fact:
                return {"valid": False, "error": "Fact not found"}

            # Validiere
            result = self.service.validate_fact(fact, fact_id, ValidationLevel.COMPREHENSIVE)
            
            # Bei niedriger Confidence: Flag für Review
            if result.confidence < self.validation_threshold:
                self._flag_for_review(fact_id, result)
            
            return {
                "valid": result.valid,
                "confidence": result.confidence,
                "flagged_for_review": result.confidence < self.validation_threshold,
                "issues": result.issues,
                "category": result.category,
                "correction": result.correction
            }
            
        except Exception as e:
            logger.error(f"Post-insert validation failed: {e}")
            return {"valid": False, "error": str(e)}

    def batch_validate_facts(self, fact_ids: List[int], level: str = "comprehensive") -> Dict[str, Any]:
        """
        Validiere einen Batch von Fakten
        
        Args:
            fact_ids: Liste von Fakt-IDs
            level: Validierungsstufe (structural, scientific, llm_reasoning, quality_check, comprehensive)
            
        Returns:
            Dict mit Batch-Validierungsergebnissen
        """
        if not self.is_enabled:
            return {"valid": True, "reason": "Validation disabled"}

        try:
            # Convert string level to enum
            validation_level = ValidationLevel(level.lower())
            
            # Validate fact_ids parameter
            if not isinstance(fact_ids, list):
                raise ValueError("fact_ids must be a list")
            
            if len(fact_ids) == 0:
                raise ValueError("fact_ids list cannot be empty")
            
            # Führe Batch-Validierung durch
            batch = self.service.validate_batch(fact_ids, validation_level)
            
            # Konvertiere Ergebnisse für API
            results = []
            for result in batch.results:
                results.append({
                    "fact_id": result.fact_id,
                    "fact": result.fact,
                    "valid": result.valid,
                    "confidence": result.confidence,
                    "issues": result.issues,
                    "category": result.category,
                    "correction": result.correction,
                    "reasoning": result.reasoning
                })
            
            return {
                "batch_id": batch.batch_id,
                "total_facts": len(fact_ids),
                "valid_facts": sum(1 for r in batch.results if r.valid),
                "invalid_facts": sum(1 for r in batch.results if not r.valid),
                "success_rate": batch.success_rate,
                "validation_level": level,
                "results": results,
                "duration": batch.end_time - batch.start_time if batch.end_time else None
            }
            
        except Exception as e:
            logger.error(f"Batch validation failed: {e}")
            return {"error": str(e)}

    def batch_validate_facts_from_statements(self, facts: List[Dict], level: str) -> Dict[str, Any]:
        """
        Validiere einen Batch von Fakten aus Statement-Objekten
        
        Args:
            facts: Liste von Fact-Objekten mit 'fact' Property
            level: Validierungslevel
            
        Returns:
            Dict mit Batch-Validierungsergebnis
        """
        if not self.is_enabled:
            return {"valid": True, "reason": "Validation disabled"}

        try:
            # Convert string level to enum
            validation_level = ValidationLevel(level.lower())

            # Extract fact statements from objects
            statements = []
            for fact_obj in facts:
                if isinstance(fact_obj, dict) and 'fact' in fact_obj:
                    statements.append(fact_obj['fact'])
                elif isinstance(fact_obj, str):
                    statements.append(fact_obj)
                else:
                    statements.append(str(fact_obj))

            # Validate each statement
            results = []
            for i, statement in enumerate(statements):
                try:
                    result = self.service.validate_fact(statement, i, validation_level)
                    results.append({
                        "fact": statement,
                        "valid": result.valid,
                        "confidence": result.confidence,
                        "issues": result.issues,
                        "category": result.category,
                        "correction": result.correction,
                        "reasoning": result.reasoning
                    })
                except Exception as e:
                    results.append({
                        "fact": statement,
                        "valid": False,
                        "confidence": 0.0,
                        "issues": [f"Validation error: {str(e)}"],
                        "category": "error",
                        "correction": None,
                        "reasoning": f"Exception during validation: {str(e)}"
                    })

            # Calculate batch statistics
            total_facts = len(results)
            valid_facts = sum(1 for r in results if r['valid'])
            invalid_facts = total_facts - valid_facts
            avg_confidence = sum(r['confidence'] for r in results) / total_facts if total_facts > 0 else 0

            return {
                "batch_result": {
                    "batch_id": f"batch_{int(time.time())}_{total_facts}",
                    "total_facts": total_facts,
                    "valid_facts": valid_facts,
                    "invalid_facts": invalid_facts,
                    "success_rate": valid_facts / total_facts if total_facts > 0 else 0,
                    "avg_confidence": avg_confidence,
                    "duration": 0.0,  # Placeholder
                    "results": results
                },
                "success": True,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Batch validation from statements failed: {e}")
            return {"error": str(e)}

    def get_validation_statistics(self) -> Dict[str, Any]:
        """Hole Validierungsstatistiken"""
        try:
            stats = self.service.get_validation_statistics()
            stats.update({
                "adapter_enabled": self.is_enabled,
                "auto_validation_enabled": self.auto_validation_enabled,
                "validation_threshold": self.validation_threshold,
                "timestamp": datetime.now().isoformat()
            })
            return stats
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"error": str(e)}

    def run_database_quality_analysis(self) -> Dict[str, Any]:
        """Führe Qualitätsanalyse der gesamten Datenbank durch"""
        if not self.is_enabled:
            return {"error": "Validation disabled"}

        try:
            return self.service.run_database_quality_analysis()
        except Exception as e:
            logger.error(f"Database quality analysis failed: {e}")
            return {"error": str(e)}

    def get_invalid_facts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Hole ungültige Fakten"""
        try:
            return self.service.get_invalid_facts(limit)
        except Exception as e:
            logger.error(f"Failed to get invalid facts: {e}")
            return []

    def suggest_corrections(self, fact_id: int) -> Optional[str]:
        """Schlage Korrekturen für einen Fakt vor"""
        try:
            return self.service.suggest_corrections(fact_id)
        except Exception as e:
            logger.error(f"Failed to get corrections: {e}")
            return None

    def enable_validation(self, enabled: bool = True):
        """Aktiviere/Deaktiviere Validierung"""
        self.is_enabled = enabled
        logger.info(f"Validation {'enabled' if enabled else 'disabled'}")

    def enable_auto_validation(self, enabled: bool = True, threshold: float = 0.8):
        """Aktiviere/Deaktiviere automatische Validierung"""
        self.auto_validation_enabled = enabled
        self.validation_threshold = threshold
        logger.info(f"Auto-validation {'enabled' if enabled else 'disabled'} with threshold {threshold}")

    def clear_validation_cache(self):
        """Leere den Validierungs-Cache"""
        self.service.clear_cache()
        logger.info("Validation cache cleared")

    def _get_fact_by_id(self, fact_id: int) -> Optional[str]:
        """Hole einen Fakt aus der Datenbank nach ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT statement FROM facts WHERE rowid = ?", (fact_id,))
            result = cursor.fetchone()
            
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Failed to get fact by ID {fact_id}: {e}")
            return None

    def suggest_correction_from_statement(self, fact_statement: str) -> Dict[str, Any]:
        """
        Schlage Korrektur für einen Fakt basierend auf dem Statement vor
        
        Args:
            fact_statement: Das Fakt-Statement als String
            
        Returns:
            Dict mit Korrekturvorschlag
        """
        if not self.is_enabled:
            return {"success": False, "error": "Service disabled"}

        try:
            # Validiere den Fakt zuerst
            result = self.service.validate_fact(fact_statement, 0, ValidationLevel.COMPREHENSIVE)
            
            # Generiere Korrekturvorschlag basierend auf den Issues
            correction = None
            if not result.valid and result.issues:
                correction = self._generate_correction_suggestion(fact_statement, result.issues)
            
            return {
                "fact": fact_statement,
                "success": True,
                "correction": correction,
                "original_issues": result.issues,
                "confidence": result.confidence,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Suggest correction from statement failed: {e}")
            return {"error": str(e)}

    def _generate_correction_suggestion(self, fact_statement: str, issues: List[str]) -> str:
        """
        Generiere Korrekturvorschlag basierend auf den Issues
        
        Args:
            fact_statement: Originales Statement
            issues: Liste der identifizierten Probleme
            
        Returns:
            Korrigiertes Statement
        """
        correction = fact_statement
        
        # Fix common issues
        for issue in issues:
            if "Missing trailing dot" in issue:
                if not correction.endswith('.'):
                    correction += '.'
            elif "Missing parentheses" in issue:
                # Try to add parentheses for n-ary syntax
                if '(' not in correction and ')' not in correction:
                    parts = correction.split('(')
                    if len(parts) == 2:
                        predicate = parts[0].strip()
                        args = parts[1].rstrip(').').strip()
                        correction = f"{predicate}({args})."
            elif "Unbalancierte Klammern" in issue:
                # Try to fix unbalanced parentheses
                open_count = correction.count('(')
                close_count = correction.count(')')
                if open_count > close_count:
                    correction += ')' * (open_count - close_count)
                elif close_count > open_count:
                    # Remove excess closing parentheses
                    correction = correction.rstrip(')') + ')' * open_count
        
        return correction

    def _flag_for_review(self, fact_id: int, validation_result: ValidationResult):
        """Flagge einen Fakt für Review (könnte in separate Tabelle gespeichert werden)"""
        # Hier könnte eine separate review_queue Tabelle verwendet werden
        logger.info(f"Fact {fact_id} flagged for review (confidence: {validation_result.confidence})")

    def validate_governance_compliance(self, fact: str) -> Dict[str, Any]:
        """
        Validiere Governance-Compliance eines Fakts
        
        Args:
            fact: Der zu validierende Fakt
            
        Returns:
            Dict mit Governance-Compliance-Ergebnis
        """
        if not self.is_enabled:
            return {"compliant": True, "reason": "Validation disabled"}

        try:
            # Grundlegende Governance-Checks
            compliance_issues = []
            
            # Check 1: Keine gefährlichen Inhalte
            dangerous_patterns = ['harm', 'illegal', 'unauthorized', 'malicious']
            if any(pattern in fact.lower() for pattern in dangerous_patterns):
                compliance_issues.append("Contains potentially dangerous content")
            
            # Check 2: Strukturelle Korrektheit
            structural_result = self.service.validate_fact(fact, 0, ValidationLevel.STRUCTURAL)
            if not structural_result.valid:
                compliance_issues.extend(structural_result.issues)
            
            # Check 3: Wissenschaftliche Plausibilität
            scientific_result = self.service.validate_fact(fact, 0, ValidationLevel.SCIENTIFIC)
            if not scientific_result.valid:
                compliance_issues.extend(scientific_result.issues)
            
            compliant = len(compliance_issues) == 0
            
            return {
                "compliant": compliant,
                "issues": compliance_issues,
                "governance_checks_passed": {
                    "structural": structural_result.valid,
                    "scientific": scientific_result.valid,
                    "content_safety": not any(pattern in fact.lower() for pattern in dangerous_patterns)
                },
                "confidence": (structural_result.confidence + scientific_result.confidence) / 2
            }
            
        except Exception as e:
            logger.error(f"Governance compliance validation failed: {e}")
            return {
                "compliant": False,
                "error": str(e),
                "issues": [f"Governance validation error: {str(e)}"]
            }

# Factory function
def create_hallucination_prevention_adapter(db_path: str = "hexagonal_kb.db") -> HallucinationPreventionAdapter:
    """Factory function to create HallucinationPreventionAdapter"""
    return HallucinationPreventionAdapter(db_path)

# Integration with existing governance
def integrate_with_governance(adapter: HallucinationPreventionAdapter, governance_engine) -> None:
    """
    Integriere Halluzinations-Prävention mit bestehender Governance
    
    Args:
        adapter: HallucinationPreventionAdapter instance
        governance_engine: Bestehende Governance-Engine
    """
    try:
        # Hook into governance decision process
        original_validate = governance_engine.validate_decision
        
        def enhanced_validate(decision_data):
            # Original validation
            governance_result = original_validate(decision_data)
            
            # Additional hallucination prevention check
            if hasattr(decision_data, 'fact') and decision_data.fact:
                hallucination_result = adapter.validate_governance_compliance(decision_data.fact)
                
                # Combine results
                if not hallucination_result['compliant']:
                    governance_result['hallucination_issues'] = hallucination_result['issues']
                    governance_result['approved'] = False
                    governance_result['reason'] = "Failed hallucination prevention check"
            
            return governance_result
        
        # Replace method
        governance_engine.validate_decision = enhanced_validate
        logger.info("Hallucination prevention integrated with governance engine")
        
    except Exception as e:
        logger.error(f"Failed to integrate with governance: {e}")

# Example usage
if __name__ == "__main__":
    adapter = create_hallucination_prevention_adapter()
    
    # Test validation
    test_fact = "HasProperty(water, liquid)."
    result = adapter.validate_fact_before_insert(test_fact)
    
    print(f"Validation result: {json.dumps(result, indent=2)}")
    
    # Test governance compliance
    compliance = adapter.validate_governance_compliance(test_fact)
    print(f"Governance compliance: {json.dumps(compliance, indent=2)}")
    
    # Get statistics
    stats = adapter.get_validation_statistics()
    print(f"Statistics: {json.dumps(stats, indent=2)}")
