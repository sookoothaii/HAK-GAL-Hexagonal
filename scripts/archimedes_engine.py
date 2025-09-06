# archimedes_engine.py

import json
import os
import sys
import asyncio
import subprocess

class ArchimedesEngine:
    def __init__(self, mcp_server_path="D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\ultimate_mcp\\hakgal_mcp_ultimate.py"):
        self.mcp_server_path = mcp_server_path
        self.mcp_server_dir = os.path.dirname(mcp_server_path)
        print(f"[ArchimedesEngine] Initializing with MCP server: {self.mcp_server_path}", file=sys.stderr)
        sys.stderr.flush()

    async def _call_mcp_tool(self, tool_name: str, tool_args: dict):
        """
        Helper to call MCP tools via JSON-RPC over stdin/stdout using subprocess.
        """
        request_payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": tool_args
            },
            "id": f"archimedes_call_{tool_name}_{os.urandom(4).hex()}"
        }
        
        json_request = json.dumps(request_payload)
        
        print(f"[ArchimedesEngine Debug] Calling MCP tool: {tool_name} with payload: {json_request[:100]}...", file=sys.stderr)
        sys.stderr.flush()

        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                self.mcp_server_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.mcp_server_dir
            )
            
            stdout_bytes, stderr_bytes = await process.communicate(json_request.encode('utf-8'))
            
            stdout = stdout_bytes.decode('utf-8', errors='replace')
            stderr = stderr_bytes.decode('utf-8', errors='replace')

            print(f"[ArchimedesEngine Debug] MCP tool {tool_name} stdout: {stdout[:500]}", file=sys.stderr)
            print(f"[ArchimedesEngine Debug] MCP tool {tool_name} stderr: {stderr[:500]}", file=sys.stderr)
            sys.stderr.flush()

            if process.returncode != 0:
                print(f"[ArchimedesEngine Error] MCP server exited with code {process.returncode}", file=sys.stderr)
                raise Exception(f"MCP server error: {stderr}")

            response = json.loads(stdout)
            return response
            
        except json.JSONDecodeError as e:
            print(f"[ArchimedesEngine Error] Failed to decode JSON from MCP server: {e}", file=sys.stderr)
            print(f"Raw stdout: {stdout}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"[ArchimedesEngine Error] Error calling MCP tool {tool_name}: {e}", file=sys.stderr)
            raise

    async def delegate_task(self, agent_name: str, task_description: str, context: dict = None):
        print(f"[ArchimedesEngine] Delegating task to {agent_name}: {task_description[:50]}...", file=sys.stderr)
        sys.stderr.flush()
        
        response = await self._call_mcp_tool("delegate_task", {
            "target_agent": agent_name,
            "task_type": "chat",
            "task_description": task_description,
            "context": context or {}
        })
        
        if "result" in response:
            return response["result"]
        elif "error" in response:
            print(f"[ArchimedesEngine Error] Delegate task failed: {response['error']}", file=sys.stderr)
            sys.stderr.flush()
            raise Exception(f"Delegate task error: {response['error']}")
        else:
            print(f"[ArchimedesEngine Error] Unexpected response from delegate_task: {response}", file=sys.stderr)
            sys.stderr.flush()
            raise Exception(f"Unexpected delegate_task response: {response}")

    async def generate_scientific_breakthrough(self, scientific_domain: str, observed_phenomena: list = None, constraints: list = None):
        print(f"[ArchimedesEngine] Generating breakthrough for domain: {scientific_domain}", file=sys.stderr)
        sys.stderr.flush()
        
        observed_phenomena = observed_phenomena or []
        constraints = constraints or []

        deepseek_task = f"Generate novel, testable scientific hypotheses for the domain '{scientific_domain}'. Observed phenomena: {', '.join(observed_phenomena)}. Focus on creativity and diversity. Provide a list of hypotheses, one per line."
        deepseek_response = await self.delegate_task("DeepSeek", deepseek_task)
        
        raw_hypotheses_text = deepseek_response["content"][0]["text"]
        raw_hypotheses = [h.strip() for h in raw_hypotheses_text.split('\n') if h.strip()]
        
        hypotheses = []
        for i, h_statement in enumerate(raw_hypotheses):
            hypotheses.append({
                "statement": h_statement,
                "novelty_score": 0.5,
                "feasibility_score": 0.5,
                "llm_origin": "DeepSeek"
            })

        experimental_designs = []
        for i, hypothesis in enumerate(hypotheses):
            claude_task = f"Design a detailed experimental protocol to test the hypothesis: '{hypothesis['statement']}'. Consider constraints: {', '.join(constraints)}. Identify potential pitfalls and suggest improvements for rigor. Provide the protocol as a step-by-step guide, followed by a list of materials and equipment, predicted outcomes, and potential pitfalls."
            claude_response = await self.delegate_task("Claude", claude_task, context={"hypothesis": hypothesis["statement"], "constraints": constraints})
            
            protocol_text = claude_response["content"][0]["text"]
            
            materials = []
            predicted_outcomes = []
            pitfalls = []
            
            if "Materials and Equipment:" in protocol_text:
                parts = protocol_text.split("Materials and Equipment:", 1)
                protocol_text = parts[0].strip()
                
                if "Predicted Outcomes:" in parts[1]:
                    mat_out_parts = parts[1].split("Predicted Outcomes:", 1)
                    materials = [m.strip() for m in mat_out_parts[0].split('\n') if m.strip()]
                    
                    if "Potential Pitfalls:" in mat_out_parts[1]:
                        out_pit_parts = mat_out_parts[1].split("Potential Pitfalls:", 1)
                        predicted_outcomes = [o.strip() for o in out_pit_parts[0].split('\n') if o.strip()]
                        pitfalls = [p.strip() for p in out_pit_parts[1].split('\n') if p.strip()]
                    else:
                        predicted_outcomes = [o.strip() for o in mat_out_parts[1].split('\n') if o.strip()]
                else:
                    materials = [m.strip() for m in parts[1].split('\n') if m.strip()]


            experimental_designs.append({
                "hypothesis_id": f"hypo_{i+1}",
                "protocol": protocol_text,
                "materials_and_equipment": materials,
                "predicted_outcomes": predicted_outcomes,
                "potential_pitfalls": pitfalls,
                "llm_origin": "Claude"
            })

        summary_report = f"""
--- The Archimedes Engine Report ---
Domain: {scientific_domain}
Observed Phenomena: {', '.join(observed_phenomena) if observed_phenomena else 'None'}
Constraints: {', '.join(constraints) if constraints else 'None'}

Generated Hypotheses:
"""
        for i, h in enumerate(hypotheses):
            summary_report += f"\n{i+1}. {h['statement']} (Novelty: {h['novelty_score']:.2f}, Feasibility: {h['feasibility_score']:.2f})"
        
        summary_report += "\n\nExperimental Designs:"
        for i, ed in enumerate(experimental_designs):
            summary_report += f"\n\n--- Design for Hypothesis {ed['hypothesis_id']} ---"
            summary_report += f"\nProtocol:\n{ed['protocol']}"
            summary_report += f"\nMaterials: {', '.join(ed['materials_and_equipment'])}"
            summary_report += f"\nPredicted Outcomes: {', '.join(ed['predicted_outcomes'])}"
            summary_report += f"\nPitfalls: {', '.join(ed['potential_pitfalls'])}"

        print(f"[ArchimedesEngine Debug] Hypotheses before return: {hypotheses}", file=sys.stderr)
        print(f"[ArchimedesEngine Debug] Experimental Designs before return: {experimental_designs}", file=sys.stderr)
        sys.stderr.flush()

        # Construct final_result step by step
        final_result = {}
        final_result["hypotheses"] = hypotheses
        final_result["experimental_designs"] = experimental_designs
        final_result["summary_report"] = summary_report
        
        print(f"[ArchimedesEngine Debug] Final result before return: {final_result}", file=sys.stderr)
        sys.stderr.flush()

        return final_result

def test_dict_creation():
    try:
        test_data = {"a": 1, "b": {"c": 2}}
        print(f"[ArchimedesEngine Debug] Test dict created: {test_data}", file=sys.stderr)
        sys.stderr.flush()
        return test_data
    except TypeError as e:
        print(f"[ArchimedesEngine Error] Test dict creation failed: {e}", file=sys.stderr)
        sys.stderr.flush()
        raise

async def main():
    test_dict_creation() # Call it here
    engine = ArchimedesEngine()
    result = await engine.generate_scientific_breakthrough(
        scientific_domain="quantum entanglement",
        observed_phenomena=["faster-than-light correlation"],
        constraints=["no supercolliders"]
    )
    
    # Write the structured result to a JSON file
    # report_file_path = "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\archimedes_report.json"
    # with open(report_file_path, "w", encoding="utf-8") as f:
    #     json.dump(result, f, indent=2, ensure_ascii=False)
    # print(f"\n--- Archimedes Engine Report saved to {report_file_path} ---", file=sys.stderr)
    # sys.stderr.flush()

    # Try dumping each part separately to find the culprit
    try:
        with open("D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hypotheses.json", "w", encoding="utf-8") as f:
            json.dump(result["hypotheses"], f, indent=2, ensure_ascii=False)
        print(f"\n--- Hypotheses saved to hypotheses.json ---", file=sys.stderr)
    except TypeError as e:
        print(f"\n--- Error dumping hypotheses: {e} ---", file=sys.stderr)
        sys.stderr.flush()
        raise

    try:
        with open("D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\experimental_designs.json", "w", encoding="utf-8") as f:
            json.dump(result["experimental_designs"], f, indent=2, ensure_ascii=False)
        print(f"\n--- Experimental Designs saved to experimental_designs.json ---", file=sys.stderr)
    except TypeError as e:
        print(f"\n--- Error dumping experimental_designs: {e} ---", file=sys.stderr)
        sys.stderr.flush()
        raise

    try:
        with open("D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\summary_report.txt", "w", encoding="utf-8") as f:
            f.write(result["summary_report"])
        print(f"\n--- Summary Report saved to summary_report.txt ---", file=sys.stderr)
    except TypeError as e:
        print(f"\n--- Error writing summary_report: {e} ---", file=sys.stderr)
        sys.stderr.flush()
        raise

    # Print the summary report to stdout as before
    print("\n--- Final Report ---")
    print(result["summary_report"])
    sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())