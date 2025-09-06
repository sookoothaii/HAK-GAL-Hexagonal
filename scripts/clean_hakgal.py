"""
Clean HAK_GAL System feedback for fresh test
"""
import json

# Load data
with open('D:/MCP Mods/HAK_GAL_HEXAGONAL/data/hrm_feedback.json', 'r') as f:
    data = json.load(f)

# Remove the problematic entry
if "isa(hak_gal, system)." in data['history']:
    del data['history']["isa(hak_gal, system)."]
    print("Removed history for 'isa(hak_gal, system).'")

if "isa(hak_gal, system)." in data['adjustments']:
    del data['adjustments']["isa(hak_gal, system)."]
    print("Removed adjustment for 'isa(hak_gal, system).'")

# Save
with open('D:/MCP Mods/HAK_GAL_HEXAGONAL/data/hrm_feedback.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Data cleaned - ready for fresh test!")
