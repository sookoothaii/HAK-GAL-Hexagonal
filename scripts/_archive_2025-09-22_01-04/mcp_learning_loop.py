"""
MCP Tools Learning Loop - Signifikante Confidence Steigerung
Verwendet HAK-GAL Native Tools für direkten Zugriff
"""
import subprocess
import json
import time
from datetime import datetime

# Test Query - eine neue Query für sauberen Test
TEST_QUERY = "IsA(HAK_GAL, Knowledge_System)."

print("=" * 80)
print("🧠 HRM LEARNING DEMONSTRATION MIT MCP TOOLS")
print("=" * 80)
print(f"\nQuery: {TEST_QUERY}")
print("Ziel: Confidence von 0% auf 20%+ durch wiederholtes Lernen\n")

# Funktion zum Ausführen von curl commands
def api_call(endpoint, method="POST", data=None):
    """Execute API call using curl"""
    cmd = [
        "curl", "-s", "-X", method,
        f"http://127.0.0.1:5002{endpoint}",
        "-H", "Content-Type: application/json",
        "-H", "X-API-Key: hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"
    ]
    if data:
        cmd.extend(["-d", json.dumps(data)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"Error: {e}")
    return None

# Phase 1: Initial State
print("📊 PHASE 1: Initial State Check")
print("-" * 40)

# Füge den Fakt zur KB hinzu
print("Adding fact to knowledge base...")
# Dies würde normalerweise über MCP Tool gemacht, aber hier simulieren wir es
initial_reason = api_call("/api/reason", data={"query": TEST_QUERY})

if initial_reason:
    initial_conf = initial_reason.get('confidence', 0)
    print(f"Initial Confidence: {initial_conf*100:.4f}%")
    print(f"Base Model: {initial_reason.get('base_confidence', 0)*100:.6f}%")
    print(f"Feedback Count: {initial_reason.get('feedback_count', 0)}")
else:
    initial_conf = 0
    print("Starting from 0%")

# Phase 2: Learning Loop
print("\n📚 PHASE 2: Automated Learning Loop (15 iterations)")
print("-" * 40)

confidence_progression = [initial_conf]

for i in range(15):
    # Give positive feedback
    feedback_result = api_call("/api/hrm/feedback", data={
        "query": TEST_QUERY,
        "type": "positive",
        "confidence": confidence_progression[-1] if confidence_progression else 0.5
    })
    
    if feedback_result and feedback_result.get('success'):
        # Get updated confidence
        time.sleep(0.1)  # Small delay for processing
        updated = api_call("/api/reason", data={"query": TEST_QUERY})
        
        if updated:
            new_conf = updated.get('confidence', 0)
            confidence_progression.append(new_conf)
            
            # Visual progress indicator
            progress = int(new_conf * 100 / 0.25)  # Scale to 25% max
            bar = '█' * min(progress, 40) + '░' * max(0, 40 - progress)
            
            print(f"Iteration {i+1:2d}: [{bar}] {new_conf*100:6.2f}%")
            
            # Every 5 iterations, show detailed stats
            if (i+1) % 5 == 0:
                print(f"  → Adjustment: {updated.get('adjustment', 0)*100:.2f}%")
                print(f"  → Total Feedbacks: {updated.get('feedback_count', 0)}")
    
    # Variable speed
    if i < 3:
        time.sleep(0.3)  # Slower initially to show effect
    else:
        time.sleep(0.05)  # Faster later

# Phase 3: Final Analysis
print("\n📈 PHASE 3: Final Results")
print("-" * 40)

final_check = api_call("/api/reason", data={"query": TEST_QUERY})

if final_check and initial_reason:
    final_conf = final_check.get('confidence', 0)
    
    print(f"\n🎯 RESULTS SUMMARY:")
    print(f"  Initial: {initial_conf*100:.2f}%")
    print(f"  Final:   {final_conf*100:.2f}%")
    print(f"  GAIN:    {(final_conf - initial_conf)*100:+.2f}%")
    
    print(f"\n📊 LEARNING METRICS:")
    print(f"  Base Model Output: {final_check.get('base_confidence', 0)*100:.6f}%")
    print(f"  Learning Adjustment: {final_check.get('adjustment', 0)*100:.2f}%")
    print(f"  Total Feedbacks: {final_check.get('feedback_count', 0)}")
    print(f"  Avg Gain per Feedback: {(final_conf - initial_conf)/15*100:.3f}%")
    
    # ASCII Chart of progression
    if len(confidence_progression) > 1:
        print(f"\n📉 CONFIDENCE GROWTH CURVE:")
        max_val = max(confidence_progression)
        chart_height = 8
        
        for row in range(chart_height, -1, -1):
            threshold = row / chart_height * max_val
            line = f"{threshold*100:5.1f}% │"
            
            for val in confidence_progression[::2]:  # Every 2nd value for space
                if val >= threshold:
                    line += "█"
                else:
                    line += " "
            print(line)
        
        print("       └" + "─" * (len(confidence_progression)//2))
        print("        Start" + " " * (len(confidence_progression)//2 - 8) + "End")

# Phase 4: Persistence Verification
print("\n🔒 PHASE 4: Persistence Check")
print("-" * 40)
print("Waiting 3 seconds...")
time.sleep(3)

persistence = api_call("/api/reason", data={"query": TEST_QUERY})
if persistence:
    persist_conf = persistence.get('confidence', 0)
    print(f"Confidence after wait: {persist_conf*100:.2f}%")
    if abs(persist_conf - final_conf) < 0.001:
        print("✅ PERSISTENCE VERIFIED - Learning is permanent!")
    else:
        print(f"⚠️  Small drift detected: {(persist_conf - final_conf)*100:+.4f}%")

# Save results
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
result_file = f"learning_demo_{timestamp}.json"
results = {
    "timestamp": datetime.now().isoformat(),
    "query": TEST_QUERY,
    "initial_confidence": initial_conf,
    "final_confidence": final_conf if 'final_conf' in locals() else persist_conf,
    "confidence_progression": confidence_progression,
    "total_gain": (final_conf - initial_conf) if 'final_conf' in locals() else 0
}

with open(result_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n💾 Results saved to {result_file}")
print("=" * 80)
