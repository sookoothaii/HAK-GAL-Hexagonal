"""
HRM Learning Loop Demonstration
Zeigt signifikante Confidence-Steigerung durch wiederholtes Feedback
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5002"
API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# Standard-Test-Query
TEST_QUERY = "IsA(Claude, AI_Assistant)."

print("=" * 80)
print(" HRM LEARNING LOOP - SIGNIFIKANTE CONFIDENCE STEIGERUNG DEMO")
print("=" * 80)
print(f"\nTest Query: {TEST_QUERY}")
print("Ziel: Confidence von ~0% auf 30% steigern durch 20 positive Feedbacks\n")

# Tracking arrays
confidence_history = []
feedback_count = 0

def get_current_confidence(query):
    """Get current confidence for query"""
    response = requests.post(
        f"{BASE_URL}/api/reason",
        headers=headers,
        json={"query": query}
    )
    if response.status_code == 200:
        data = response.json()
        return {
            'confidence': data.get('confidence', 0),
            'base': data.get('base_confidence', 0),
            'adjustment': data.get('adjustment', 0),
            'feedback_count': data.get('feedback_count', 0)
        }
    return None

def give_positive_feedback(query, current_confidence):
    """Submit positive feedback"""
    response = requests.post(
        f"{BASE_URL}/api/hrm/feedback",
        headers=headers,
        json={
            "query": query,
            "type": "positive",
            "confidence": current_confidence
        }
    )
    return response.status_code == 200

# Initial state
print("📊 INITIAL STATE")
print("-" * 40)
initial = get_current_confidence(TEST_QUERY)
if initial:
    print(f"Initial Confidence: {initial['confidence']*100:.2f}%")
    print(f"Base Model: {initial['base']*100:.6f}%")
    print(f"Current Adjustment: {initial['adjustment']*100:.2f}%")
    print(f"Existing Feedbacks: {initial['feedback_count']}")
    confidence_history.append(initial['confidence'])

print("\n" + "=" * 80)
print(" STARTING LEARNING LOOP - 20 ITERATIONS")
print("=" * 80)

# Learning Loop
for i in range(20):
    print(f"\n📚 ITERATION {i+1}/20")
    print("-" * 40)
    
    # Get current state
    current = get_current_confidence(TEST_QUERY)
    if not current:
        print("❌ Failed to get confidence")
        continue
    
    # Give positive feedback
    success = give_positive_feedback(TEST_QUERY, current['confidence'])
    if success:
        feedback_count += 1
        print(f"✅ Positive feedback #{feedback_count} submitted")
    else:
        print("❌ Failed to submit feedback")
        continue
    
    # Wait a moment for processing
    time.sleep(0.1)
    
    # Get updated confidence
    updated = get_current_confidence(TEST_QUERY)
    if updated:
        confidence_history.append(updated['confidence'])
        
        # Calculate improvement
        improvement = updated['confidence'] - current['confidence']
        
        # Display progress bar
        bar_length = 50
        filled = int(bar_length * updated['confidence'] / 0.3)  # Max 30%
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"Before: {current['confidence']*100:6.2f}%")
        print(f"After:  {updated['confidence']*100:6.2f}% (+{improvement*100:.2f}%)")
        print(f"Progress: [{bar}] {updated['confidence']*100:.1f}%")
        
        # Show learning rate trend
        if len(confidence_history) > 1:
            recent_gain = confidence_history[-1] - confidence_history[-2]
            print(f"Learning Rate: {recent_gain*100:.3f}% per feedback")
    
    # Optional: Speed up or slow down based on progress
    if i < 5:
        time.sleep(0.5)  # Slower at start to show effect
    else:
        time.sleep(0.1)  # Faster later

print("\n" + "=" * 80)
print(" FINAL RESULTS")
print("=" * 80)

# Final state
final = get_current_confidence(TEST_QUERY)
if final and initial:
    print(f"\n📈 CONFIDENCE PROGRESSION:")
    print(f"   Start:  {initial['confidence']*100:6.2f}%")
    print(f"   End:    {final['confidence']*100:6.2f}%")
    print(f"   GAIN:   {(final['confidence']-initial['confidence'])*100:+6.2f}%")
    
    print(f"\n📊 LEARNING STATISTICS:")
    print(f"   Total Feedbacks Given: {feedback_count}")
    print(f"   Total in Database: {final['feedback_count']}")
    print(f"   Base Model Output: {final['base']*100:.6f}%")
    print(f"   Learning Adjustment: {final['adjustment']*100:.2f}%")
    print(f"   Average Gain per Feedback: {(final['confidence']-initial['confidence'])/feedback_count*100:.3f}%")
    
    # Visualize progression
    print(f"\n📉 CONFIDENCE CURVE (every 2nd point):")
    max_conf = max(confidence_history) if confidence_history else 0.3
    height = 10
    
    for h in range(height, -1, -1):
        threshold = h / height * max_conf
        line = f"{threshold*100:5.1f}% |"
        for j in range(0, len(confidence_history), 2):  # Every 2nd point
            if confidence_history[j] >= threshold:
                line += "█"
            else:
                line += " "
        print(line)
    
    print("       └" + "─" * (len(confidence_history)//2))
    print("        " + "".join([str(i%10) for i in range(0, len(confidence_history), 2)]))
    print(f"        Iterations (Total: {len(confidence_history)})")

# Test persistence
print("\n" + "=" * 80)
print(" PERSISTENCE TEST")
print("=" * 80)
print("\nWaiting 2 seconds and checking if confidence persists...")
time.sleep(2)

persistence_check = get_current_confidence(TEST_QUERY)
if persistence_check:
    print(f"✅ Confidence after wait: {persistence_check['confidence']*100:.2f}%")
    if abs(persistence_check['confidence'] - final['confidence']) < 0.001:
        print("✅ PERSISTENCE CONFIRMED - Value stable!")
    else:
        print("⚠️ Value changed slightly")

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "query": TEST_QUERY,
    "iterations": feedback_count,
    "initial_confidence": initial['confidence'] if initial else 0,
    "final_confidence": final['confidence'] if final else 0,
    "confidence_history": confidence_history,
    "improvement": (final['confidence'] - initial['confidence']) if (final and initial) else 0
}

with open("hrm_learning_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n✅ Results saved to hrm_learning_results.json")
print("=" * 80)
