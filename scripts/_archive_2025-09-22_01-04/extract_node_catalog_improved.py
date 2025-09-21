# extract_node_catalog_improved.py
import json
import re

# Read the WorkflowPro.tsx file
with open("frontend/src/pages/WorkflowPro.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# Find NODE_CATALOG definition
start = content.find("const NODE_CATALOG = {")
if start == -1:
    print("NODE_CATALOG not found!")
    exit(1)

# Find the matching closing brace
depth = 0
i = start + len("const NODE_CATALOG = ") - 1
end = -1

while i < len(content):
    if content[i] == '{':
        depth += 1
    elif content[i] == '}':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
    i += 1

if end == -1:
    print("Could not find closing brace!")
    exit(1)

# Extract the catalog
catalog_str = content[start + len("const NODE_CATALOG = "):end]

# Manual parsing since it's TypeScript, not JSON
# We'll extract the tools manually
tools_by_category = {}
current_category = None
in_tools_array = False
current_tool = None
tools_list = []

lines = catalog_str.split('\n')
for line in lines:
    line = line.strip()
    
    # Detect category
    if ': {' in line and not in_tools_array:
        current_category = line.split(':')[0].strip()
        tools_by_category[current_category] = {
            'label': '',
            'tools': []
        }
    
    # Detect label
    elif line.startswith('label:') and current_category and not in_tools_array:
        label = line.split("'")[1] if "'" in line else line.split('"')[1]
        tools_by_category[current_category]['label'] = label
    
    # Detect tools array start
    elif line.startswith('tools: ['):
        in_tools_array = True
        tools_list = []
    
    # Detect tool start
    elif '{ id:' in line and in_tools_array:
        # Extract tool id
        match = re.search(r"id:\s*'([^']+)'", line)
        if match:
            tool_id = match.group(1)
            current_tool = {'id': tool_id}
    
    # Detect tool label
    elif 'label:' in line and in_tools_array and current_tool:
        match = re.search(r"label:\s*'([^']+)'", line)
        if match:
            current_tool['label'] = match.group(1)
    
    # Detect write flag
    elif 'write: true' in line and current_tool:
        current_tool['write'] = True
    
    # Tool end (closing brace with comma or without)
    elif (line == '},' or line == '}') and current_tool:
        tools_list.append(current_tool)
        current_tool = None
    
    # Tools array end
    elif line.startswith(']') and in_tools_array:
        if current_category:
            tools_by_category[current_category]['tools'] = tools_list
        in_tools_array = False
        tools_list = []

# Create results
all_tools = []
mcp_tools = []
workflow_tools = []
write_tools = []

# Categories that are MCP backend tools based on the file
MCP_CATEGORIES = [
    'KNOWLEDGE_BASE', 'DB_ADMIN', 'PROJECT_HUB', 'NICHE_SYSTEM',
    'SENTRY_MONITORING', 'AI_DELEGATION', 'FILE_OPERATIONS', 'EXECUTION'
]

# Process tools
for category, data in tools_by_category.items():
    for tool in data['tools']:
        tool_info = {
            'category': category,
            'category_label': data['label'],
            'id': tool['id'],
            'label': tool.get('label', tool['id']),
            'write': tool.get('write', False),
            'is_mcp': category in MCP_CATEGORIES
        }
        
        all_tools.append(tool_info)
        
        if tool_info['is_mcp']:
            mcp_tools.append(tool_info)
        else:
            workflow_tools.append(tool_info)
            
        if tool_info['write']:
            write_tools.append(tool_info)

# Save results
with open('node_catalog_analysis.json', 'w', encoding='utf-8') as f:
    json.dump({
        'total_tools': len(all_tools),
        'mcp_tools_count': len(mcp_tools),
        'workflow_tools_count': len(workflow_tools),
        'write_tools_count': len(write_tools),
        'categories': list(tools_by_category.keys()),
        'mcp_categories': MCP_CATEGORIES,
        'all_tools': all_tools,
        'mcp_tools': mcp_tools,
        'workflow_tools': workflow_tools,
        'write_tools': write_tools
    }, f, indent=2, ensure_ascii=False)

# Print summary
print(f"=== NODE CATALOG ANALYSIS ===")
print(f"Total tools: {len(all_tools)}")
print(f"MCP tools: {len(mcp_tools)}")
print(f"Workflow-only tools: {len(workflow_tools)}")
print(f"Write-enabled tools: {len(write_tools)}")
print(f"\nCategories ({len(tools_by_category)}):")
for cat, data in tools_by_category.items():
    is_mcp = cat in MCP_CATEGORIES
    print(f"  - {cat}: {len(data['tools'])} tools {'(MCP)' if is_mcp else '(Workflow)'}")

print(f"\nWrite tools by category:")
write_by_category = {}
for tool in write_tools:
    cat = tool['category']
    if cat not in write_by_category:
        write_by_category[cat] = []
    write_by_category[cat].append(tool['id'])

for cat, tools in write_by_category.items():
    print(f"  - {cat}: {', '.join(tools)}")

print("\nAnalysis saved to: node_catalog_analysis.json")
