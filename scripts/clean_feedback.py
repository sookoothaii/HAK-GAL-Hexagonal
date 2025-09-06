"""
Clean Feedback Data - Remove corrupted entries for isa(gemini, ai_model).
"""

import json
from datetime import datetime

# Load current data
with open('D:/MCP Mods/HAK_GAL_HEXAGONAL/data/hrm_feedback.json', 'r') as f:
    data = json.load(f)

# Backup original
with open('D:/MCP Mods/HAK_GAL_HEXAGONAL/data/hrm_feedback_backup.json', 'w') as f:
    json.dump(data, f, indent=2)

# Clean up gemini entries - remove the corrupted ones with inconsistent confidence values
query_key = "isa(gemini, ai_model)."

if query_key in data['history']:
    # Keep only the first few entries that seem consistent
    # Remove all entries as they are corrupted by the bug
    del data['history'][query_key]
    print(f"Removed {query_key} corrupted history")

if query_key in data['adjustments']:
    del data['adjustments'][query_key]
    print(f"Removed {query_key} adjustment")

# Save cleaned data
data['last_updated'] = datetime.now().isoformat()
with open('D:/MCP Mods/HAK_GAL_HEXAGONAL/data/hrm_feedback.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Cleaned feedback data saved.")
print(f"Remaining queries: {list(data['history'].keys())}")
