#!/usr/bin/env python3
"""
HAK/GAL Diagnostics Integration Server
=====================================

Integration zwischen:
- HAK/GAL API (Port 5002)
- Agent Diagnostics Server (Port 5000)
- Knowledge Base für Agent-Metriken

Gemäß HAK/GAL Verfassung Artikel 3 (Externe Verifikation)
und Artikel 6 (Empirische Validierung)
"""

import requests
import json
import time
import os
from datetime import datetime
from pathlib import Path
import sqlite3
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hakgal_diagnostics.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HAKGALDiagnosticsIntegration:
    """Integration zwischen Diagnostics Server und HAK/GAL API"""

    def __init__(self):
        self.hakgal_api = "http://localhost:5002"
        self.diagnostics_port = 5000
        self.api_key = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

        # Exchange directories (as mentioned by Claude Opus)
        self.exchange_dirs = {
            "cursor": Path("cursor_exchange"),
            "claude_cli": Path("claude_cli_exchange"),
            "claude_desktop": Path("claude_desktop_exchange")
        }

        # Response logging structure
        self.response_dir = Path("agent_responses")
        self.success_dir = self.response_dir / "success"
        self.error_dir = self.response_dir / "error"
        self.by_agent_dir = self.response_dir / "by_agent"

        # Ensure directories exist
        for dir_path in [self.success_dir, self.error_dir, self.by_agent_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        logger.info("HAK/GAL Diagnostics Integration initialized")

    def test_hakgal_connection(self):
        """Test connection to HAK/GAL API"""
        try:
            response = requests.get(
                f"{self.hakgal_api}/api/status",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                logger.info("SUCCESS: HAK/GAL API connection successful")
                return True
            else:
                logger.error(f"ERROR: HAK/GAL API connection failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"ERROR: HAK/GAL API connection error: {e}")
            return False

    def get_agent_status_from_kb(self):
        """Retrieve agent status facts from Knowledge Base"""
        try:
            # Query Knowledge Base for agent-related facts
            conn = sqlite3.connect('hexagonal_kb.db')
            cursor = conn.cursor()

            cursor.execute('''
                SELECT subject, predicate, object
                FROM facts
                WHERE (LOWER(subject) LIKE '%agent%' OR LOWER(object) LIKE '%agent%')
                   OR (LOWER(subject) LIKE '%claude%' OR LOWER(object) LIKE '%claude%')
                   OR (LOWER(subject) LIKE '%gemini%' OR LOWER(object) LIKE '%gemini%')
                   OR (LOWER(subject) LIKE '%cursor%' OR LOWER(object) LIKE '%cursor%')
                ORDER BY rowid DESC
                LIMIT 20
            ''')

            agent_facts = cursor.fetchall()
            conn.close()

            logger.info(f"Retrieved {len(agent_facts)} agent-related facts from KB")
            return agent_facts

        except Exception as e:
            logger.error(f"Error retrieving agent facts from KB: {e}")
            return []

    def log_agent_metric_to_kb(self, agent_name, metric_type, value, context=""):
        """Log agent metrics to Knowledge Base (Artikel 6: Empirische Validierung)"""
        try:
            timestamp = datetime.now().isoformat()

            fact_statement = f"AgentMetric({agent_name}, {metric_type}, {value}, '{timestamp}')"

            payload = {
                "statement": fact_statement,
                "source": "diagnostics_integration",
                "tags": ["agent", "metric", metric_type],
                "auth_token": "515f57956e7bd15ddc3817573598f190"
            }

            response = requests.post(
                f"{self.hakgal_api}/api/knowledge/add-fact",
                headers=self.headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"SUCCESS: Logged metric to KB: {agent_name} {metric_type}={value}")
                return True
            else:
                logger.error(f"ERROR: Failed to log metric to KB: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error logging metric to KB: {e}")
            return False

    def run_agent_diagnostic(self, agent_name):
        """Run diagnostic test for specific agent"""
        logger.info(f"Running diagnostic for agent: {agent_name}")

        # Test agent delegation
        payload = {
            "target_agent": agent_name,
            "task_description": f"Diagnostic test for {agent_name} - respond with 'OK'",
            "context": {
                "diagnostic": True,
                "timestamp": datetime.now().isoformat()
            }
        }

        try:
            start_time = time.time()
            response = requests.post(
                f"{self.hakgal_api}/api/agent-bus/delegate",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            end_time = time.time()

            response_time = end_time - start_time

            if response.status_code == 200:
                result = response.json()
                status = "success"
                response_length = len(result.get("response", ""))

                # Log to Knowledge Base
                self.log_agent_metric_to_kb(agent_name, "response_time", f"{response_time:.2f}s")
                self.log_agent_metric_to_kb(agent_name, "response_length", response_length)
                self.log_agent_metric_to_kb(agent_name, "status", "operational")

                # Save response to file system
                self.save_response_to_filesystem(agent_name, result, status)

                logger.info(f"SUCCESS: {agent_name} diagnostic successful ({response_time:.2f}s)")
                return {
                    "agent": agent_name,
                    "status": "success",
                    "response_time": response_time,
                    "response_length": response_length
                }

            else:
                status = "error"
                error_msg = response.text

                # Log error to Knowledge Base
                self.log_agent_metric_to_kb(agent_name, "status", "error")
                self.log_agent_metric_to_kb(agent_name, "error", error_msg[:100])

                # Save error to file system
                self.save_response_to_filesystem(agent_name, {"error": error_msg}, status)

                logger.error(f"ERROR: {agent_name} diagnostic failed: {response.status_code}")
                return {
                    "agent": agent_name,
                    "status": "error",
                    "error": error_msg
                }

        except Exception as e:
            logger.error(f"ERROR: {agent_name} diagnostic error: {e}")
            self.log_agent_metric_to_kb(agent_name, "status", "exception")
            return {
                "agent": agent_name,
                "status": "exception",
                "error": str(e)
            }

    def save_response_to_filesystem(self, agent_name, response_data, status):
        """Save response to file system structure"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{agent_name}_{timestamp}.json"

            # Save to status directory
            if status == "success":
                filepath = self.success_dir / filename
            else:
                filepath = self.error_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, indent=2, ensure_ascii=False)

            # Save to agent-specific directory
            agent_dir = self.by_agent_dir / agent_name
            agent_dir.mkdir(exist_ok=True)
            agent_filepath = agent_dir / filename

            with open(agent_filepath, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved response to filesystem: {filepath}")

        except Exception as e:
            logger.error(f"Error saving response to filesystem: {e}")

    def check_exchange_directories(self):
        """Check exchange directories for new files (as mentioned by Claude Opus)"""
        logger.info("Checking exchange directories...")

        for agent_name, dir_path in self.exchange_dirs.items():
            if dir_path.exists():
                files = list(dir_path.glob("*"))
                logger.info(f"{agent_name}: {len(files)} files in exchange directory")

                # Log to Knowledge Base
                self.log_agent_metric_to_kb(agent_name, "exchange_files", len(files))
            else:
                logger.warning(f"{agent_name}: Exchange directory not found: {dir_path}")

    def generate_diagnostic_report(self):
        """Generate comprehensive diagnostic report"""
        logger.info("Generating diagnostic report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "hakgal_connection": self.test_hakgal_connection(),
            "agent_facts_from_kb": len(self.get_agent_status_from_kb()),
            "exchange_directories": {}
        }

        # Check exchange directories
        for agent_name, dir_path in self.exchange_dirs.items():
            report["exchange_directories"][agent_name] = {
                "exists": dir_path.exists(),
                "file_count": len(list(dir_path.glob("*"))) if dir_path.exists() else 0
            }

        # Save report
        report_path = Path("diagnostic_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Diagnostic report saved to: {report_path}")
        return report

    def run_full_diagnostic_suite(self):
        """Run complete diagnostic suite for all agents"""
        logger.info("=== STARTING FULL DIAGNOSTIC SUITE ===")

        agents_to_test = ["gemini", "claude_cli", "cursor", "claude_desktop"]
        results = []

        for agent in agents_to_test:
            logger.info(f"Testing agent: {agent}")
            result = self.run_agent_diagnostic(agent)
            results.append(result)
            time.sleep(2)  # Brief pause between tests

        # Check exchange directories
        self.check_exchange_directories()

        # Generate report
        report = self.generate_diagnostic_report()

        # Summary
        successful = [r for r in results if r["status"] == "success"]
        failed = [r for r in results if r["status"] != "success"]

        logger.info("=== DIAGNOSTIC SUITE COMPLETE ===")
        logger.info(f"Successful: {len(successful)}/{len(agents_to_test)}")
        logger.info(f"Failed: {len(failed)}/{len(agents_to_test)}")

        if successful:
            avg_time = sum(r.get("response_time", 0) for r in successful) / len(successful)
            logger.info(f"Average response time: {avg_time:.2f}s")

        return {
            "results": results,
            "report": report,
            "summary": {
                "total_agents": len(agents_to_test),
                "successful": len(successful),
                "failed": len(failed)
            }
        }

def main():
    """Main function"""
    print("HAK/GAL Diagnostics Integration Server")
    print("=" * 50)

    integration = HAKGALDiagnosticsIntegration()

    # Test connection
    if not integration.test_hakgal_connection():
        print("ERROR: Cannot connect to HAK/GAL API. Please ensure it's running on port 5002.")
        return

    # Run full diagnostic suite
    results = integration.run_full_diagnostic_suite()

    # Print summary
    print("\nDIAGNOSTIC RESULTS SUMMARY:")
    print("-" * 30)

    for result in results["results"]:
        status_icon = "SUCCESS" if result["status"] == "success" else "ERROR"
        if result["status"] == "success":
            time_str = f"{result.get('response_time', 0):.2f}s"
            print(f"{status_icon}: {result['agent']}: {time_str}")
        else:
            print(f"{status_icon}: {result['agent']}: {result['status']}")

    print(f"\nOverall: {results['summary']['successful']}/{results['summary']['total_agents']} agents operational")

    # Check Knowledge Base integration
    kb_facts = integration.get_agent_status_from_kb()
    print(f"Knowledge Base: {len(kb_facts)} agent-related facts stored")

    print("\nIntegration Features:")
    print("   - Agent metrics logged to Knowledge Base")
    print("   - Responses saved to filesystem structure")
    print("   - Exchange directories monitored")
    print("   - Real-time diagnostic reports generated")

if __name__ == "__main__":
    main()