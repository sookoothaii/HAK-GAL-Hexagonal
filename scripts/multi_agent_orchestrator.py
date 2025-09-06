#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MULTI-AGENT ORCHESTRATOR WITH PERFORMANCE LEARNING
===================================================
Vereint alle Komponenten zu einem selbstlernenden System
"""

import json
import time
import sqlite3
import os
import sys
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Sichere Imports mit Fehlerbehandlung
try:
    from performance_tracker import PerformanceTracker
except ImportError as e:
    print(f"Warning: Could not import PerformanceTracker: {e}")
    # Dummy-Klasse als Fallback
    class PerformanceTracker:
        def __init__(self):
            pass
        def get_best_tool_for_task(self, task):
            return None
        def track_performance(self, **kwargs):
            pass
        def get_tool_performance(self, tool):
            return {"error": "Tracker not available"}
        def get_learning_report(self):
            return "Performance tracking not available"
        def track_combination(self, **kwargs):
            pass

try:
    from gemini_bridge import GeminiBridge
except ImportError as e:
    print(f"Warning: Could not import GeminiBridge: {e}")
    # Dummy-Klasse als Fallback
    class GeminiBridge:
        def __init__(self):
            pass
        def send_message(self, prompt, context):
            return "Gemini bridge not available"

class MultiAgentOrchestrator:
    """Master-Orchestrator fuer Multi-Agent System mit Learning"""
    
    def __init__(self):
        self.tracker = PerformanceTracker()
        self.gemini = GeminiBridge()
        
        # Agent-Definitionen ohne Umlaute
        self.agents = {
            "Claude": {
                "strengths": ["Creativity", "Ethics", "Nuanced Analysis"],
                "context_file": "claude_context.md",
                "api": "claude_api"  # Placeholder
            },
            "Deepseek": {
                "strengths": ["Code", "Technical Precision", "Debugging"],
                "context_file": "deepseek_context.md", 
                "api": "deepseek_api"  # Placeholder
            },
            "Gemini": {
                "strengths": ["Multimodal", "Research", "Facts"],
                "context_file": "gemini_context.md",
                "api": self.gemini  # Real Bridge!
            },
            "GPT5Max": {
                "strengths": ["Orchestration", "MCP Tools", "Safe Automation"],
                "context_file": "gpt5max_context.md",
                "api": "internal"
            }
        }
        
        # Lade SSOT
        self.ssot = self._load_ssot()
        
    def _load_ssot(self) -> str:
        """Load Single Source of Truth"""
        ssot_path = Path("ssot.md")
        if ssot_path.exists():
            try:
                return ssot_path.read_text(encoding='utf-8')
            except Exception as e:
                print(f"Warning: Could not load SSOT: {e}")
                return "# SSOT\nNo central context loaded."
        return "# SSOT\nNo central context loaded yet."
    
    def delegate_task(self, task: str, context: Optional[Dict] = None, force_analysis: bool = False) -> Dict[str, Any]:
        """Intelligente Task-Delegation mit Learning"""
        
        start_time = time.time()
        
        best_agent = None
        if not force_analysis:
            # 1. FRAGE PERFORMANCE TRACKER
            best_agent = self.tracker.get_best_tool_for_task(task)
        
        if not best_agent:
            # 2. FALLBACK/FORCIERT: Analysiere Task
            best_agent = self._analyze_task(task)
        
        print(f"Delegating to: {best_agent}")
        
        # 3. EXECUTE
        result = self._execute_with_agent(best_agent, task, context)
        
        # 4. TRACK PERFORMANCE
        execution_time = time.time() - start_time
        success = result.get("success", False)
        
        self.tracker.track_performance(
            tool_name=best_agent,
            task=task,
            result=result,
            execution_time=execution_time,
            success=success
        )
        
        # 5. Bei Multi-Agent: Konsens
        if context and context.get("use_consensus"):
            result = self._get_consensus(task, context)
        
        return {
            "agent": best_agent,
            "result": result,
            "execution_time": execution_time,
            "tracked": True
        }
    
    def _analyze_task(self, task: str) -> str:
        """Analyze task and choose best agent"""
        task_lower = task.lower()
        
        # Rule-based selection
        if any(word in task_lower for word in ["code", "debug", "implement", "fix", "generator", "python", "javascript"]):
            return "Deepseek"
        elif any(word in task_lower for word in ["ethisch", "ethics", "kreativ", "creative", "analyse", "analyze", "nuance"]):
            return "Claude"
        elif any(word in task_lower for word in ["recherch", "research", "fakten", "facts", "multimodal", "image", "bild"]):
            return "Gemini"
        else:
            # Default: Claude for general tasks
            return "Claude"
    
    def _build_prompt(self, agent: str, task: str) -> str:
        """Compose SSoT + niche context and include an SSoT checksum header."""
        full_context = f"{self.ssot}\n\n"
        # Kontextdatei mit Fallbacks (CLAUDE.md, GEMINI.md, DEEPSEEK.md)
        preferred = Path(self.agents[agent]["context_file"]) if agent in self.agents else None
        fallback_map = {
            "Claude": Path("CLAUDE.md"),
            "Gemini": Path("GEMINI.md"),
            "Deepseek": Path("DEEPSEEK.md"),
        }
        chosen_file = None
        for cand in [preferred, fallback_map.get(agent)]:
            if cand and cand.exists():
                chosen_file = cand
                break
        if chosen_file:
            try:
                full_context += chosen_file.read_text(encoding='utf-8')
            except Exception as e:
                print(f"Warning: Could not load {agent} context from {chosen_file}: {e}")
        ssot_hash = hashlib.sha256(self.ssot.encode('utf-8', errors='replace')).hexdigest()[:12]
        header = f"SSOT_ID: {ssot_hash}\nAGENT: {agent}\n"\
                 f"GUIDELINES: Follow SSoT + niche; ASCII-only; be concise.\n\n"
        return f"{header}{full_context}\n\nTASK: {task}"

    def _log_agent_response(self, agent: str, task: str, response: str, success: bool, elapsed: float) -> None:
        """Append a minimal JSON log line per agent execution (safe)."""
        try:
            ts = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            entry = {
                "ts": ts,
                "agent": agent,
                "task": task[:300],
                "success": success,
                "time_s": round(elapsed, 3),
                "response_preview": (response or "")[:500]
            }
            log_dir = Path("agent_responses")
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / (datetime.utcnow().strftime('%Y%m%d') + "_agent_runs.log")
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def _execute_with_agent(self, agent: str, task: str, context: Optional[Dict]) -> Dict:
        """Execute task with specific agent"""
        prompt = self._build_prompt(agent, task)
        
        # Execute based on agent
        if agent == "Gemini" and hasattr(self.gemini, 'send_message'):
            try:
                start = time.time()
                response = self.gemini.send_message(prompt, context)
                elapsed = time.time() - start
                self._log_agent_response(agent, task, str(response), True, elapsed)
                return {"success": True, "response": response}
            except Exception as e:
                self._log_agent_response(agent, task, f"Gemini error: {e}", False, 0.0)
                return {"success": False, "response": f"Gemini error: {e}"}
        elif agent in ("Claude", "Deepseek"):
            # Try via MCP delegate_task
            try:
                start = time.time()
                response = self._delegate_via_mcp(agent, prompt, context or {})
                elapsed = time.time() - start
                self._log_agent_response(agent, task, response, True, elapsed)
                return {"success": True, "response": response}
            except Exception as e:
                self._log_agent_response(agent, task, f"MCP delegate error: {e}", False, 0.0)
                return {"success": False, "response": f"MCP delegate error: {e}"}
        else:
            # Placeholder for other agents
            return {
                "success": True, 
                "response": f"[{agent}] would execute: {task}",
                "placeholder": True
            }

    def _delegate_via_mcp(self, agent: str, prompt: str, ctx: Dict) -> str:
        """Call MCP server's delegate_task with combined context (SSOT + niche)."""
        try:
            # Lazy import to avoid hard dependency at module import time
            from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer  # type: ignore
        except Exception as e:
            raise RuntimeError(f"Cannot import MCP server: {e}")

        # Map agent to target_agent prefix
        if agent.lower().startswith("claude"):
            target = "Claude:sonnet"
        elif agent.lower().startswith("deepseek"):
            target = "DeepSeek:chat"
        else:
            target = agent

        # Build task_description and context
        task_description = f"Use given context and answer the task concisely.\nContext follows.\n\n{prompt}"

        # Minimal async bridge
        import asyncio
        result_text: str = ""

        async def _run() -> None:
            nonlocal result_text
            server = HAKGALMCPServer()
            captured = []

            async def cap(resp):
                captured.append(resp)

            server.send_response = cap
            await server.handle_initialize({"id": 1})
            await server.handle_tool_call({
                "id": 2,
                "params": {
                    "name": "delegate_task",
                    "arguments": {
                        "target_agent": target,
                        "task_description": task_description,
                        "context": ctx
                    }
                }
            })
            for r in captured:
                if r.get("id") == 2:
                    items = (r.get("result") or {}).get("content") or []
                    for it in items:
                        if it.get("type") == "text":
                            result_text = it.get("text") or ""
                            return

        asyncio.run(_run())
        return result_text or ""
    
    def _get_consensus(self, task: str, context: Dict) -> Dict:
        """Get consensus from multiple agents"""
        results = []
        
        for agent_name in self.agents.keys():
            result = self._execute_with_agent(agent_name, task, context)
            results.append({
                "agent": agent_name,
                "response": result.get("response", ""),
                "confidence": 0.8
            })
        
        self.tracker.track_combination(
            task_pattern=task[:50],
            tools=list(self.agents.keys()),
            consensus_score=75.0,
            success=True
        )
        
        return {
            "consensus": True,
            "results": results,
            "agreement_score": 75.0
        }

    def consensus_run(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Run all agents on a task and compute a simple consensus (ASCII-only, safe)."""
        context = context or {}
        agent_outputs: Dict[str, str] = {}
        for agent_name in self.agents.keys():
            res = self._execute_with_agent(agent_name, task, context)
            agent_outputs[agent_name] = str(res.get("response", ""))

        # Simple token-based intersection as consensus hint
        def tokenize(s: str) -> set:
            import re
            return set(re.findall(r"[a-zA-Z0-9_]+", s.lower()))

        tokens = {k: tokenize(v) for k, v in agent_outputs.items()}
        common = set.intersection(*tokens.values()) if tokens else set()

        # Rank terms by frequency across agents
        from collections import Counter
        c = Counter()
        for t in tokens.values():
            for w in t:
                c[w] += 1
        top_terms = [w for w, n in c.most_common(20) if n >= 2]

        return {
            "task": task,
            "agents": agent_outputs,
            "consensus_terms": sorted(list(common))[:20],
            "top_shared_terms": top_terms
        }
    
    def get_system_status(self) -> str:
        """Show system status with learning metrics"""
        status = "=== MULTI-AGENT ORCHESTRATOR STATUS ===\n\n"
        
        # Agent Status
        status += "AGENTS:\n"
        for agent, info in self.agents.items():
            perf = self.tracker.get_tool_performance(agent)
            if "error" not in perf:
                success_rate = perf.get("success_rate", 0)
                total_runs = perf.get("total_runs", 0)
                status += f"  {agent}: {total_runs} runs, {success_rate:.1f}% success\n"
            else:
                status += f"  {agent}: No data yet\n"
        
        # Learning Report
        status += "\n" + self.tracker.get_learning_report()
        
        # System Health
        status += "\n=== SYSTEM HEALTH ===\n"
        status += f"SSOT loaded: {len(self.ssot)} chars\n"
        status += f"Gemini Bridge: {'Connected' if hasattr(self.gemini, 'send_message') else 'Not connected'}\n"
        status += f"Performance Tracking: Active\n"
        
        return status
    
    def run_test_suite(self):
        """Run test suite"""
        print("STARTING MULTI-AGENT TEST SUITE\n")
        print("="*60)
        
        test_tasks = [
            ("Implementiere einen Fibonacci-Generator", {"expected_agent": "Deepseek"}),
            ("Analysiere die ethischen Implikationen von KI", {"expected_agent": "Claude"}),
            ("Recherchiere aktuelle Fakten ueber Quantencomputer", {"expected_agent": "Gemini"}),
            ("Debugge diesen Python Code", {"expected_agent": "Deepseek"}),
            ("Schreibe ein kreatives Gedicht", {"expected_agent": "Claude"})
        ]
        
        correct = 0
        total = len(test_tasks)
        
        for task, meta in test_tasks:
            print(f"\nTASK: {task}")
            print(f"   Expected: {meta['expected_agent']}")
            
            result = self.delegate_task(task, force_analysis=True)
            
            print(f"   Selected: {result['agent']}")
            print(f"   Time: {result['execution_time']:.3f}s")
            print(f"   Tracked: {result['tracked']}")
            
            if result['agent'] == meta['expected_agent']:
                print("   --> CORRECT DELEGATION")
                correct += 1
            else:
                print("   --> WRONG DELEGATION")
        
        print("\n" + "="*60)
        print(f"TEST RESULTS: {correct}/{total} correct ({correct/total*100:.1f}%)")
        print("="*60)
        print("\n" + self.get_system_status())

# CLI
if __name__ == "__main__":
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("Error: Python 3.7+ required")
        sys.exit(1)
    
    orchestrator = MultiAgentOrchestrator()
    
    if "--test" in sys.argv:
        orchestrator.run_test_suite()
    elif "--status" in sys.argv:
        print(orchestrator.get_system_status())
    elif "--delegate" in sys.argv:
        if len(sys.argv) > sys.argv.index("--delegate") + 1:
            task = " ".join(sys.argv[sys.argv.index("--delegate")+1:])
            result = orchestrator.delegate_task(task)
            print(json.dumps(result, indent=2))
        else:
            print("Error: No task specified after --delegate")
    elif "--consensus" in sys.argv:
        if len(sys.argv) > sys.argv.index("--consensus") + 1:
            task = " ".join(sys.argv[sys.argv.index("--consensus")+1:])
            out = orchestrator.consensus_run(task)
            print(json.dumps(out, indent=2))
        else:
            print("Error: No task specified after --consensus")
    else:
        # Interactive mode
        print("="*60)
        print("MULTI-AGENT ORCHESTRATOR - Interactive Mode")
        print("="*60)
        print("Commands: 'exit', 'status', 'test', or enter a task")
        print("-" * 60)
        
        while True:
            try:
                user_input = input("\nTask> ").strip()
                
                if user_input.lower() == 'exit':
                    break
                elif user_input.lower() == 'status':
                    print(orchestrator.get_system_status())
                elif user_input.lower() == 'test':
                    orchestrator.run_test_suite()
                else:
                    result = orchestrator.delegate_task(user_input)
                    print(f"\nAgent: {result['agent']}")
                    print(f"Response: {result['result']}")
                    print(f"Time: {result['execution_time']:.3f}s")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")