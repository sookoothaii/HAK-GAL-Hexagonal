import asyncio, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer

SAFE_SKIP = {
  'add_fact','update_fact','delete_fact','bulk_delete',
  'write_file','create_file','delete_file','move_file','edit_file','multi_edit',
  'restore_kb','backup_kb','db_backup_now','db_backup_rotate','db_enable_wal','db_vacuum','db_checkpoint'
}

ARGS = {
  'search_knowledge': {"query": "HAK_GAL", "limit": 3},
  'get_recent_facts': {"count": 3},
  'list_recent_facts': {"count": 3},
  'get_predicates_stats': {},
  'get_system_status': {},
  'kb_stats': {},
  'list_audit': {"limit": 5},
  'export_facts': {"count": 5, "direction": "tail"},
  'growth_stats': {"days": 7},
  'semantic_similarity': {"statement": "Related(EntityA, EntityB).", "threshold": 0.1, "limit": 5},
  'consistency_check': {"limit": 200},
  'validate_facts': {"limit": 200},
  'get_entities_stats': {"min_occurrences": 2},
  'search_by_predicate': {"predicate": "Related", "limit": 5},
  'get_fact_history': {"statement": "Example(A,B).", "limit": 3},
  'query_related': {"entity": "HAK_GAL", "limit": 5},
  'analyze_duplicates': {"threshold": 0.8, "max_pairs": 10},
  'get_knowledge_graph': {"entity": "HAK_GAL", "depth": 1, "format": "json"},
  'find_isolated_facts': {"limit": 10},
  'inference_chain': {"start_fact": "Relates(A,B).", "max_depth": 3},
  'bulk_translate_predicates': {"mapping": {"Relates": "Related"}, "dry_run": True},
  'project_snapshot': {"title": "AutoTest", "description": "Read-only snapshot", "hub_path": str(Path('..\\PROJECT_HUB').resolve())},
  'project_list_snapshots': {"hub_path": str(Path('..\\PROJECT_HUB').resolve()), "limit": 5},
  'project_hub_digest': {"hub_path": str(Path('..\\PROJECT_HUB').resolve()), "limit_files": 1, "max_chars": 500},
  'health_check': {},
  'health_check_json': {},
  'get_facts_count': {},
  'execute_code': {"code": "print('2')\n", "language": "python", "timeout": 5},
  'consensus_evaluator': {"task_id": "auto", "outputs": [{"tool_name":"a","model":"m","content":"x","confidence":0.5},{"tool_name":"b","model":"m","content":"x","confidence":0.7}], "method": "semantic_similarity", "threshold": 0.5},
  'reliability_checker': {"tool_name": "get_system_status", "task": "Check status", "n_runs": 2},
  'bias_detector': {"tool_outputs": {"tool":["A","B","C"]}, "baseline": "balanced"},
  'delegation_optimizer': {"task_description": "Find best agent for code task", "available_tools": ["Claude","Deepseek","Gemini"], "context": {}}
}

DELEGATE_TESTS = [
  ("DeepSeek:chat", "Kurztest: Antworte mit 'OK-DS'"),
  ("Gemini:2.5-flash", "Kurztest: Antworte mit 'OK-G'"),
  ("Claude:sonnet", "Kurztest: Antworte mit 'OK-C'"),
]

def ascii_clean(s: str) -> str:
    try:
        return s.encode('ascii','replace').decode('ascii')
    except Exception:
        return s

async def run():
    server = HAKGALMCPServer()
    captured = []
    async def cap(resp): captured.append(resp)
    server.send_response = cap
    await server.handle_initialize({"id": 1})

    await server.handle_list_tools({"id": 2})
    tools = []
    for r in captured:
        if r.get("id") == 2:
            tools = [t.get('name') for t in (r.get('result') or {}).get('tools', [])]
    results = {"ts": time.time(), "total_tools": len(tools), "summary": {}, "errors": {}, "skipped": []}

    for idx, (agent, task) in enumerate(DELEGATE_TESTS, start=10):
        try:
            await server.handle_tool_call({"id": idx, "params": {"name": "delegate_task", "arguments": {"target_agent": agent, "task_description": task, "context": {"ssot_mode": True}}}})
            for r in captured:
                if r.get("id") == idx:
                    items = (r.get("result") or {}).get("content") or []
                    text = next((it.get("text") for it in items if it.get("type")=="text"), "")
                    results["summary"][f"delegate:{agent}"] = (text or "")[:200]
        except Exception as e:
            results["errors"][f"delegate:{agent}"] = str(e)

    request_id = 100
    for name in tools:
        if name in ("delegate_task",):
            continue
        if name in SAFE_SKIP:
            results["skipped"].append(name)
            continue
        args = ARGS.get(name, {})
        try:
            request_id += 1
            await server.handle_tool_call({"id": request_id, "params": {"name": name, "arguments": args}})
            for r in captured:
                if r.get("id") == request_id:
                    items = (r.get("result") or {}).get("content") or []
                    text = next((it.get("text") for it in items if it.get("type")=="text"), "")
                    results["summary"][name] = (text or "")[:300]
                    break
            if name not in results["summary"]:
                results["summary"][name] = "<no-text>"
        except Exception as e:
            results["errors"][name] = str(e)

    out_dir = Path('..\\reports')
    out_dir.mkdir(exist_ok=True)
    (out_dir/ 'mcp_full_test.json').write_text(json.dumps(results, ensure_ascii=True, indent=2), encoding='ascii')
    md = ["MCP Full Tool Test (ASCII)", ""]
    md.append("Total tools: " + str(results['total_tools']))
    md.append("")
    md.append("Skipped (write/ops): " + ", ".join(sorted(results['skipped'])))
    md.append("")
    md.append("Errors:")
    if results['errors']:
        for k,v in results['errors'].items():
            md.append("- " + ascii_clean(k) + ": " + ascii_clean((v or "")[:200]))
    else:
        md.append("- <none>")
    md.append("")
    md.append("Summaries:")
    for k,v in sorted(results['summary'].items()):
        safe = ascii_clean((v or "").replace("\n"," ")[:200])
        md.append("- " + ascii_clean(k) + ": " + safe)
    (out_dir/ 'mcp_full_test.md').write_text("\n".join(md), encoding='ascii')
    print('MCP tool test written to reports/mcp_full_test.{json,md}')

asyncio.run(run())
