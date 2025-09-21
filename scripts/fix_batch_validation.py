"""
FIX for Hallucination Prevention Batch Validation
- Problem: Empty results array when using numeric IDs
- Solution: Fix the batch validation to properly map results
"""

def fix_batch_validation_in_adapter():
    """
    The issue is in the hallucination_prevention_adapter.py
    The batch_validate_facts method needs to properly map the results.
    """
    
    # Original problematic code in batch_validate_facts:
    # The service returns ValidationBatch with results, but the adapter
    # doesn't properly convert them
    
    fixed_code = '''
    def batch_validate_facts(self, fact_ids: List[int], level: str = "comprehensive") -> Dict[str, Any]:
        """
        Validiere einen Batch von Fakten
        
        Args:
            fact_ids: Liste von Fakt-IDs
            level: Validierungsstufe
            
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
            
            # FIX: Ensure results are properly populated
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
            
            # Calculate duration properly
            duration = batch.end_time - batch.start_time if batch.end_time and batch.start_time else 0.0
            
            return {
                "batch_id": batch.batch_id,
                "total_facts": len(fact_ids),
                "valid_facts": sum(1 for r in batch.results if r.valid),
                "invalid_facts": sum(1 for r in batch.results if not r.valid),
                "success_rate": batch.success_rate,
                "validation_level": level,
                "results": results,  # Now properly populated
                "duration": duration
            }
            
        except Exception as e:
            logger.error(f"Batch validation failed: {e}")
            return {
                "error": str(e),
                "batch_id": f"error_batch_{int(time.time())}",
                "total_facts": len(fact_ids) if fact_ids else 0,
                "valid_facts": 0,
                "invalid_facts": 0,
                "success_rate": 0.0,
                "validation_level": level,
                "results": [],
                "duration": 0.0
            }
    '''
    
    return fixed_code

# The actual fix needs to be applied to the file
print("Fix for batch validation identified. The issue is that the results array is populated")
print("but the API endpoint might be using the wrong method (batch_validate_facts_from_statements)")
print("instead of batch_validate_facts.")
