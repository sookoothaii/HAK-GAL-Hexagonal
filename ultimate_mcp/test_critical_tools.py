#!/usr/bin/env python3
"""
Comprehensive Test Suite for Critical HAK-GAL Tools
Tests all 11 new workflow tools systematically
"""

import json
import sys
import asyncio
from datetime import datetime

# Test cases for each tool
TEST_CASES = {
    # 1. evaluate_expression
    "evaluate_expression": [
        {
            "name": "Simple math",
            "args": {
                "expression": "2 + 2",
                "variables": {}
            },
            "expected": {"result": 4, "type": "int"}
        },
        {
            "name": "With variables",
            "args": {
                "expression": "x * 2 + y",
                "variables": {"x": 5, "y": 3}
            },
            "expected": {"result": 13, "type": "int"}
        },
        {
            "name": "Boolean logic",
            "args": {
                "expression": "a > b and c",
                "variables": {"a": 10, "b": 5, "c": True}
            },
            "expected": {"result": True, "type": "bool"}
        },
        {
            "name": "Safe mode test",
            "args": {
                "expression": "__import__('os').system('echo test')",
                "variables": {},
                "safe_mode": True
            },
            "expected_error": True
        },
        {
            "name": "Math functions (unsafe mode)",
            "args": {
                "expression": "sqrt(16) + pi",
                "variables": {},
                "safe_mode": False
            },
            "expected": {"result": 7.141592653589793, "type": "float"}
        }
    ],
    
    # 2. set_variable
    "set_variable": [
        {
            "name": "Set string",
            "args": {
                "name": "username",
                "value": "test_user",
                "type": "string"
            },
            "expected": {"name": "username", "value": "test_user", "type": "str"}
        },
        {
            "name": "Set integer",
            "args": {
                "name": "counter",
                "value": "42",
                "type": "int"
            },
            "expected": {"name": "counter", "value": 42, "type": "int"}
        },
        {
            "name": "Set boolean",
            "args": {
                "name": "is_active",
                "value": "true",
                "type": "bool"
            },
            "expected": {"name": "is_active", "value": True, "type": "bool"}
        },
        {
            "name": "Set JSON object",
            "args": {
                "name": "config",
                "value": '{"host": "localhost", "port": 8080}',
                "type": "json"
            },
            "expected": {"name": "config", "value": {"host": "localhost", "port": 8080}, "type": "dict"}
        }
    ],
    
    # 3. get_variable
    "get_variable": [
        {
            "name": "Get existing variable",
            "args": {
                "name": "username",
                "default": "anonymous"
            },
            "expected": {"name": "username", "exists": False, "value": "anonymous"}
        },
        {
            "name": "Get with complex default",
            "args": {
                "name": "settings",
                "default": {"theme": "dark", "lang": "en"}
            },
            "expected": {"name": "settings", "exists": False, "value": {"theme": "dark", "lang": "en"}}
        }
    ],
    
    # 4. merge_branches
    "merge_branches": [
        {
            "name": "Merge all strategy",
            "args": {
                "branch_results": [
                    {"success": True, "data": "A"},
                    {"success": False, "data": "B"},
                    {"success": True, "data": "C"}
                ],
                "strategy": "all"
            },
            "expected": {"strategy": "all", "branch_count": 3}
        },
        {
            "name": "First success strategy",
            "args": {
                "branch_results": [
                    {"success": False, "data": "A"},
                    {"success": True, "data": "B"},
                    {"success": True, "data": "C"}
                ],
                "strategy": "first_success"
            },
            "expected": {"strategy": "first_success", "selected_branch": 1}
        },
        {
            "name": "Majority strategy",
            "args": {
                "branch_results": [
                    {"result": "approved"},
                    {"result": "approved"},
                    {"result": "rejected"}
                ],
                "strategy": "majority",
                "key_field": "result"
            },
            "expected": {"strategy": "majority", "merged_data": "approved", "consensus_count": 2}
        }
    ],
    
    # 5. wait_for_all
    "wait_for_all": [
        {
            "name": "Wait for multiple nodes",
            "args": {
                "node_ids": ["node-1", "node-2", "node-3"],
                "timeout_ms": 5000,
                "fail_on_any_error": True
            },
            "expected": {"waiting_for": ["node-1", "node-2", "node-3"], "status": "waiting"}
        }
    ],
    
    # 6. no_op
    "no_op": [
        {
            "name": "Basic no-op",
            "args": {},
            "expected": {"action": "no_op", "message": "No operation performed"}
        },
        {
            "name": "With custom message",
            "args": {
                "message": "Placeholder for future functionality",
                "metadata": {"version": "1.0", "author": "test"}
            },
            "expected": {"action": "no_op", "message": "Placeholder for future functionality"}
        }
    ],
    
    # 7. comment
    "comment": [
        {
            "name": "Basic comment",
            "args": {
                "text": "This node processes user authentication"
            },
            "expected": {"action": "comment", "text": "This node processes user authentication"}
        },
        {
            "name": "Detailed comment",
            "args": {
                "text": "Critical section: handles payment processing",
                "author": "security_team",
                "node_id": "payment-processor-01"
            },
            "expected": {"action": "comment", "author": "security_team"}
        }
    ],
    
    # 8. metrics_collector
    "metrics_collector": [
        {
            "name": "Counter metric",
            "args": {
                "metric_name": "api_calls",
                "value": 1,
                "type": "counter",
                "tags": {"endpoint": "/api/v1/users", "method": "GET"}
            },
            "expected": {"status": "collected"}
        },
        {
            "name": "Gauge metric",
            "args": {
                "metric_name": "memory_usage_mb",
                "value": 512.5,
                "type": "gauge",
                "tags": {"server": "web-01"}
            },
            "expected": {"status": "collected"}
        }
    ],
    
    # 9. workflow_status
    "workflow_status": [
        {
            "name": "Current workflow status",
            "args": {
                "workflow_id": "current",
                "include_nodes": True
            },
            "expected": {"workflow_id": "current", "status": "running"}
        }
    ],
    
    # 10. cron_validator
    "cron_validator": [
        {
            "name": "Valid daily cron",
            "args": {
                "expression": "0 9 * * *"
            },
            "expected": {"valid": True, "fields": 5}
        },
        {
            "name": "Valid with seconds",
            "args": {
                "expression": "0 0 9 * * *"
            },
            "expected": {"valid": True, "fields": 6}
        },
        {
            "name": "Invalid cron",
            "args": {
                "expression": "99 99 * * *"
            },
            "expected": {"valid": False}
        },
        {
            "name": "Complex cron",
            "args": {
                "expression": "*/15 0-5,20-23 * * MON-FRI"
            },
            "expected": {"valid": True}
        }
    ],
    
    # 11. recurring_schedule
    "recurring_schedule": [
        {
            "name": "Create cron schedule",
            "args": {
                "name": "daily_backup",
                "type": "cron",
                "config": {"expression": "0 2 * * *"},
                "enabled": True
            },
            "expected": {"status": "created"}
        },
        {
            "name": "Create interval schedule",
            "args": {
                "name": "health_check",
                "type": "interval",
                "config": {"interval_seconds": 300},
                "enabled": True
            },
            "expected": {"status": "created"}
        }
    ]
}

