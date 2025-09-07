#!/usr/bin/env python3
# Compare frontend node_catalog.csv with MCP tool list
# Usage: python compare_with_mcp.py
import csv, re, sys, pathlib, json

NODE_CSV = pathlib.Path("node_catalog.csv")
MCP_FILE = pathlib.Path("ultimate_mcp/hakgal_mcp_ultimate.py")
OUT_DIFF = pathlib.Path("tools_diff_report.csv")
OUT_JSON = pathlib.Path("tools_diff_report.json")

def parse_mcp_tools(mcp_text):
    """Extract tool IDs from MCP file using multiple patterns"""
    ids = set()
    
    # Pattern 1: @tool decorators
    for m in re.finditer(r'@tool\(["\']([a-z0-9_]+)["\']', mcp_text):
        ids.add(m.group(1))
    
    # Pattern 2: server.register_tool patterns
    for m in re.finditer(r'register_tool\(["\']([a-z0-9_]+)["\']', mcp_text):
        ids.add(m.group(1))
    
    # Pattern 3: Look for tool functions (def toolname_handler)
    for m in re.finditer(r'def\s+([a-z0-9_]+)_handler\s*\(', mcp_text):
        ids.add(m.group(1))
    
    # Pattern 4: Tool registry entries
    for m in re.finditer(r'["\']([a-z0-9_]+)["\']:\s*\{[^}]*description["\']', mcp_text):
        ids.add(m.group(1))
    
    return ids

def main():
    if not NODE_CSV.exists():
        print("node_catalog.csv not found. Run extract_node_catalog.py first.")
        sys.exit(2)
    
    # Try multiple MCP file locations
    mcp_files = [
        pathlib.Path("ultimate_mcp/hakgal_mcp_ultimate.py"),
        pathlib.Path("ultimate_mcp/__init__.py"),
        pathlib.Path("hakgal_mcp.py"),
        pathlib.Path("mcp_server.py"),
    ]
    
    mcp_text = ""
    mcp_source = None
    for mcp_file in mcp_files:
        if mcp_file.exists():
            mcp_text = mcp_file.read_text(encoding="utf-8")
            mcp_source = str(mcp_file)
            print(f"Using MCP file: {mcp_file}")
            break
    
    if not mcp_text:
        print("No MCP file found. Checked:", ", ".join(str(f) for f in mcp_files))
        sys.exit(3)
    
    # read frontend nodes
    frontend = {}
    frontend_by_category = {}
    with NODE_CSV.open(encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        for row in r:
            frontend[row["id"]] = row
            cat = row["category"]
            if cat not in frontend_by_category:
                frontend_by_category[cat] = []
            frontend_by_category[cat].append(row["id"])
    
    # parse mcp file
    mcp_ids = parse_mcp_tools(mcp_text)
    print(f"Found {len(mcp_ids)} tools in MCP file")
    
    # Define MCP categories
    MCP_CATEGORIES = [
        'KNOWLEDGE_BASE', 'DB_ADMIN', 'PROJECT_HUB', 'NICHE_SYSTEM',
        'SENTRY_MONITORING', 'AI_DELEGATION', 'FILE_OPERATIONS', 'EXECUTION'
    ]
    
    # Get expected MCP tools from frontend
    expected_mcp_tools = set()
    for cat in MCP_CATEGORIES:
        if cat in frontend_by_category:
            expected_mcp_tools.update(frontend_by_category[cat])
    
    # produce diff
    rows = []
    all_ids = sorted(set(list(frontend.keys()) + list(mcp_ids)))
    
    only_in_frontend = []
    only_in_mcp = []
    in_both = []
    mcp_category_mismatch = []
    
    for tid in all_ids:
        in_frontend = tid in frontend
        in_mcp = tid in mcp_ids
        category = frontend[tid]["category"] if in_frontend else ""
        should_be_mcp = category in MCP_CATEGORIES if in_frontend else False
        
        status = ""
        if in_frontend and in_mcp:
            status = "OK (in both)"
            in_both.append(tid)
        elif in_frontend and not in_mcp and should_be_mcp:
            status = "MISSING in MCP"
            only_in_frontend.append(tid)
            mcp_category_mismatch.append(tid)
        elif in_frontend and not in_mcp and not should_be_mcp:
            status = "OK (Workflow-only)"
        elif not in_frontend and in_mcp:
            status = "EXTRA in MCP"
            only_in_mcp.append(tid)
        
        row = {
            "tool_id": tid,
            "in_frontend": str(in_frontend),
            "in_mcp": str(in_mcp),
            "category": category,
            "label": frontend[tid]["label"] if in_frontend else "",
            "is_mcp_category": str(should_be_mcp),
            "write": frontend[tid]["write"] if in_frontend else "",
            "status": status
        }
        rows.append(row)
    
    # write CSV
    with OUT_DIFF.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["tool_id","in_frontend","in_mcp","category","label","is_mcp_category","write","status"])
        writer.writeheader()
        writer.writerows(rows)
    
    # Write JSON report with summary
    report = {
        "mcp_source": mcp_source,
        "total_tools": len(all_ids),
        "frontend_tools": len(frontend),
        "mcp_tools": len(mcp_ids),
        "expected_mcp_tools": len(expected_mcp_tools),
        "in_both": len(in_both),
        "only_in_frontend": len(only_in_frontend),
        "only_in_mcp": len(only_in_mcp),
        "mcp_category_mismatch": len(mcp_category_mismatch),
        "missing_from_mcp": only_in_frontend,
        "extra_in_mcp": only_in_mcp,
        "write_tools_missing": [t for t in only_in_frontend if frontend.get(t, {}).get("write") == "True"]
    }
    
    OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    
    # Print summary
    print("\n=== TOOLS COMPARISON REPORT ===")
    print(f"Frontend tools: {len(frontend)}")
    print(f"MCP tools found: {len(mcp_ids)}")
    print(f"Expected MCP tools: {len(expected_mcp_tools)}")
    print(f"\nStatus:")
    print(f"  ✅ In both: {len(in_both)}")
    print(f"  ❌ Missing from MCP: {len(only_in_frontend)}")
    print(f"  ⚠️  Extra in MCP: {len(only_in_mcp)}")
    
    if only_in_frontend:
        print(f"\nMissing from MCP backend:")
        for tid in sorted(only_in_frontend):
            cat = frontend[tid]["category"]
            label = frontend[tid]["label"]
            write = " [WRITE]" if frontend[tid]["write"] == "True" else ""
            print(f"  - {tid} ({cat}: {label}){write}")
    
    if only_in_mcp:
        print(f"\nExtra in MCP (not in frontend):")
        for tid in sorted(only_in_mcp):
            print(f"  - {tid}")
    
    print(f"\nReports written to: {OUT_DIFF}, {OUT_JSON}")

if __name__ == "__main__":
    main()
