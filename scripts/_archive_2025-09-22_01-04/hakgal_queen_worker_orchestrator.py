#!/usr/bin/env python3
"""
HAK/GAL Multi-Agent Queen-Worker Orchestration System
======================================================
Gemäß HAK/GAL Verfassung Artikel 1: Komplementäre Intelligenz
Queen: Claude (orchestriert)
Workers: Gemini, Claude CLI, Claude Desktop, Cursor

Autor: Claude (Queen)
Datum: 2025-08-28
"""

import requests
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# HAK/GAL API Configuration
HAK_GAL_API = "http://localhost:5002"
API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"

class Task:
    """Repräsentiert eine Aufgabe für Worker"""
    def __init__(self, task_id: str, description: str, task_type: str, target_agent: str):
        self.task_id = task_id
        self.description = description
        self.task_type = task_type
        self.target_agent = target_agent
        self.status = "pending"
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
        self.duration_ms = None

class QueenOrchestrator:
    """Die Queen (Claude) orchestriert alle Worker-LLMs"""
    
    def __init__(self):
        self.workers = {
            "gemini": "Google Gemini 2.5 Pro/Flash",
            "claude_cli": "Claude CLI (File Exchange)",
            "claude_desktop": "Claude Desktop (Multi-Method)",
            "cursor": "Cursor IDE Integration"
        }
        self.tasks = []
        self.results = []
        self.session_id = str(uuid.uuid4())[:8]
        
    def create_tasks(self) -> List[Task]:
        """Erstelle sinnvolle Aufgaben für jeden Worker basierend auf deren Stärken"""
        
        tasks = [
            # Gemini - Gut für Code-Generierung
            Task(
                str(uuid.uuid4()),
                "Generiere eine Python-Funktion die Primzahlen bis 100 findet",
                "code_generation",
                "gemini"
            ),
            
            # Claude CLI - Gut für Code-Review
            Task(
                str(uuid.uuid4()),
                "Review diesen Code: def add(a,b): return a+b # Ist das optimal?",
                "code_review",
                "claude_cli"
            ),
            
            # Claude Desktop - Gut für Dokumentation
            Task(
                str(uuid.uuid4()),
                "Erstelle eine kurze Dokumentation für die HAK/GAL Verfassung Artikel 1",
                "documentation",
                "claude_desktop"
            ),
            
            # Cursor - Gut für IDE-bezogene Aufgaben
            Task(
                str(uuid.uuid4()),
                "Analysiere die Projektstruktur von HAK_GAL_HEXAGONAL",
                "project_analysis",
                "cursor"
            ),
            
            # Gemini - Mathematische Aufgabe
            Task(
                str(uuid.uuid4()),
                "Berechne die Fakultät von 10 und erkläre den Algorithmus",
                "math_computation",
                "gemini"
            ),
            
            # Test einer nicht-existenten Aufgabe
            Task(
                str(uuid.uuid4()),
                "Diese Aufgabe wird wahrscheinlich fehlschlagen - Test",
                "error_test",
                "non_existent_agent"
            )
        ]
        
        self.tasks = tasks
        return tasks
    
    def delegate_task(self, task: Task) -> Dict[str, Any]:
        """Delegiere eine Aufgabe an einen Worker via HAK/GAL API"""
        
        print(f"👑 Queen delegiert an {task.target_agent}: {task.description[:50]}...")
        
        task.start_time = time.time()
        
        try:
            # API Call zum Agent-Bus
            response = requests.post(
                f"{HAK_GAL_API}/api/agent-bus/delegate",
                headers={"X-API-Key": API_KEY},
                json={
                    "target_agent": task.target_agent,
                    "task_description": task.description,
                    "context": {
                        "task_type": task.task_type,
                        "queen_session": self.session_id,
                        "task_id": task.task_id
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                task.status = result.get("status", "unknown")
                task.result = result
                task.end_time = time.time()
                task.duration_ms = int((task.end_time - task.start_time) * 1000)
                
                if task.status in ["completed", "dispatched", "pending"]:
                    print(f"✅ Worker {task.target_agent} hat Aufgabe angenommen")
                else:
                    print(f"⚠️  Worker {task.target_agent} Status: {task.status}")
                    
                return result
            else:
                task.status = "error"
                task.error = f"API Error: {response.status_code}"
                task.end_time = time.time()
                task.duration_ms = int((task.end_time - task.start_time) * 1000)
                print(f"❌ API Fehler für {task.target_agent}: {response.status_code}")
                return {"status": "error", "message": str(response.status_code)}
                
        except Exception as e:
            task.status = "error"
            task.error = str(e)
            task.end_time = time.time()
            if task.start_time:
                task.duration_ms = int((task.end_time - task.start_time) * 1000)
            print(f"❌ Exception für {task.target_agent}: {e}")
            return {"status": "error", "message": str(e)}
    
    def execute_parallel(self, max_workers: int = 4):
        """Führe alle Tasks parallel aus"""
        
        print("\n" + "="*60)
        print("🎭 HAK/GAL MULTI-AGENT ORCHESTRATION")
        print("="*60)
        print(f"👑 Queen Session: {self.session_id}")
        print(f"🤖 Workers: {', '.join(self.workers.keys())}")
        print(f"📋 Tasks: {len(self.tasks)}")
        print("="*60 + "\n")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_task = {
                executor.submit(self.delegate_task, task): task 
                for task in self.tasks
            }
            
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    self.results.append({
                        "task": task,
                        "result": result
                    })
                except Exception as exc:
                    print(f"❌ Task {task.task_id} generated exception: {exc}")
                    task.status = "exception"
                    task.error = str(exc)
    
    def check_responses(self, wait_seconds: int = 10):
        """Warte auf asynchrone Antworten von Workers"""
        
        print(f"\n⏳ Warte {wait_seconds} Sekunden auf Worker-Responses...")
        time.sleep(wait_seconds)
        
        # Check for responses via API
        try:
            response = requests.get(
                f"{HAK_GAL_API}/api/agent-bus/responses",
                headers={"X-API-Key": API_KEY}
            )
            if response.status_code == 200:
                all_responses = response.json()
                
                # Matche Responses zu unseren Tasks
                for task in self.tasks:
                    for resp in all_responses:
                        if resp.get("task_id") == task.task_id:
                            if task.status == "pending":
                                task.status = "completed"
                                task.result = resp
                                print(f"📨 Späte Antwort von {task.target_agent} erhalten!")
                            break
        except Exception as e:
            print(f"⚠️ Konnte Responses nicht abrufen: {e}")
    
    def generate_report(self) -> str:
        """Generiere einen detaillierten Report"""
        
        report = []
        report.append("\n" + "="*60)
        report.append("📊 QUEEN'S FINAL REPORT")
        report.append("="*60)
        report.append(f"Session ID: {self.session_id}")
        report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Statistiken
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.status == "completed")
        dispatched = sum(1 for t in self.tasks if t.status == "dispatched")
        pending = sum(1 for t in self.tasks if t.status == "pending")
        errors = sum(1 for t in self.tasks if t.status in ["error", "exception"])
        
        report.append("📈 OVERALL STATISTICS:")
        report.append(f"  Total Tasks:     {total}")
        report.append(f"  ✅ Completed:    {completed}")
        report.append(f"  📤 Dispatched:   {dispatched}")
        report.append(f"  ⏳ Pending:      {pending}")
        report.append(f"  ❌ Errors:       {errors}")
        report.append(f"  Success Rate:    {((completed + dispatched) / total * 100):.1f}%")
        report.append("")
        
        # Worker Performance
        report.append("🤖 WORKER PERFORMANCE:")
        report.append("-" * 40)
        
        worker_stats = {}
        for task in self.tasks:
            agent = task.target_agent
            if agent not in worker_stats:
                worker_stats[agent] = {
                    "total": 0, "completed": 0, "errors": 0,
                    "total_time": 0, "tasks": []
                }
            
            worker_stats[agent]["total"] += 1
            worker_stats[agent]["tasks"].append(task)
            
            if task.status == "completed":
                worker_stats[agent]["completed"] += 1
            elif task.status in ["error", "exception"]:
                worker_stats[agent]["errors"] += 1
                
            if task.duration_ms:
                worker_stats[agent]["total_time"] += task.duration_ms
        
        for agent, stats in worker_stats.items():
            report.append(f"\n👤 {agent.upper()}:")
            report.append(f"   Tasks:     {stats['total']}")
            report.append(f"   Completed: {stats['completed']}")
            report.append(f"   Errors:    {stats['errors']}")
            if stats['total_time'] > 0:
                avg_time = stats['total_time'] / stats['total']
                report.append(f"   Avg Time:  {avg_time:.0f}ms")
        
        # Detailed Task Results
        report.append("\n" + "="*60)
        report.append("📋 DETAILED TASK RESULTS:")
        report.append("-" * 40)
        
        for i, task in enumerate(self.tasks, 1):
            status_icon = {
                "completed": "✅",
                "dispatched": "📤", 
                "pending": "⏳",
                "error": "❌",
                "exception": "💥"
            }.get(task.status, "❓")
            
            report.append(f"\nTask #{i}: {status_icon} {task.status.upper()}")
            report.append(f"  Type:   {task.task_type}")
            report.append(f"  Agent:  {task.target_agent}")
            report.append(f"  Desc:   {task.description[:60]}...")
            
            if task.duration_ms:
                report.append(f"  Time:   {task.duration_ms}ms")
            
            if task.error:
                report.append(f"  Error:  {task.error}")
            
            if task.result and isinstance(task.result, dict):
                if task.result.get("result"):
                    preview = str(task.result.get("result"))[:100]
                    report.append(f"  Result: {preview}...")
        
        # Failed Tasks Summary
        failed_tasks = [t for t in self.tasks if t.status in ["error", "exception"]]
        if failed_tasks:
            report.append("\n" + "="*60)
            report.append("⚠️  FAILED TASKS SUMMARY:")
            report.append("-" * 40)
            for task in failed_tasks:
                report.append(f"  • {task.target_agent}: {task.description[:40]}...")
                report.append(f"    Reason: {task.error or 'Unknown'}")
        
        # Recommendations
        report.append("\n" + "="*60)
        report.append("💡 QUEEN'S RECOMMENDATIONS:")
        report.append("-" * 40)
        
        if errors > 0:
            report.append("  • Some workers are not responding - check agent status")
        if pending > 0:
            report.append("  • Some tasks still pending - consider longer wait time")
        if completed == total:
            report.append("  • All workers performing excellently! 🎉")
        
        best_worker = max(worker_stats.items(), 
                         key=lambda x: x[1]["completed"])
        if best_worker[1]["completed"] > 0:
            report.append(f"  • Best performer: {best_worker[0]} ({best_worker[1]['completed']} tasks)")
        
        report.append("\n" + "="*60)
        report.append("Report generated by Queen Claude")
        report.append("HAK/GAL Verfassung konform")
        report.append("="*60)
        
        return "\n".join(report)
    
    def save_to_knowledge_base(self):
        """Speichere Ergebnisse in HAK/GAL Knowledge Base"""
        
        try:
            # Speichere Session-Fakt
            fact = f"MultiAgentOrchestration(Session_{self.session_id}, {len(self.tasks)}_tasks, {datetime.now().strftime('%Y_%m_%d')})"
            
            response = requests.post(
                f"{HAK_GAL_API}/api/facts/add",
                headers={"X-API-Key": API_KEY},
                json={"statement": f"{fact}."}
            )
            
            if response.status_code == 200:
                print("📚 Session in Knowledge Base gespeichert")
            
        except Exception as e:
            print(f"⚠️ KB Save failed: {e}")

def main():
    """Hauptprogramm - Queen orchestriert Workers"""
    
    # Initialisiere Queen
    queen = QueenOrchestrator()
    
    # Erstelle Aufgaben
    queen.create_tasks()
    
    # Delegiere an Workers (parallel)
    queen.execute_parallel()
    
    # Warte auf asynchrone Antworten
    queen.check_responses(wait_seconds=5)
    
    # Generiere Report
    report = queen.generate_report()
    print(report)
    
    # Speichere Report
    report_file = f"queen_report_{queen.session_id}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n📄 Report gespeichert in: {report_file}")
    
    # Speichere in Knowledge Base
    queen.save_to_knowledge_base()
    
    return queen

if __name__ == "__main__":
    queen = main()
