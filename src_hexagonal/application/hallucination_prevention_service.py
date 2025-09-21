"""
Hallucination Prevention Service
Integriert die 4 Python-Validatoren für umfassende Halluzinations-Prävention
"""

import os
import sys
import json
import time
import sqlite3
import asyncio
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
# Add current directory for relative imports
sys.path.insert(0, str(Path(__file__).parent))

# Import der 4 Validatoren
try:
    from strict_scientific_validator import ScientificFactValidator, create_strict_validation_prompt
    from validate_facts_with_llm import MaximalFactValidator
    from quality_check import analyze_database_quality
    from deepseek_reasoning_validator import validate_with_deepseek_reasoning
except ImportError as e:
    print(f"[WARNING] Validator imports failed: {e}")
    # Fallback für fehlende Imports
    ScientificFactValidator = None
    MaximalFactValidator = None
    analyze_database_quality = None
    validate_with_deepseek_reasoning = None

logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Validierungsstufen"""
    STRUCTURAL = "structural"
    SCIENTIFIC = "scientific"
    LLM_REASONING = "llm_reasoning"
    QUALITY_CHECK = "quality_check"
    COMPREHENSIVE = "comprehensive"

@dataclass
class ValidationResult:
    """Ergebnis einer Validierung"""
    fact_id: int
    fact: str
    valid: bool
    confidence: float
    validation_level: ValidationLevel
    issues: List[str]
    category: str
    correction: Optional[str] = None
    reasoning: Optional[str] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class ValidationBatch:
    """Batch von Validierungen"""
    batch_id: str
    facts: List[Tuple[int, str]]
    validation_level: ValidationLevel
    results: List[ValidationResult]
    start_time: float
    end_time: Optional[float] = None
    success_rate: Optional[float] = None

    def __post_init__(self):
        self.start_time = time.time()

class HallucinationPreventionService:
    """
    Hauptservice für Halluzinations-Prävention
    Integriert alle 4 Validatoren
    """

    def __init__(self, db_path: str = "hexagonal_kb.db"):
        self.db_path = db_path
        self.scientific_validator = None
        self.maximal_validator = None
        
        # Initialize validators if available
        self._initialize_validators()
        
        # Validation cache
        self.validation_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        # Statistics
        self.stats = {
            'total_validated': 0,
            'invalid_found': 0,
            'corrections_suggested': 0,
            'cache_hits': 0,
            'validation_time_avg': 0.0
        }

    def _initialize_validators(self):
        """Initialisiere die Validatoren"""
        try:
            if ScientificFactValidator:
                self.scientific_validator = ScientificFactValidator()
                logger.info("Scientific Fact Validator initialized")
            
            if MaximalFactValidator:
                self.maximal_validator = MaximalFactValidator(self.db_path)
                logger.info("Maximal Fact Validator initialized")
                
        except Exception as e:
            logger.error(f"Validator initialization failed: {e}")

    def validate_fact(self, fact: str, fact_id: int, level: ValidationLevel = ValidationLevel.COMPREHENSIVE) -> ValidationResult:
        """
        Validiere einen einzelnen Fakt
        
        Args:
            fact: Der zu validierende Fakt
            fact_id: ID des Fakts in der Datenbank
            level: Validierungsstufe
            
        Returns:
            ValidationResult
        """
        # Cache check - use fact content as key for better cache hits
        cache_key = f"{hash(fact)}_{level.value}"
        if cache_key in self.validation_cache:
            cached_result = self.validation_cache[cache_key]
            if time.time() - cached_result['timestamp'] < self.cache_ttl:
                self.stats['cache_hits'] += 1
                # Update fact_id for return
                cached_result['result'].fact_id = fact_id
                return cached_result['result']

        start_time = time.time()
        
        try:
            if level == ValidationLevel.STRUCTURAL:
                result = self._validate_structural(fact, fact_id)
            elif level == ValidationLevel.SCIENTIFIC:
                result = self._validate_scientific(fact, fact_id)
            elif level == ValidationLevel.LLM_REASONING:
                result = self._validate_llm_reasoning(fact, fact_id)
            elif level == ValidationLevel.QUALITY_CHECK:
                result = self._validate_quality_check(fact, fact_id)
            elif level == ValidationLevel.COMPREHENSIVE:
                result = self._validate_comprehensive(fact, fact_id)
            else:
                raise ValueError(f"Unknown validation level: {level}")

            # Update statistics
            validation_time = time.time() - start_time
            self.stats['total_validated'] += 1
            if not result.valid:
                self.stats['invalid_found'] += 1
            if result.correction:
                self.stats['corrections_suggested'] += 1
            
            # Update average validation time
            self.stats['validation_time_avg'] = (
                (self.stats['validation_time_avg'] * (self.stats['total_validated'] - 1) + validation_time) 
                / self.stats['total_validated']
            )

            # Cache result
            self.validation_cache[cache_key] = {
                'result': result,
                'timestamp': time.time()
            }

            return result

        except Exception as e:
            logger.error(f"Validation failed for fact {fact_id}: {e}")
            return ValidationResult(
                fact_id=fact_id,
                fact=fact,
                valid=False,
                confidence=0.0,
                validation_level=level,
                issues=[f"Validation error: {str(e)}"],
                category="error"
            )

    def _validate_structural(self, fact: str, fact_id: int) -> ValidationResult:
        """Strukturelle Validierung für HAK_GAL n-äre Syntax"""
        issues = []
        valid = True
        confidence = 1.0
        
        # Basic structure checks
        if not fact.strip():
            issues.append("Empty fact")
            valid = False
            confidence = 0.0
        
        # Determine predicate type early
        predicate_type = self._determine_predicate_type(fact)
        
        # HAK_GAL n-äre Syntax: Predicate(arg1, arg2, ...).
        # Prüfe auf korrekte Struktur
        if not fact.endswith('.'):
            issues.append("Missing trailing dot")
            confidence *= 0.9
        
        # Prüfe auf Klammern (für n-äre Syntax erforderlich)
        if not '(' in fact or not ')' in fact:
            issues.append("Missing parentheses for n-ary syntax")
            valid = False
            confidence = 0.0
        
        # Prüfe auf ausbalancierte Klammern
        if fact.count('(') != fact.count(')'):
            issues.append("Unbalanced parentheses")
            valid = False
            confidence = 0.0
        
        # Prüfe auf HAK_GAL n-äre Syntax: Predicate(args)
        if valid and '(' in fact and ')' in fact:
            # Extrahiere Predicate und Args
            try:
                # Finde erste Klammer
                paren_start = fact.find('(')
                predicate = fact[:paren_start].strip()
                args_part = fact[paren_start+1:fact.rfind(')')]
                
                # Prüfe Predicate
                if not predicate or not predicate.replace('_', '').replace('-', '').isalnum():
                    issues.append("Invalid predicate format")
                    confidence *= 0.8
                
                # Prüfe Args (können leer sein für 0-stellige Prädikate)
                if args_part.strip():
                    # Args sind durch Kommas getrennt
                    args = [arg.strip() for arg in args_part.split(',')]
                    
                    # Spezielle Prüfung für HasProperty (muss genau 2 Args haben)
                    if predicate_type == "HasProperty" and len(args) != 2:
                        issues.append(f"HasProperty requires exactly 2 arguments, found {len(args)}")
                        confidence *= 0.5
                    
                    if len(args) > 7:  # Max 7 Args für HAK_GAL
                        issues.append(f"{len(args)} Argumente (max. 7 erlaubt)")
                        confidence *= 0.7
                
            except Exception as e:
                issues.append(f"Syntax parsing error: {str(e)}")
                confidence *= 0.5

        return ValidationResult(
            fact_id=fact_id,
            fact=fact,
            valid=valid,
            confidence=confidence,
            validation_level=ValidationLevel.STRUCTURAL,
            issues=issues,
            category=predicate_type  # Use predicate type as category
        )

    def _validate_scientific(self, fact: str, fact_id: int) -> ValidationResult:
        """Wissenschaftliche Validierung"""
        if not self.scientific_validator:
            return ValidationResult(
                fact_id=fact_id,
                fact=fact,
                valid=False,
                confidence=0.0,
                validation_level=ValidationLevel.SCIENTIFIC,
                issues=["Scientific validator not available"],
                category="error"
            )

        try:
            # Determine domain
            domain = self._determine_domain(fact)
            
            # Validate with scientific validator
            result = self.scientific_validator.validate_fact(fact, domain)
            
            return ValidationResult(
                fact_id=fact_id,
                fact=fact,
                valid=result['is_valid'],
                confidence=result['confidence'],
                validation_level=ValidationLevel.SCIENTIFIC,
                issues=result['issues'],
                category=domain.lower(),
                correction=result.get('corrected_fact'),
                reasoning=f"Domain: {domain}, Scientific accuracy: {result['scientific_accuracy']}"
            )
        except Exception as e:
            logger.error(f"Scientific validation error: {e}")
            return ValidationResult(
                fact_id=fact_id,
                fact=fact,
                valid=False,
                confidence=0.0,
                validation_level=ValidationLevel.SCIENTIFIC,
                issues=[f"Scientific validation error: {str(e)}"],
                category="error"
            )

    def _validate_llm_reasoning(self, fact: str, fact_id: int) -> ValidationResult:
        """LLM-basierte Reasoning-Validierung"""
        if not validate_with_deepseek_reasoning:
            return ValidationResult(
                fact_id=fact_id,
                fact=fact,
                valid=False,
                confidence=0.0,
                validation_level=ValidationLevel.LLM_REASONING,
                issues=["LLM reasoning validator not available"],
                category="error"
            )

        try:
            # Use DeepSeek reasoning for single fact
            validations = validate_with_deepseek_reasoning([fact])
            
            if validations and len(validations) > 0:
                val = validations[0]
                return ValidationResult(
                    fact_id=fact_id,
                    fact=fact,
                    valid=val.get('valid', True),
                    confidence=val.get('confidence', 0.8),
                    validation_level=ValidationLevel.LLM_REASONING,
                    issues=val.get('issues', []),
                    category=val.get('category', 'general'),
                    correction=val.get('correction'),
                    reasoning=val.get('reasoning')
                )
            else:
                return ValidationResult(
                    fact_id=fact_id,
                    fact=fact,
                    valid=False,
                    confidence=0.0,
                    validation_level=ValidationLevel.LLM_REASONING,
                    issues=["No validation result from LLM"],
                    category="error"
                )
        except Exception as e:
            logger.error(f"LLM reasoning validation error: {e}")
            return ValidationResult(
                fact_id=fact_id,
                fact=fact,
                valid=False,
                confidence=0.0,
                validation_level=ValidationLevel.LLM_REASONING,
                issues=[f"LLM reasoning validation error: {str(e)}"],
                category="error"
            )

    def _validate_quality_check(self, fact: str, fact_id: int) -> ValidationResult:
        """Qualitätscheck-Validierung"""
        issues = []
        valid = True
        confidence = 0.8
        
        # Determine predicate type for specific checks
        predicate_type = self._determine_predicate_type(fact)
        
        # Check for vague terms (especially problematic in HasProperty)
        vague_terms = ['dynamic', 'static', 'complex', 'simple', 'variable', 
                       'optimal', 'critical', 'essential', 'fundamental', 'reactive']
        
        if any(term in fact.lower() for term in vague_terms):
            issues.append("Contains vague/generic terms")
            confidence *= 0.6
            # Extra penalty for HasProperty with vague terms
            if predicate_type == "HasProperty":
                issues.append("HasProperty with vague property - likely auto-generated")
                confidence *= 0.5
        
        # Check for minimal HasProperty facts (too simple)
        if predicate_type == "HasProperty" and '(' in fact and ')' in fact:
            args_part = fact[fact.find('(')+1:fact.rfind(')')]
            args = [arg.strip() for arg in args_part.split(',')]
            if len(args) == 2:  # Basic HasProperty(X, Y)
                # Check if property is too generic
                if len(args) == 2 and len(args[1]) < 4:  # Very short property
                    issues.append("Property term too short/generic")
                    confidence *= 0.7
        
        # Check for known problematic patterns
        problematic_patterns = [
            ('NH3', 'oxygen'),
            ('H2O', 'carbon'),
            ('CO2', 'hydrogen'),
            ('CH4', 'oxygen')
        ]
        
        for pattern1, pattern2 in problematic_patterns:
            if pattern1 in fact and pattern2 in fact:
                issues.append(f"Known problematic pattern: {pattern1} + {pattern2}")
                valid = False
                confidence = 0.1
                break

        return ValidationResult(
            fact_id=fact_id,
            fact=fact,
            valid=valid,
            confidence=confidence,
            validation_level=ValidationLevel.QUALITY_CHECK,
            issues=issues,
            category=predicate_type  # Use predicate type as category
        )

    def _validate_comprehensive(self, fact: str, fact_id: int) -> ValidationResult:
        """Umfassende Validierung (alle Stufen)"""
        # Run all validation levels
        structural = self._validate_structural(fact, fact_id)
        scientific = self._validate_scientific(fact, fact_id)
        quality = self._validate_quality_check(fact, fact_id)
        
        # Combine results
        all_valid = structural.valid and scientific.valid and quality.valid
        avg_confidence = (structural.confidence + scientific.confidence + quality.confidence) / 3
        
        all_issues = []
        all_issues.extend(structural.issues)
        all_issues.extend(scientific.issues)
        all_issues.extend(quality.issues)
        
        # Remove duplicates
        all_issues = list(set(all_issues))
        
        # FIX: Determine predicate type AND domain for proper classification
        predicate_type = self._determine_predicate_type(fact)
        domain = self._determine_domain(fact)
        
        # Primary category should include both predicate type and domain
        if predicate_type != "Other":
            primary_category = f"{predicate_type}_{domain.lower()}"
        else:
            primary_category = domain.lower()
        
        # For simple classification, just use the predicate type
        simple_category = predicate_type

        return ValidationResult(
            fact_id=fact_id,
            fact=fact,
            valid=all_valid,
            confidence=avg_confidence,
            validation_level=ValidationLevel.COMPREHENSIVE,
            issues=all_issues,
            category=simple_category,  # Use predicate type as main category
            correction=scientific.correction,
            reasoning=f"Comprehensive validation: Structural={structural.valid}, Scientific={scientific.valid}, Quality={quality.valid}, Predicate={predicate_type}, Domain={domain}"
        )

    def _determine_predicate_type(self, fact: str) -> str:
        """
        Bestimme den Prädikat-Typ eines Fakts
        
        Returns:
            Prädikat-Typ (HasProperty, ConsistsOf, Uses, etc.)
        """
        fact_stripped = fact.strip()
        
        # Definiere bekannte Prädikate
        predicate_patterns = [
            ('HasProperty(', 'HasProperty'),
            ('ConsistsOf(', 'ConsistsOf'),
            ('Uses(', 'Uses'),
            ('IsTypeOf(', 'IsTypeOf'),
            ('HasPart(', 'HasPart'),
            ('HasPurpose(', 'HasPurpose'),
            ('IsA(', 'IsA'),
            ('Contains(', 'Contains'),
            ('Requires(', 'Requires'),
            ('Supports(', 'Supports'),
            ('DependsOn(', 'DependsOn'),
            ('PartOf(', 'PartOf'),
            ('ConnectedTo(', 'ConnectedTo'),
            ('HasFunction(', 'HasFunction'),
            ('ComposedOf(', 'ComposedOf'),
            ('ProducedBy(', 'ProducedBy'),
            ('UsedBy(', 'UsedBy'),
            ('LocatedIn(', 'LocatedIn'),
            ('RelatedTo(', 'RelatedTo')
        ]
        
        # Prüfe jeden bekannten Prädikat-Typ
        for pattern, predicate_type in predicate_patterns:
            if fact_stripped.startswith(pattern):
                return predicate_type
        
        # Versuche generisches Prädikat zu extrahieren
        if '(' in fact_stripped:
            predicate = fact_stripped.split('(')[0].strip()
            if predicate:
                return predicate
        
        return "Other"

    def _determine_domain(self, fact: str) -> str:
        """Bestimme die Domäne eines Fakts"""
        fact_lower = fact.lower()
        
        chemistry_terms = ['h2o', 'co2', 'nh3', 'molecule', 'atom', 'chemical', 'reaction']
        biology_terms = ['cell', 'dna', 'protein', 'virus', 'organism', 'biological']
        physics_terms = ['electron', 'photon', 'gravity', 'energy', 'force', 'quantum']
        cs_terms = ['algorithm', 'tcp', 'http', 'hash', 'computer', 'software']
        math_terms = ['function', 'matrix', 'equation', 'mathematical', 'calculation']
        
        if any(term in fact_lower for term in chemistry_terms):
            return "CHEMISTRY"
        elif any(term in fact_lower for term in biology_terms):
            return "BIOLOGY"
        elif any(term in fact_lower for term in physics_terms):
            return "PHYSICS"
        elif any(term in fact_lower for term in cs_terms):
            return "COMPUTER_SCIENCE"
        elif any(term in fact_lower for term in math_terms):
            return "MATHEMATICS"
        else:
            return "GENERAL"

    def validate_batch(self, fact_ids: List[int], level: ValidationLevel = ValidationLevel.COMPREHENSIVE) -> ValidationBatch:
        """
        Validiere einen Batch von Fakten
        
        Args:
            fact_ids: Liste von Fakt-IDs
            level: Validierungsstufe
            
        Returns:
            ValidationBatch
        """
        batch_id = f"batch_{int(time.time())}_{len(fact_ids)}"
        
        # Get facts from database
        facts = self._get_facts_by_ids(fact_ids)
        
        batch = ValidationBatch(
            batch_id=batch_id,
            facts=facts,
            validation_level=level,
            results=[],
            start_time=time.time()
        )
        
        # Validate each fact
        for fact_id, fact in facts:
            result = self.validate_fact(fact, fact_id, level)
            batch.results.append(result)
        
        # Calculate batch statistics
        batch.end_time = time.time()
        valid_count = sum(1 for r in batch.results if r.valid)
        batch.success_rate = valid_count / len(batch.results) if batch.results else 0.0
        
        return batch

    def _get_facts_by_ids(self, fact_ids: List[int]) -> List[Tuple[int, str]]:
        """Hole Fakten aus der Datenbank nach IDs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(fact_ids))
        cursor.execute(f"""
            SELECT rowid, statement 
            FROM facts 
            WHERE rowid IN ({placeholders})
            ORDER BY rowid
        """, fact_ids)
        
        facts = cursor.fetchall()
        conn.close()
        
        return facts

    def get_validation_statistics(self) -> Dict[str, Any]:
        """Hole Validierungsstatistiken"""
        # Count predicate types in cache
        predicate_counts = {}
        for cache_key, cached_data in self.validation_cache.items():
            result = cached_data['result']
            if result.category and result.category != 'error':
                predicate_counts[result.category] = predicate_counts.get(result.category, 0) + 1
        
        return {
            'stats': self.stats.copy(),
            'cache_size': len(self.validation_cache),
            'predicate_distribution': predicate_counts,
            'validators_available': {
                'scientific': self.scientific_validator is not None,
                'maximal': self.maximal_validator is not None,
                'quality_check': analyze_database_quality is not None,
                'llm_reasoning': validate_with_deepseek_reasoning is not None
            },
            'validation_threshold': 0.8,
            'auto_validation_enabled': False
        }

    def clear_cache(self):
        """Leere den Validierungs-Cache"""
        self.validation_cache.clear()
        logger.info("Validation cache cleared")

    def run_database_quality_analysis(self) -> Dict[str, Any]:
        """Führe Qualitätsanalyse der gesamten Datenbank durch"""
        if not analyze_database_quality:
            return {
                "success": False,
                "error": "Quality analysis not available",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            result = analyze_database_quality()
            return {
                "success": True,
                "analysis": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Database quality analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_invalid_facts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Hole ungültige Fakten aus der Datenbank"""
        # This would typically query a validation_results table
        # For now, return empty list
        return []

    def suggest_corrections(self, fact_id: int) -> Optional[str]:
        """Schlage Korrekturen für einen Fakt vor"""
        # Check cache for previous validation
        for cache_key, cached_data in self.validation_cache.items():
            if str(fact_id) in cache_key:
                result = cached_data['result']
                return result.correction
        
        return None

# Factory function
def create_hallucination_prevention_service(db_path: str = "hexagonal_kb.db") -> HallucinationPreventionService:
    """Factory function to create HallucinationPreventionService"""
    return HallucinationPreventionService(db_path)

# Example usage
if __name__ == "__main__":
    service = create_hallucination_prevention_service()
    
    # Test with sample fact
    test_fact = "HasProperty(water, liquid)."
    result = service.validate_fact(test_fact, 1, ValidationLevel.COMPREHENSIVE)
    
    print(f"Fact: {result.fact}")
    print(f"Valid: {result.valid}")
    print(f"Confidence: {result.confidence}")
    print(f"Issues: {result.issues}")
    print(f"Category: {result.category}")
    
    # Get statistics
    stats = service.get_validation_statistics()
    print(f"\nStatistics: {stats}")
