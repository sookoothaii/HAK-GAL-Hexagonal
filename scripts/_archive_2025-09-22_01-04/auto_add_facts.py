#!/usr/bin/env python3
"""
Auto-Add Facts from LLM to Knowledge Base
==========================================
Automatically adds high-confidence facts from LLM responses to the KB
"""

import requests
import json
import time
from typing import List, Dict, Tuple
from datetime import datetime

class FactAutoAdder:
    """Manages automatic addition of LLM-generated facts to Knowledge Base"""
    
    def __init__(self, api_url: str = "http://localhost:5002"):
        self.api_url = api_url
        self.added_facts = []
        self.rejected_facts = []
        self.duplicate_facts = []
        
    def validate_fact(self, fact: str) -> Tuple[bool, str]:
        """
        Validate fact format and quality
        
        Returns:
            (is_valid, reason)
        """
        # Check format
        import re
        pattern = r'^[A-Za-z][A-Za-z0-9_]*\([^,\)]+,\s*[^\)]+\)\.$'
        
        if not re.match(pattern, fact):
            return False, "Invalid format"
        
        # Check for test/example patterns
        exclude_terms = ['Test', 'Example', 'TODO', 'Foo', 'Bar', 'Entity1', 'Entity2']
        for term in exclude_terms:
            if term in fact:
                return False, f"Contains test term: {term}"
        
        # Check minimum quality
        parts = fact.split('(')
        if len(parts) != 2:
            return False, "Malformed predicate"
            
        predicate = parts[0]
        if len(predicate) < 3:
            return False, "Predicate too short"
            
        # Extract entities
        entities_part = parts[1].rstrip(').')
        entities = [e.strip() for e in entities_part.split(',')]
        
        if len(entities) != 2:
            return False, "Must have exactly 2 entities"
            
        for entity in entities:
            if len(entity) < 2:
                return False, f"Entity too short: {entity}"
            if len(entity) > 50:
                return False, f"Entity too long: {entity}"
        
        return True, "Valid"
    
    def check_duplicate(self, fact: str) -> bool:
        """Check if fact already exists in KB"""
        try:
            # Search for exact match
            response = requests.post(
                f"{self.api_url}/api/search",
                json={"query": fact, "limit": 1},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                # Check for exact match
                for result in results:
                    if result.get('statement', '').strip() == fact.strip():
                        return True
                        
            return False
            
        except Exception as e:
            print(f"Error checking duplicate: {e}")
            return False  # Assume not duplicate if check fails
    
    def add_fact(self, fact: str, source: str = "LLM") -> Dict:
        """Add single fact to Knowledge Base"""
        try:
            response = requests.post(
                f"{self.api_url}/api/facts",
                json={
                    "statement": fact,
                    "context": {
                        "source": source,
                        "timestamp": datetime.now().isoformat(),
                        "auto_added": True
                    }
                },
                timeout=10
            )
            
            return {
                "fact": fact,
                "status": response.status_code,
                "success": response.status_code in [200, 201],
                "message": response.json().get('message', '') if response.status_code == 200 else response.text
            }
            
        except Exception as e:
            return {
                "fact": fact,
                "status": 500,
                "success": False,
                "message": str(e)
            }
    
    def process_llm_response(self, llm_response: Dict, confidence_threshold: float = 0.7) -> Dict:
        """
        Process LLM response and add valid facts to KB
        
        Args:
            llm_response: Response from /api/llm/get-explanation
            confidence_threshold: Minimum confidence to add fact
            
        Returns:
            Summary of additions
        """
        facts = llm_response.get('suggested_facts', [])
        
        if not facts:
            return {
                "error": "No facts found in response",
                "added": 0,
                "rejected": 0,
                "duplicates": 0
            }
        
        print(f"\n{'='*60}")
        print(f"Processing {len(facts)} suggested facts")
        print(f"{'='*60}")
        
        for fact in facts:
            # Clean fact string
            if isinstance(fact, dict):
                fact_str = fact.get('statement', '')
                confidence = fact.get('confidence', 0.5)
            else:
                fact_str = str(fact)
                confidence = confidence_threshold  # Default confidence
            
            fact_str = fact_str.strip()
            
            print(f"\n📝 Fact: {fact_str}")
            print(f"   Confidence: {confidence:.1%}")
            
            # Validate
            is_valid, reason = self.validate_fact(fact_str)
            if not is_valid:
                print(f"   ❌ Rejected: {reason}")
                self.rejected_facts.append((fact_str, reason))
                continue
            
            # Check duplicate
            if self.check_duplicate(fact_str):
                print(f"   ⚠️ Duplicate: Already exists")
                self.duplicate_facts.append(fact_str)
                continue
            
            # Check confidence
            if confidence < confidence_threshold:
                print(f"   ❌ Rejected: Low confidence")
                self.rejected_facts.append((fact_str, f"Confidence {confidence:.1%} below threshold"))
                continue
            
            # Add to KB
            result = self.add_fact(fact_str, source=f"Ollama/Phi3 (confidence: {confidence:.1%})")
            
            if result['success']:
                print(f"   ✅ Added successfully")
                self.added_facts.append(fact_str)
            else:
                print(f"   ❌ Failed: {result['message']}")
                self.rejected_facts.append((fact_str, result['message']))
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.1)
        
        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Added: {len(self.added_facts)}")
        print(f"⚠️ Duplicates: {len(self.duplicate_facts)}")
        print(f"❌ Rejected: {len(self.rejected_facts)}")
        
        return {
            "added": len(self.added_facts),
            "rejected": len(self.rejected_facts),
            "duplicates": len(self.duplicate_facts),
            "added_facts": self.added_facts,
            "rejected_facts": self.rejected_facts,
            "duplicate_facts": self.duplicate_facts
        }