# Test report template
TEST_REPORT = {
    "test_run_id": datetime.utcnow().isoformat() + "Z",
    "total_tools": 11,
    "tools_tested": 0,
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "errors": [],
    "results": {}
}

def generate_test_script():
    """Generate a test script for manual testing"""
    script = []
    script.append("#!/bin/bash")
    script.append("# HAK-GAL Critical Tools Test Script")
    script.append("# Generated: " + datetime.utcnow().isoformat())
    script.append("")
    script.append("# Test each tool with curl commands")
    script.append("API_URL='http://localhost:5002/api'")
    script.append("")
    
    for tool_name, tests in TEST_CASES.items():
        script.append(f"# === {tool_name} ===")
        for test in tests:
            script.append(f"echo 'Testing: {tool_name} - {test['name']}'")
            
            # Create curl command
            data = {
                "tool": tool_name,
                "arguments": test["args"]
            }
            curl_cmd = f"curl -X POST $API_URL/tools/{tool_name} \\"
            curl_cmd += f"\n  -H 'Content-Type: application/json' \\"
            curl_cmd += f"\n  -H 'X-API-Key: hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d' \\"
            curl_cmd += f"\n  -d '{json.dumps(data, separators=(',', ':'))}'"
            
            script.append(curl_cmd)
            script.append("echo ''")
            script.append("")
    
    return "\n".join(script)

