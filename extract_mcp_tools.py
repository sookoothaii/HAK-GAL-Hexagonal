#!/usr/bin/env python3
# Extract tools from hakgal_mcp_ultimate.py by parsing the _get_tool_list() method
import re, json, csv, pathlib

MCP_FILE = pathlib.Path("ultimate_mcp/hakgal_mcp_ultimate.py")
OUT_JSON = pathlib.Path("mcp_tools_extracted.json")

def extract_mcp_tools(mcp_text):
    """Extract tools from the _get_tool_list() method"""
    tools = []
    
    # Find the _get_tool_list method
    start_match = re.search(r'def _get_tool_list\(self\):', mcp_text)
    if not start_match:
        print("_get_tool_list method not found!")
        return tools
    
    # Find all tool definitions within the method
    # Look for patterns like {"name": "tool_name", "description": "...", ...}
    # Use a simpler pattern to find tool names first
    tool_pattern = r'\{\s*"name"\s*:\s*"([^"]+)"'
    
    # Extract from the method body
    method_start = start_match.start()
    # Find the next method or class definition to limit scope
    next_def = re.search(r'\n\s*(def|class)\s+', mcp_text[method_start+100:])
    if next_def:
        method_end = method_start + 100 + next_def.start()
    else:
        method_end = len(mcp_text)
    
    method_text = mcp_text[method_start:method_end]
    
    # Find all tool names
    for match in re.finditer(tool_pattern, method_text):
        tool_name = match.group(1)
        tools.append(tool_name)
    
    # Also check the handle_tool_call method to see what tools are actually implemented
    # Look for patterns like: if tool_name == "tool_name":
    handle_pattern = r'if\s+tool_name\s*==\s*["\']([^"\']+)["\']'
    for match in re.finditer(handle_pattern, mcp_text):
        tool_name = match.group(1)
        if tool_name not in tools:
            tools.append(tool_name)
    
    # Also look for elif tool_name == patterns
    elif_pattern = r'elif\s+tool_name\s*==\s*["\']([^"\']+)["\']'
    for match in re.finditer(elif_pattern, mcp_text):
        tool_name = match.group(1)
        if tool_name not in tools:
            tools.append(tool_name)
    
    return sorted(list(set(tools)))

def main():
    if not MCP_FILE.exists():
        print(f"MCP file not found: {MCP_FILE}")
        return
    
    mcp_text = MCP_FILE.read_text(encoding="utf-8")
    print(f"Loaded MCP file: {len(mcp_text)} characters")
    
    # Extract tools
    tools = extract_mcp_tools(mcp_text)
    print(f"Found {len(tools)} tools in MCP file")
    
    # Save results
    result = {
        "mcp_file": str(MCP_FILE),
        "tool_count": len(tools),
        "tools": tools
    }
    
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Results saved to: {OUT_JSON}")
    
    # Compare with frontend
    node_csv = pathlib.Path("node_catalog.csv")
    if node_csv.exists():
        frontend_tools = set()
        with node_csv.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                frontend_tools.add(row["id"])
        
        mcp_set = set(tools)
        
        print(f"\nComparison:")
        print(f"Frontend tools: {len(frontend_tools)}")
        print(f"MCP tools: {len(mcp_set)}")
        print(f"In both: {len(frontend_tools & mcp_set)}")
        print(f"Only in frontend: {len(frontend_tools - mcp_set)}")
        print(f"Only in MCP: {len(mcp_set - frontend_tools)}")
        
        # Show first 10 missing tools
        missing = sorted(list(frontend_tools - mcp_set))[:10]
        if missing:
            print(f"\nFirst 10 tools missing from MCP:")
            for t in missing:
                print(f"  - {t}")

if __name__ == "__main__":
    main()
