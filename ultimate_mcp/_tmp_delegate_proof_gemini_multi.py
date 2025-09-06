import asyncio, json, sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer

MODELS = [
    ("gemini-2.0-flash-exp", "PROOF_GEM20_EXP_OK_11111"),
    ("gemini-2.5-flash", "PROOF_GEM25_FLASH_OK_22222"),
    ("gemini-2.5-pro", "PROOF_GEM25_PRO_OK_33333")
]

async def run_for(model_name: str, proof_text: str):
    os.environ["GEMINI_MODEL"] = model_name
    server = HAKGALMCPServer()
    captured = []
    async def capture(resp):
        captured.append(resp)
    server.send_response = capture
    await server.handle_initialize({"id": 1})
    args = {
        "target_agent": "Gemini",
        "task_description": f"Schreibe genau: {proof_text}",
        "context": {"kb": "hexagonal_kb.db"}
    }
    await server.handle_tool_call({"id": 2, "params": {"name": "delegate_task", "arguments": args}})
    proof = None
    for resp in captured:
        if resp.get("id") == 2:
            items = resp.get("result", {}).get("content", [])
            for it in items:
                if it.get("type") == "text":
                    proof = it.get("text")
                    break
    print(f"\n=== Model: {model_name} ===")
    print(proof or "<keine>")

async def main():
    for m, p in MODELS:
        try:
            await run_for(m, p)
        except Exception as e:
            print(f"\n=== Model: {m} ===")
            print(f"<error: {e}>")

asyncio.run(main())