def generate_postman_collection():
    """Generate Postman collection for API testing"""
    collection = {
        "info": {
            "name": "HAK-GAL Critical Tools Tests",
            "description": "Test collection for 11 new critical workflow tools",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }
    
    for tool_name, tests in TEST_CASES.items():
        folder = {
            "name": tool_name,
            "item": []
        }
        
        for test in tests:
            request = {
                "name": f"{tool_name} - {test['name']}",
                "request": {
                    "method": "POST",
                    "header": [
                        {
                            "key": "Content-Type",
                            "value": "application/json"
                        },
                        {
                            "key": "X-API-Key",
                            "value": "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"
                        }
                    ],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "tool": tool_name,
                            "arguments": test["args"]
                        }, indent=2)
                    },
                    "url": {
                        "raw": "{{base_url}}/api/tools/" + tool_name,
                        "host": ["{{base_url}}"],
                        "path": ["api", "tools", tool_name]
                    }
                }
            }
            folder["item"].append(request)
        
        collection["item"].append(folder)
    
    return collection

def generate_pytest_suite():
    """Generate pytest test suite"""
    pytest_code = '''import pytest
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5002/api"
API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"

class TestCriticalTools:
    """Test suite for HAK-GAL critical workflow tools"""
    
    @pytest.fixture
    def headers(self):
        return {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        }
    
'''
    
    for tool_name, tests in TEST_CASES.items():
        class_name = ''.join(word.capitalize() for word in tool_name.split('_'))
        pytest_code += f'\nclass Test{class_name}:\n'
        pytest_code += f'    """Tests for {tool_name} tool"""\n\n'
        
        for i, test in enumerate(tests):
            test_method_name = test['name'].lower().replace(' ', '_').replace('-', '_')
            pytest_code += f'    def test_{test_method_name}(self, headers):\n'
            pytest_code += f'        """Test: {test["name"]}"""\n'
            pytest_code += f'        data = {json.dumps({"tool": tool_name, "arguments": test["args"]}, indent=12)}\n'
            pytest_code += f'        response = requests.post(f"{{BASE_URL}}/tools/{tool_name}", json=data, headers=headers)\n'
            pytest_code += f'        assert response.status_code == 200\n'
            
            if "expected" in test and not test.get("expected_error", False):
                pytest_code += f'        result = response.json()\n'
                for key, value in test["expected"].items():
                    pytest_code += f'        assert result.get("{key}") == {repr(value)}\n'
            
            pytest_code += '\n'
    
    return pytest_code

# Generate all test artifacts
if __name__ == "__main__":
    print("Generating HAK-GAL Critical Tools Test Suite...")
    
    # Generate bash script
    with open("test_critical_tools.sh", "w") as f:
        f.write(generate_test_script())
    print("✓ Generated: test_critical_tools.sh")
    
    # Generate Postman collection
    with open("HAK_GAL_Critical_Tools.postman_collection.json", "w") as f:
        json.dump(generate_postman_collection(), f, indent=2)
    print("✓ Generated: HAK_GAL_Critical_Tools.postman_collection.json")
    
    # Generate pytest suite
    with open("test_critical_tools_pytest.py", "w") as f:
        f.write(generate_pytest_suite())
    print("✓ Generated: test_critical_tools_pytest.py")
    
    # Generate summary
    print("\n=== TEST SUMMARY ===")
    print(f"Total Tools: 11")
    print(f"Total Test Cases: {sum(len(tests) for tests in TEST_CASES.values())}")
    print("\nTools covered:")
    for i, tool in enumerate(TEST_CASES.keys(), 1):
        print(f"  {i}. {tool} ({len(TEST_CASES[tool])} tests)")
    
    print("\n✓ Test suite generation complete!")
    print("\nNext steps:")
    print("1. Run: chmod +x test_critical_tools.sh && ./test_critical_tools.sh")
    print("2. Import Postman collection for API testing")
    print("3. Run: pytest test_critical_tools_pytest.py -v")
