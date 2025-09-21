#!/usr/bin/env python3
"""
Monitor the quality of newly generated facts
"""
import requests
import time
import json
from collections import defaultdict

def monitor_generation():
    """Monitor fact generation quality"""
    print("="*60)
    print("FACT GENERATION MONITOR")
    print("="*60)
    
    api_base = "http://127.0.0.1:5002"
    
    # Get initial count
    try:
        response = requests.get(f"{api_base}/api/facts/count")
        initial_count = response.json().get('count', 0)
        print(f"\nStarting count: {initial_count:,} facts")
    except:
        print("API not responding")
        return
    
    # Monitor for 30 seconds
    print("\nMonitoring generation for 30 seconds...")
    print("-"*40)
    
    predicate_counts = defaultdict(int)
    start_time = time.time()
    last_count = initial_count
    
    while time.time() - start_time < 30:
        time.sleep(5)
        
        try:
            # Get current count
            response = requests.get(f"{api_base}/api/facts/count")
            current_count = response.json().get('count', 0)
            
            # Get new facts
            new_facts = current_count - last_count
            
            if new_facts > 0:
                # Sample recent facts
                response = requests.get(f"{api_base}/api/facts?limit=20")
                facts = response.json()
                
                # Analyze predicates
                for fact in facts:
                    statement = fact.get('statement', '')
                    
                    # Extract predicate
                    if ' HasProperty ' in statement:
                        predicate_counts['HasProperty'] += 1
                    elif ' IsA ' in statement:
                        predicate_counts['IsA'] += 1
                    elif ' HasPart ' in statement:
                        predicate_counts['HasPart'] += 1
                    elif ' Causes ' in statement:
                        predicate_counts['Causes'] += 1
                    elif ' Requires ' in statement:
                        predicate_counts['Requires'] += 1
                    elif ' Uses ' in statement:
                        predicate_counts['Uses'] += 1
                    elif ' DependsOn ' in statement:
                        predicate_counts['DependsOn'] += 1
                    elif ' IsTypeOf ' in statement:
                        predicate_counts['IsTypeOf'] += 1
                    else:
                        # Try to find predicate in functional form
                        if '(' in statement:
                            pred = statement.split('(')[0]
                            predicate_counts[pred] += 1
                
                elapsed = time.time() - start_time
                rate = (current_count - initial_count) / (elapsed / 60)
                
                print(f"Time: {elapsed:.0f}s | Facts: {current_count:,} (+{new_facts}) | Rate: {rate:.1f}/min")
                
                last_count = current_count
                
        except Exception as e:
            print(f"Error: {e}")
    
    # Final analysis
    print("-"*40)
    total_new = current_count - initial_count
    print(f"\n📊 Generation Summary:")
    print(f"  Total new facts: {total_new}")
    print(f"  Rate: {total_new/0.5:.1f} facts/min")
    
    if predicate_counts:
        print(f"\n📈 Predicate Distribution (sample):")
        total_sampled = sum(predicate_counts.values())
        for pred, count in sorted(predicate_counts.items(), key=lambda x: -x[1])[:10]:
            pct = (count / total_sampled) * 100
            bar = '█' * int(pct/5)
            print(f"  {pred:20s}: {bar:20s} {pct:.1f}%")
        
        # Check HasProperty percentage
        has_prop_pct = (predicate_counts.get('HasProperty', 0) / total_sampled) * 100 if total_sampled > 0 else 0
        
        print(f"\n🎯 HasProperty Check:")
        if has_prop_pct <= 25:
            print(f"  ✅ {has_prop_pct:.1f}% - OPTIMIZED (target: ≤20%)")
        else:
            print(f"  ⚠️  {has_prop_pct:.1f}% - Still high (target: ≤20%)")
            print(f"     Old generator may still be running")
    
    print("="*60)

if __name__ == "__main__":
    monitor_generation()
