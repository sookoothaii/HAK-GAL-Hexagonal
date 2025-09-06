import asyncio, json, sys, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer

ROOT = Path(r'D:\MCP Mods\HAK_GAL_HEXAGONAL')

SAFE_TOKEN = re.compile(r'[^A-Za-z0-9_]')

def to_token(s: str, prefix: str) -> str:
    s = s.strip().lower()
    s = s.replace('-', ' ').replace(':',' ').replace('/',' ').replace('\\',' ')
    s = re.sub(r'\s+', '_', s)
    s = SAFE_TOKEN.sub('_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    if not s:
        s = 'x'
    return (prefix + '_' + s)[:64]

async def add_fact(server: HAKGALMCPServer, text: str):
    out = []
    async def cap(resp): out.append(resp)
    server.send_response = cap
    await server.handle_tool_call({"id": 2, "params": {"name": "add_fact", "arguments": {"statement": text}}})
    # ignore response content

async def main():
    # Load report
    report_path = ROOT / 'archimedes_report.json'
    hypotheses = []
    designs = []
    summary = ''
    if report_path.exists():
        try:
            data = json.loads(report_path.read_text(encoding='utf-8', errors='replace'))
            hypotheses = data.get('hypotheses') or []
            designs = data.get('experimental_designs') or []
            summary = data.get('summary_report') or ''
        except Exception:
            pass
    # Fallback to split files
    if not hypotheses:
        p = ROOT / 'hypotheses.json'
        if p.exists():
            try:
                hypotheses = json.loads(p.read_text(encoding='utf-8', errors='replace')) or []
            except Exception:
                pass
    if not designs:
        p = ROOT / 'experimental_designs.json'
        if p.exists():
            try:
                designs = json.loads(p.read_text(encoding='utf-8', errors='replace')) or []
            except Exception:
                pass
    if not summary:
        p = ROOT / 'summary_report.txt'
        if p.exists():
            try:
                summary = p.read_text(encoding='utf-8', errors='replace')
            except Exception:
                pass

    # Build facts (ASCII-safe tokens only)
    domain = 'QuantumEntanglement'
    facts = []
    for idx, h in enumerate(hypotheses, start=1):
        hid = f'H{idx:02d}'
        hname = f'Hypo_{hid}'
        facts.append(f"HypothesisForDomain({hname}, {domain}).")
        facts.append(f"HypothesisOrigin({hname}, DeepSeek).")
    for idx, d in enumerate(designs, start=1):
        did = f'D{idx:02d}'
        dname = f'Design_{did}'
        # link 1:1 by index where possible
        hname = f'Hypo_H{idx:02d}' if idx <= len(hypotheses) else f'Hypo_H01'
        facts.append(f"HasExperimentalDesign({hname}, {dname}).")
        facts.append(f"DesignOrigin({dname}, Claude).")
    # Summary marker
    from datetime import datetime
    ts = datetime.utcnow().strftime('%Y%m%d')
    facts.append(f"SummaryCreated(ArchimedesEngine, {ts}).")

    server = HAKGALMCPServer()
    # initialize once
    out = []
    async def cap(resp): out.append(resp)
    server.send_response = cap
    await server.handle_initialize({"id": 1})

    # Insert facts
    added = 0
    for f in facts:
        try:
            await add_fact(server, f)
            added += 1
        except Exception:
            continue

    # Append summary to GEMINI.md
    gpath = ROOT / 'GEMINI.md'
    try:
        header = f"\n\n## Archimedes Engine Summary ({ts})\n\n"
        gpath.write_text(gpath.read_text(encoding='utf-8', errors='replace') + header + (summary or '') + "\n", encoding='utf-8', errors='ignore')
        appended = True
    except Exception:
        appended = False

    print(json.dumps({"facts_added": added, "hypotheses": len(hypotheses), "designs": len(designs), "summary_appended": appended}, ensure_ascii=True))

asyncio.run(main())
