# ASCII-only Performance Tracker
import json, time, os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class PerformanceTracker:
    def __init__(self, base_dir: Optional[str] = None) -> None:
        self.base_dir = Path(base_dir or '.') / 'performance'
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.base_dir / 'perf_log.jsonl'
        self.summary_path = self.base_dir / 'perf_summary.json'
        if not self.summary_path.exists():
            self._write_summary({"tools": {}, "combos": {}})

    def _read_summary(self) -> Dict[str, Any]:
        try:
            return json.loads(self.summary_path.read_text(encoding='utf-8'))
        except Exception:
            return {"tools": {}, "combos": {}}

    def _write_summary(self, data: Dict[str, Any]) -> None:
        self.summary_path.write_text(json.dumps(data, ensure_ascii=True, indent=2), encoding='ascii')

    def _append_log(self, entry: Dict[str, Any]) -> None:
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=True) + "\n")

    def track_performance(self, tool_name: str, task: str, result: Dict[str, Any], execution_time: float, success: bool) -> None:
        ts = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        entry = {
            "ts": ts,
            "tool": tool_name,
            "task": task[:200],
            "success": bool(success),
            "time_s": round(execution_time, 6),
            "response_size": len(str(result.get('response', '')))
        }
        self._append_log(entry)
        # update summary
        s = self._read_summary()
        t = s.setdefault('tools', {}).setdefault(tool_name, {"total_runs": 0, "success_runs": 0, "avg_time_s": 0.0})
        t['total_runs'] += 1
        if success:
            t['success_runs'] += 1
        # incremental average
        n = t['total_runs']
        t['avg_time_s'] = round(((t['avg_time_s'] * (n - 1)) + execution_time) / max(1, n), 6)
        self._write_summary(s)

    def track_combination(self, task_pattern: str, tools: list, consensus_score: float, success: bool) -> None:
        ts = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        entry = {
            "ts": ts,
            "combo": tools,
            "task_pattern": task_pattern,
            "consensus_score": consensus_score,
            "success": bool(success)
        }
        self._append_log(entry)
        s = self._read_summary()
        c = s.setdefault('combos', {})
        key = '+'.join(sorted(tools))[:120]
        rec = c.setdefault(key, {"runs": 0, "avg_consensus": 0.0, "success_runs": 0})
        rec['runs'] += 1
        if success:
            rec['success_runs'] += 1
        n = rec['runs']
        rec['avg_consensus'] = round(((rec['avg_consensus'] * (n - 1)) + consensus_score) / max(1, n), 3)
        self._write_summary(s)

    def get_tool_performance(self, tool: str) -> Dict[str, Any]:
        s = self._read_summary()
        t = s.get('tools', {}).get(tool)
        if not t:
            return {"total_runs": 0, "success_rate": 0.0, "avg_time_s": 0.0}
        total = t.get('total_runs', 0)
        succ = t.get('success_runs', 0)
        rate = (succ / total * 100.0) if total else 0.0
        return {"total_runs": total, "success_rate": round(rate, 1), "avg_time_s": t.get('avg_time_s', 0.0)}

    def get_best_tool_for_task(self, task: str) -> Optional[str]:
        # naive heuristic: choose tool with highest success_rate then lowest avg_time
        s = self._read_summary().get('tools', {})
        if not s:
            return None
        items = []
        for name, rec in s.items():
            total = rec.get('total_runs', 0)
            if total == 0:
                continue
            rate = (rec.get('success_runs', 0) / total) if total else 0.0
            items.append((rate, -rec.get('avg_time_s', 0.0), name))
        if not items:
            return None
        items.sort(reverse=True)
        return items[0][2]

    def get_learning_report(self) -> str:
        s = self._read_summary()
        lines = ["=== LEARNING REPORT ==="]
        tools = s.get('tools', {})
        if not tools:
            lines.append("No data yet")
        else:
            for name, rec in tools.items():
                total = rec.get('total_runs', 0)
                succ = rec.get('success_runs', 0)
                rate = (succ / total * 100.0) if total else 0.0
                lines.append(f"- {name}: runs={total}, success={rate:.1f}%, avg_time_s={rec.get('avg_time_s', 0.0):.3f}")
        return "\n".join(lines)