def test_with_example():
    """Test with the Socrates example from the screenshot"""
    
    # Example facts from the Socrates query
    example_facts = [
        "Predicate(Plato, Philosopher).",
        "Predicate(Aristotle, Philosopher).",
        "Predicate(Socrates, Athenian).",
        "Predicate(SocraticMethod, Dialectic).",
        "Predicate(Socrates, Mortal).",
        "Predicate(Socrates, Ethicist).",
        "Predicate(SocraticDialogue, Literature).",
        "Predicate(SocraticDialogue, Philosophy).",
        "Predicate(PlatoDionysusDialogue, Philosophy).",
        "IsA(Socrates, Philosopher)."  # This should be duplicate
    ]
    
    # Simulate LLM response
    llm_response = {
        "status": "success",
        "suggested_facts": example_facts
    }
    
    # Process
    adder = FactAutoAdder()
    result = adder.process_llm_response(llm_response, confidence_threshold=0.5)
    
    return result

def auto_add_from_query(query: str, context_facts: List[str] = None) -> Dict:
    """
    Run a query and automatically add the generated facts
    
    Args:
        query: The topic/query to send to LLM
        context_facts: Optional context facts
        
    Returns:
        Summary of the operation
    """
    print(f"\n🤖 Running query: {query}")
    print("="*60)
    
    # Step 1: Get LLM explanation
    try:
        response = requests.post(
            "http://localhost:5002/api/llm/get-explanation",
            json={
                "topic": query,
                "context_facts": context_facts or []
            },
            timeout=30
        )
        
        if response.status_code != 200:
            return {"error": f"LLM request failed: {response.status_code}"}
        
        llm_response = response.json()
        
        # Show explanation
        print("\n📖 LLM Explanation:")
        print("-"*40)
        explanation = llm_response.get('explanation', '')[:500]
        print(explanation + "..." if len(explanation) == 500 else explanation)
        
        # Step 2: Process and add facts
        adder = FactAutoAdder()
        result = adder.process_llm_response(llm_response)
        
        return result
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import sys
    
    print("="*60)
    print("AUTO-ADD FACTS FROM LLM TO KNOWLEDGE BASE")
    print("="*60)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # Run test with example data
            print("\n🧪 Running test with Socrates example...")
            result = test_with_example()
            print(f"\nTest complete: {result}")
        else:
            # Run with custom query
            query = " ".join(sys.argv[1:])
            result = auto_add_from_query(query)
            print(f"\nComplete: {result}")
    else:
        # Interactive mode
        print("\nUsage:")
        print("  python auto_add_facts.py test                    # Test with example")
        print("  python auto_add_facts.py <query>                 # Run query and add facts")
        print("  python auto_add_facts.py 'Ancient Philosophy'    # Example query")
        print("\nEntering interactive mode...")
        
        while True:
            query = input("\n🔍 Enter query (or 'quit'): ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
                
            if query:
                result = auto_add_from_query(query)
                
                if 'error' not in result:
                    print(f"\n✅ Successfully processed!")
                    print(f"   Added: {result.get('added', 0)} facts")
                    print(f"   Rejected: {result.get('rejected', 0)}")
                    print(f"   Duplicates: {result.get('duplicates', 0)}")
