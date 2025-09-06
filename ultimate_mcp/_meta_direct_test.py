import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer

async def call_tool(name, args):
    server = HAKGALMCPServer()
    bucket = []
    async def cap(resp): bucket.append(resp)
    server.send_response = cap
    await server.handle_initialize({"id": 1})
    await server.handle_tool_call({"id": 2, "params": {"name": name, "arguments": args}})
    for r in bucket:
        if r.get("id") == 2:
            items = (r.get("result") or {}).get("content") or []
            for it in items:
                if it.get("type") == "text":
                    return it.get("text")
    return "<no result>"

async def main():
    print('[DelegationOptimizer]')
    print(await call_tool('delegation_optimizer', {"task_description": "Kurzanalyse KB-Anomalien", "available_tools": ["DeepSeek","Gemini","Claude"], "context": {"has_analysis": True}}))

    print('\n[ConsensusEvaluator]')
    print(await call_tool('consensus_evaluator', {"task_id":"demo","outputs":[{"tool_name":"DeepSeek","content":"Empfehlung: validate_facts"},{"tool_name":"Gemini","content":"Empfehlung: validate_facts"},{"tool_name":"Claude","content":"Empfehlung: consistency_check"}],"method":"semantic_similarity","threshold":0.6}))

    print('\n[ReliabilityChecker]')
    print(await call_tool('reliability_checker', {"tool_name":"search_knowledge","task":"finde KB","n_runs":5}))

    print('\n[BiasDetector]')
    print(await call_tool('bias_detector', {"baseline":"balanced"}))

if __name__ == '__main__':
    asyncio.run(main())
