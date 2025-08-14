#!/usr/bin/env python3
"""
Test Intelligent Fact Extraction
=================================
Verifiziert, dass die Fact-Vorschläge jetzt kontextbezogen sind
"""

import requests
import json
import time

API_URL = "http://127.0.0.1:5001"

def test_fact_suggestions():
    """Test the improved fact suggestion system"""
    
    print("=" * 60)
    print("TESTING INTELLIGENT FACT EXTRACTION")
    print("=" * 60)
    
    # Test cases with expected relevant suggestions
    test_cases = [
        {
            "query": "IsA(Socrates, Philosopher)",
            "expected_keywords": ["Socrates", "Philosopher", "Greek"],
            "unexpected": ["TestEntity", "ValidType", "TestCategory"]
        },
        {
            "query": "HasPart(Computer, CPU)",
            "expected_keywords": ["Computer", "CPU", "Motherboard", "Component"],
            "unexpected": ["TestEntity", "Socrates", "Philosopher"]
        },
        {
            "query": "Causes(Rain, Wetness)",
            "expected_keywords": ["Rain", "Wetness", "Leads", "Results"],
            "unexpected": ["TestEntity", "Computer", "Socrates"]
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test['query']}")
        print("-" * 40)
        
        try:
            # Call the LLM explanation endpoint
            resp = requests.post(
                f"{API_URL}/api/llm/get-explanation",
                json={
                    "topic": test['query'],
                    "context_facts": []
                },
                timeout=45
            )
            
            if resp.status_code == 200:
                result = resp.json()
                
                if 'suggested_facts' in result:
                    suggestions = result['suggested_facts']
                    print(f"   Got {len(suggestions)} suggestions:")
                    
                    # Check each suggestion
                    relevant_count = 0
                    irrelevant_count = 0
                    
                    for fact in suggestions[:10]:
                        print(f"   - {fact}")
                        
                        # Check if relevant
                        is_relevant = any(
                            keyword in fact 
                            for keyword in test['expected_keywords']
                        )
                        
                        # Check if it's a test fact
                        is_test = any(
                            bad in fact 
                            for bad in test['unexpected']
                        )
                        
                        if is_relevant and not is_test:
                            relevant_count += 1
                        elif is_test:
                            irrelevant_count += 1
                    
                    # Evaluation
                    print(f"\n   Evaluation:")
                    print(f"   - Relevant facts: {relevant_count}/{len(suggestions)}")
                    print(f"   - Test/Irrelevant facts: {irrelevant_count}/{len(suggestions)}")
                    
                    if irrelevant_count == 0:
                        print("   ✅ NO TEST FACTS! Intelligent extraction working!")
                    else:
                        print(f"   ⚠️ Still found {irrelevant_count} test/irrelevant facts")
                    
                    if relevant_count >= len(suggestions) * 0.7:
                        print("   ✅ Most suggestions are relevant!")
                    else:
                        print("   ⚠️ Need more relevant suggestions")
                    
                else:
                    print("   ❌ No suggested_facts in response")
            else:
                print(f"   ❌ API error: {resp.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test the /api/command endpoint as well
    print("\n" + "=" * 60)
    print("4. Testing /api/command endpoint")
    print("-" * 40)
    
    try:
        resp = requests.post(
            f"{API_URL}/api/command",
            json={
                "command": "explain",
                "query": "IsA(Plato, Philosopher)"
            },
            timeout=45
        )
        
        if resp.status_code == 200:
            result = resp.json()
            if 'chatResponse' in result:
                chat = result['chatResponse']
                if 'suggested_facts' in chat:
                    suggestions = chat['suggested_facts']
                    print(f"   Got {len(suggestions)} suggestions via command endpoint:")
                    
                    test_facts = 0
                    for fact in suggestions[:5]:
                        print(f"   - {fact}")
                        if "Test" in fact or "Valid" in fact:
                            test_facts += 1
                    
                    if test_facts == 0:
                        print("   ✅ Command endpoint also using intelligent extraction!")
                    else:
                        print(f"   ⚠️ Found {test_facts} test facts")
        else:
            print(f"   ❌ API error: {resp.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    print("\nMake sure the API is running on port 5001!")
    print("Press Enter to start testing...")
    input()
    
    test_fact_suggestions()
