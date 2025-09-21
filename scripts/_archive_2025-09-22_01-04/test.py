import re
import os
from datetime import datetime

files = {
    "v31_REPAIRED": r"D:\MCP Mods\HAK_GAL_HEXAGONAL\scripts\hakgal_mcp_v31_REPAIRED.py",
    "sqlite_full": r"D:\MCP Mods\HAK_GAL_HEXAGONAL\scripts\hak_gal_mcp_sqlite_full.py", 
    "fixed_backup": r"D:\MCP Mods\HAK_GAL_HEXAGONAL\scripts\hak_gal_mcp_fixed_backup.py"
}

print("=" * 80)
print(" UMFASSENDER MCP SERVER VERGLEICHSBERICHT")
print("=" * 80)
print()

server_data = {}

for name, filepath in files.items():
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Sammle Metriken
    lines = content.split('\n')  # KORRIGIERT: Einfacher String statt Escape-Sequenz
    
    # Tools
    tool_impls = re.findall(r'(?:if|elif) tool_name == "([^"]+)"', content)
    unique_tools = set(tool_impls)
    
    # Features erkennen
    features = {
        'SQLite Support': 'sqlite3' in content.lower(),
        'Code Execution': 'execute_code' in content or 'subprocess.run' in content,
        'Semantic Search': 'semantic_similarity' in content,
        'Project Management': 'project_snapshot' in content,
        'Delegation': 'delegate_task' in content,
        'WebSocket': 'websocket' in content.lower(),
        'Multi-Edit': 'multi_edit' in content,
        'Growth Engine': 'growth_stats' in content,
        'Audit Logging': 'list_audit' in content,
        'Knowledge Graph': 'get_knowledge_graph' in content,
        'Consistency Check': 'consistency_check' in content,
        'Bulk Operations': 'bulk_delete' in content or 'bulk_translate' in content,
        'File Search': 'grep' in content and 'find_files' in content,
        'Backup/Restore': 'backup_kb' in content and 'restore_kb' in content
    }
    
    # Error Handling - KORRIGIERT: Raw strings richtig verwendet
    try_blocks = len(re.findall(r'\btry:', content))
    except_blocks = len(re.findall(r'\bexcept\b', content))
    
    # Imports
    imports = len(re.findall(r'^import |^from ', content, re.MULTILINE))
    
    # Dokumentation
    docstrings = len(re.findall(r'""".*?"""', content, re.DOTALL))
    
    server_data[name] = {
        'file_size': len(content),
        'lines': len(lines),
        'tools': len(unique_tools),
        'tool_list': sorted(unique_tools),
        'features': features,
        'try_blocks': try_blocks,
        'except_blocks': except_blocks,
        'imports': imports,
        'docstrings': docstrings,
        'last_modified': os.path.getmtime(filepath)
    }

# 1. ÜBERSICHT
print("📊 ÜBERSICHT")
print("-" * 40)
print(f"{'Server':<15} {'Größe':<12} {'Zeilen':<10} {'Tools':<8} {'Letzte Änderung'}")
print("-" * 40)

for name, data in server_data.items():
    mod_date = datetime.fromtimestamp(data['last_modified']).strftime('%Y-%m-%d')
    size_kb = f"{data['file_size']/1024:.1f} KB"
    print(f"{name:<15} {size_kb:<12} {data['lines']:<10} {data['tools']:<8} {mod_date}")

# 2. FEATURE-MATRIX
print("\n📋 FEATURE-MATRIX")  # KORRIGIERT
print("-" * 40)
print(f"{'Feature':<25} {'v31_REP':<10} {'sqlite':<10} {'fixed':<10}")
print("-" * 40)

all_features = set()
for data in server_data.values():
    all_features.update(data['features'].keys())

for feature in sorted(all_features):
    v31 = "✅" if server_data['v31_REPAIRED']['features'].get(feature, False) else "❌"
    sql = "✅" if server_data['sqlite_full']['features'].get(feature, False) else "❌"
    fix = "✅" if server_data['fixed_backup']['features'].get(feature, False) else "❌"
    print(f"{feature:<25} {v31:<10} {sql:<10} {fix:<10}")

# 3. CODE-QUALITÄT
print("\n🔍 CODE-QUALITÄT")  # KORRIGIERT
print("-" * 40)
print(f"{'Metrik':<20} {'v31_REP':<10} {'sqlite':<10} {'fixed':<10}")
print("-" * 40)

metrics = ['try_blocks', 'except_blocks', 'imports', 'docstrings']
for metric in metrics:
    v31 = server_data['v31_REPAIRED'][metric]
    sql = server_data['sqlite_full'][metric]
    fix = server_data['fixed_backup'][metric]
    print(f"{metric:<20} {v31:<10} {sql:<10} {fix:<10}")

# 4. UNIQUE TOOLS
print("\n🔧 EINZIGARTIGE TOOLS")  # KORRIGIERT
print("-" * 40)

for name, data in server_data.items():
    unique = set(data['tool_list'])
    for other_name, other_data in server_data.items():
        if other_name != name:
            unique -= set(other_data['tool_list'])
    
    if unique:
        print(f"\nNur in {name}:")  # KORRIGIERT
        for tool in sorted(unique)[:5]:  # Max 5 zeigen
            print(f"  - {tool}")

# 5. BEWERTUNG
print("\n⭐ BEWERTUNG")  # KORRIGIERT
print("-" * 40)

scores = {}
for name, data in server_data.items():
    score = 0
    score += min(data['tools'], 50) * 2  # Max 100 Punkte für Tools
    score += sum(1 for f in data['features'].values() if f) * 5  # 5 Punkte pro Feature
    score += min(data['try_blocks'], 20)  # Max 20 für Error Handling
    score += min(data['docstrings'], 10) * 2  # Max 20 für Dokumentation
    scores[name] = score

max_score = max(scores.values())
for name, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
    stars = "⭐" * (score * 5 // max_score)
    print(f"{name:<15} {score:3} Punkte {stars}")

# FINALE EMPFEHLUNG
print("\n" + "=" * 80)  # KORRIGIERT
print("📌 EMPFEHLUNG")
print("=" * 80)

winner = max(scores.items(), key=lambda x: x[1])[0]
print(f"\nUMFANGREICHSTER SERVER: {winner}")  # KORRIGIERT
print(f"- {server_data[winner]['tools']} Tools implementiert")
print(f"- {sum(1 for f in server_data[winner]['features'].values() if f)} von {len(all_features)} Features")
print(f"- {server_data[winner]['file_size']/1024:.1f} KB Codegröße")
print(f"- Gesamtpunktzahl: {scores[winner]}")
