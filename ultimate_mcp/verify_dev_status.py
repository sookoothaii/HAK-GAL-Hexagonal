
import subprocess
import json
import os
import sys

# Tools we already know are working from our previous tests
IMPLEMENTED_TOOLS = {
    "get_system_status", "get_facts_count", "get_predicates_stats",
    "health_check", "add_fact", "search_knowledge", "delete_fact", "execute_code"
}

# Full list of 47 declared tools from the server's source code
ALL_TOOLS = [
    "get_facts_count", "search_knowledge", "get_recent_facts", "get_predicates_stats",
    "get_system_status", "list_recent_facts", "add_fact", "delete_fact", "update_fact",
    "kb_stats", "list_audit", "export_facts", "growth_stats", "health_check",
    "semantic_similarity", "consistency_check", "validate_facts", "get_entities_stats",
    "search_by_predicate", "get_fact_history", "backup_kb", "restore_kb", "bulk_delete",
    "query_related", "analyze_duplicates", "get_knowledge_graph", "find_isolated_facts",
    "inference_chain", "bulk_translate_predicates", "project_snapshot",
    "project_list_snapshots", "project_hub_digest", "delegate_task", "execute_code",
    "read_file", "write_file", "list_files", "get_file_info", "directory_tree",
    "create_file", "delete_file", "move_file", "grep", "find_files", "search",
    "edit_file", "multi_edit"
]

TOOLS_TO_TEST = sorted([tool for tool in ALL_TOOLS if tool not in IMPLEMENTED_TOOLS])

# This script should be in 'ultimate_mcp', so paths are relative to it
PYTHON_EXE = os.path.abspath(os.path.join("..", ".venv_hexa", "Scripts", "python.exe"))
MCP_SCRIPT = os.path.abspath("hakgal_mcp_ultimate.py")

if not os.path.exists(PYTHON_EXE):
    print(f"FATAL: Python executable not found at {PYTHON_EXE}")
    sys.exit(1)
if not os.path.exists(MCP_SCRIPT):
    print(f"FATAL: MCP script not found at {MCP_SCRIPT}")
    sys.exit(1)

print("Starting automated verification of 'in development' tools...")
print(f"Found {len(TOOLS_TO_TEST)} tools to check.")
print("-" * 60)

implemented_count = 0
in_dev_count = 0
error_count = 0

for i, tool_name in enumerate(TOOLS_TO_TEST):
    # Use harmless arguments for tools that might require them
    # This avoids errors for missing arguments and focuses on the implementation status
    args = {
        "query": "test", "predicate": "test", "entity": "test", "statement": "test(a,b)",
        "start_fact": "test(a,b)", "path": "dummy_file.txt", "source": "a", "destination": "b",
        "pattern": "test", "oldText": "a", "newText": "b", "edits": [], "mapping": {},
        "target_agent": "test", "task_description": "test"
    }

    request = {
        "jsonrpc": "2.0",
        "id": i + 1,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": args}
    }
    
    input_data = json.dumps(request)
    status = ""
    
    try:
        result = subprocess.run(
            [PYTHON_EXE, MCP_SCRIPT],
            input=input_data,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=15
        )
        
        response_text = result.stdout.strip()
        if not response_text:
            status = "ERROR (No Response)"
            error_count += 1
        else:
            response_json = json.loads(response_text)
            content = response_json.get("result", {}).get("content", [{}])[0].get("text", "")
            
            if "in development" in content:
                status = "In Development"
                in_dev_count += 1
            else:
                # Any other response means it's likely implemented in some form
                status = "Implemented"
                implemented_count += 1

    except Exception as e:
        status = f"ERROR ({type(e).__name__})"
        error_count += 1

    print(f"  - {tool_name:<30} ... STATUS: {status}")

print("-" * 60)
print("Verification Complete.")
print(f"  Implemented:     {implemented_count}")
print(f"  In Development:  {in_dev_count}")
print(f"  Errors:          {error_count}")
print(f"  --------------------")
print(f"  Total Tested:    {len(TOOLS_TO_TEST)}")
