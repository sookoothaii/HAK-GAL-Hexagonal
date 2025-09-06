"""
Auto-Add Feature Extension for HAK-GAL API
===========================================
Adds automatic fact addition from LLM responses
"""

from flask import Blueprint, jsonify, request
import requests
from typing import List, Dict
import re
from datetime import datetime

auto_add_bp = Blueprint('auto_add', __name__)

class FactValidator:
    """Validates facts before adding to KB"""
    
    @staticmethod
    def validate(fact: str) -> tuple:
        """Returns (is_valid, reason)"""
        # Format check
        pattern = r'^[A-Za-z][A-Za-z0-9_]*\([^,\)]+,\s*[^\)]+\)\.$'
        if not re.match(pattern, fact):
            return False, "Invalid format"
        
        # Exclude test patterns
        exclude = ['Test', 'Example', 'TODO', 'Foo', 'Bar', 'Entity1', 'Entity2']
        for term in exclude:
            if term in fact:
                return False, f"Test term: {term}"
        
        # Length checks
        parts = fact.split('(')
        if len(parts) != 2:
            return False, "Malformed"
            
        predicate = parts[0]
        if len(predicate) < 3:
            return False, "Predicate too short"
            
        entities = parts[1].rstrip(').').split(',')
        if len(entities) != 2:
            return False, "Need 2 entities"
            
        for entity in entities:
            entity = entity.strip()
            if len(entity) < 2 or len(entity) > 50:
                return False, f"Invalid entity length"
        
        return True, "Valid"

def register_auto_add_routes(app, fact_service):
    """Register auto-add routes with the main app"""
    
    @app.route('/api/llm/auto-add', methods=['POST'])
    def auto_add_facts():
        """
        Automatically add LLM-generated facts to KB
        
        Request body:
        {
            "suggested_facts": [...],
            "confidence_threshold": 0.7,
            "source": "Ollama/Phi3",
            "validate": true,
            "check_duplicates": true
        }
        """
        data = request.get_json() or {}
        facts = data.get('suggested_facts', [])
        threshold = data.get('confidence_threshold', 0.7)
        source = data.get('source', 'LLM')
        validate = data.get('validate', True)
        check_dupes = data.get('check_duplicates', True)
        
        if not facts:
            return jsonify({'error': 'No facts provided'}), 400
        
        results = {
            'added': [],
            'rejected': [],
            'duplicates': [],
            'errors': []
        }
        
        for fact_item in facts:
            # Extract fact and confidence
            if isinstance(fact_item, dict):
                fact = fact_item.get('statement', '')
                confidence = fact_item.get('confidence', 0.5)
            else:
                fact = str(fact_item)
                confidence = threshold
            
            fact = fact.strip()
            
            # Skip if below threshold
            if confidence < threshold:
                results['rejected'].append({
                    'fact': fact,
                    'reason': f'Low confidence: {confidence:.1%}'
                })
                continue
            
            # Validate if requested
            if validate:
                is_valid, reason = FactValidator.validate(fact)
                if not is_valid:
                    results['rejected'].append({
                        'fact': fact,
                        'reason': reason
                    })
                    continue
            
            # Check duplicate if requested
            if check_dupes:
                # Use the fact_service to check
                existing = fact_service.search_facts(fact)
                if existing and any(f.statement == fact for f in existing):
                    results['duplicates'].append(fact)
                    continue
            
            # Add to KB
            try:
                success, message = fact_service.add_fact(
                    fact,
                    context={
                        'source': source,
                        'confidence': confidence,
                        'auto_added': True,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
                if success:
                    results['added'].append(fact)
                else:
                    results['rejected'].append({
                        'fact': fact,
                        'reason': message
                    })
                    
            except Exception as e:
                results['errors'].append({
                    'fact': fact,
                    'error': str(e)
                })
        
        # Summary
        summary = {
            'total_processed': len(facts),
            'added_count': len(results['added']),
            'rejected_count': len(results['rejected']),
            'duplicate_count': len(results['duplicates']),
            'error_count': len(results['errors']),
            'results': results
        }
        
        status_code = 200 if results['added'] else 207  # 207 = Multi-Status
        return jsonify(summary), status_code
    
    @app.route('/api/llm/suggest-and-add', methods=['POST'])
    def suggest_and_add():
        """
        Combined endpoint: Get LLM suggestions and optionally auto-add them
        
        Request body:
        {
            "topic": "...",
            "context_facts": [...],
            "auto_add": true,
            "confidence_threshold": 0.7
        }
        """
        data = request.get_json() or {}
        topic = data.get('topic', '')
        context_facts = data.get('context_facts', [])
        auto_add = data.get('auto_add', False)
        threshold = data.get('confidence_threshold', 0.7)
        
        if not topic:
            return jsonify({'error': 'No topic provided'}), 400
        
        # Step 1: Get LLM explanation
        try:
            # Call the existing LLM endpoint internally
            prompt = (
                f"Query: {topic}\n\n"
                f"Context facts:\n{chr(10).join(context_facts) if context_facts else 'None'}\n\n"
                "Please provide a deep explanation and suggest logical facts. "
                "Format facts as: Predicate(Entity1, Entity2)."
            )
            
            # Import the LLM provider based on configuration
            from adapters.ollama_adapter import OllamaProvider
            llm = OllamaProvider(model="phi3")
            
            if not llm.is_available():
                return jsonify({'error': 'LLM not available'}), 503
            
            explanation = llm.generate_response(prompt)
            
            # Extract facts
            try:
                from adapters.fact_extractor_refined import extract_facts_from_llm
            except ImportError:
                try:
                    from adapters.fact_extractor_optimized import extract_facts_from_llm
                except ImportError:
                    from adapters.fact_extractor import extract_facts_from_llm
            
            suggested_facts = extract_facts_from_llm(explanation, topic)
            
            response = {
                'explanation': explanation,
                'suggested_facts': suggested_facts,
                'fact_count': len(suggested_facts)
            }
            
            # Step 2: Auto-add if requested
            if auto_add and suggested_facts:
                # Prepare facts with confidence
                facts_with_confidence = [
                    {'statement': fact, 'confidence': 0.7}
                    for fact in suggested_facts
                ]
                
                # Call auto-add internally
                add_results = {
                    'added': [],
                    'rejected': [],
                    'duplicates': []
                }
                
                for fact_item in facts_with_confidence:
                    fact = fact_item['statement']
                    
                    # Validate
                    is_valid, reason = FactValidator.validate(fact)
                    if not is_valid:
                        add_results['rejected'].append({
                            'fact': fact,
                            'reason': reason
                        })
                        continue
                    
                    # Add to KB
                    try:
                        success, message = fact_service.add_fact(
                            fact,
                            context={
                                'source': f'Auto-added from query: {topic}',
                                'confidence': fact_item['confidence'],
                                'timestamp': datetime.now().isoformat()
                            }
                        )
                        
                        if success:
                            add_results['added'].append(fact)
                        elif 'exists' in str(message).lower():
                            add_results['duplicates'].append(fact)
                        else:
                            add_results['rejected'].append({
                                'fact': fact,
                                'reason': message
                            })
                    except Exception as e:
                        add_results['rejected'].append({
                            'fact': fact,
                            'reason': str(e)
                        })
                
                response['auto_add_results'] = add_results
                response['facts_added'] = len(add_results['added'])
            
            return jsonify(response)
            
        except Exception as e:
            return jsonify({
                'error': f'Processing failed: {str(e)}'
            }), 500
    
    return app

# Export for use in main API
__all__ = ['register_auto_add_routes', 'FactValidator']
