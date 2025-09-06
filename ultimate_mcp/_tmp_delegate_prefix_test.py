import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer

async def run_case(target_agent: str, proof_text: str):
    server = HAKGALMCPServer()
    captured = []
    async def capture(resp):
        captured.append(resp)
    server.send_response = capture

    await server.handle_initialize({"id": 1})
    args = {
        "target_agent": target_agent,
        "task_description": f"Schreibe genau: {proof_text}",
        "context": {"kb": "hexagonal_kb.db"}
    }
    await server.handle_tool_call({"id": 2, "params": {"name": "delegate_task", "arguments": args}})
    text = None
    for resp in captured:
        if resp.get("id") == 2:
            items = resp.get("result", {}).get("content", [])
            for it in items:
                if it.get("type") == "text":
                    text = it.get("text")
                    break
    print(f"\n[{target_agent}] -> {text}")

async def main():
    await run_case("DeepSeek:chat", "PREFIX_DEEPSEEK_OK_44444")
    await run_case("Gemini:2.5-flash", "PREFIX_GEMINI25_FLASH_OK_55555")

asyncio.run(main())
