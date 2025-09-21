#!/usr/bin/env python3
# Read-only extractor: extracts NODE_CATALOG from WorkflowPro.tsx and writes JSON+CSV
# Usage: python extract_node_catalog.py
import re, json, csv, sys, pathlib

SRC = pathlib.Path("frontend/src/pages/WorkflowPro.tsx")
OUT_JSON = pathlib.Path("node_catalog.json")
OUT_CSV = pathlib.Path("node_catalog.csv")
DEBUG_DUMP = pathlib.Path("node_catalog_debug.json")

def find_node_catalog_text(text):
    m = re.search(r"const\s+NODE_CATALOG\s*=\s*{", text)
    if not m:
        return None
    start = m.start()
    # find balanced braces starting at the first '{' after 'NODE_CATALOG ='
    idx = text.find("{", start)
    if idx == -1:
        return None
    stack = []
    j = idx
    while j < len(text):
        ch = text[j]
        if ch == "{":
            stack.append("{")
        elif ch == "}":
            stack.pop()
            if not stack:
                return text[idx:j+1]
        j += 1
    return None

def sanitize_js_to_json(js_text):
    s = js_text
    # remove single-line comments
    s = re.sub(r"//.*", "", s)
    # remove block comments
    s = re.sub(r"/\*[\s\S]*?\*/", "", s)
    
    # replace unquoted category keys like KNOWLEDGE_BASE: with "KNOWLEDGE_BASE":
    s = re.sub(r"([\n\r]\s*)([A-Z0-9_]+)\s*:", r'\1"\2":', s)
    
    # replace all unquoted object property keys: label:, icon:, color:, tools:, id:, params:, write:, type: etc.
    s = re.sub(r'(\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', s)
    
    # replace icon identifiers (e.g., Database,) and other bare identifiers with null
    # but be careful not to replace boolean values (true, false) or null
    s = re.sub(r':\s*([A-Z][A-Za-z0-9_\.]*)(\s*[,}\]])', r': null\2', s)
    
    # replace single quotes with double quotes
    s = s.replace("'", '"')
    
    # remove trailing commas before } or ]
    s = re.sub(r",\s*([}\]])", r"\1", s)
    
    return s

def main():
    if not SRC.exists():
        print("Error: source file not found:", SRC)
        sys.exit(2)
    txt = SRC.read_text(encoding="utf-8")
    obj_text = find_node_catalog_text(txt)
    if not obj_text:
        print("NODE_CATALOG not found in", SRC)
        sys.exit(3)
    # wrap to make valid JSON-ish and sanitize
    json_like = obj_text
    clean = sanitize_js_to_json(json_like)
    try:
        data = json.loads(clean)
    except Exception as e:
        # fallback: write debug dump and exit
        print("JSON parse failed:", e)
        DEBUG_DUMP.write_text(clean, encoding="utf-8")
        print("Wrote debug file:", DEBUG_DUMP)
        sys.exit(4)
    # write JSON
    OUT_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    # write CSV
    rows = []
    for cat, meta in data.items():
        tools = meta.get("tools", [])
        for t in tools:
            rows.append({
                "category": cat,
                "id": t.get("id",""),
                "label": t.get("label",""),
                "write": bool(t.get("write", False))
            })
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["category","id","label","write"])
        writer.writeheader()
        writer.writerows(rows)
    print("Wrote:", OUT_JSON, OUT_CSV, "rows:", len(rows))
    
    # Print summary statistics
    mcp_categories = [
        'KNOWLEDGE_BASE', 'DB_ADMIN', 'PROJECT_HUB', 'NICHE_SYSTEM',
        'SENTRY_MONITORING', 'AI_DELEGATION', 'FILE_OPERATIONS', 'EXECUTION'
    ]
    
    mcp_tools = 0
    workflow_tools = 0
    write_tools = 0
    
    for row in rows:
        if row['category'] in mcp_categories:
            mcp_tools += 1
        else:
            workflow_tools += 1
        if row['write']:
            write_tools += 1
    
    print(f"\nSummary:")
    print(f"  Total tools: {len(rows)}")
    print(f"  MCP tools: {mcp_tools}")
    print(f"  Workflow-only tools: {workflow_tools}")
    print(f"  Write-enabled tools: {write_tools}")

if __name__ == "__main__":
    main()
