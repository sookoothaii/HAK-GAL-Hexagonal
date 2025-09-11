#!/usr/bin/env python3
"""
Test script for HAK_GAL Extended Tools
Tests each new tool category before integration
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extended_tools import ExtendedTools

class MockServer:
    """Mock server for testing"""
    def __init__(self):
        self.write_enabled = True
        self.write_token = "test_token"
    
    def _is_write_allowed(self, token):
        return True

def test_git_tools():
    """Test Git operations"""
    print("\n=== TESTING GIT TOOLS ===")
    tools = ExtendedTools(MockServer())
    
    # Test git status
    result = tools.git_status()
    print(f"Git Status: {result}")
    
    # Test git log
    result = tools.git_log(limit=5)
    print(f"Git Log: {json.dumps(result, indent=2)}")
    
    # Test git branch
    result = tools.git_branch()
    print(f"Git Branches: {result}")

def test_package_tools():
    """Test Package Management"""
    print("\n=== TESTING PACKAGE MANAGEMENT ===")
    tools = ExtendedTools(MockServer())
    
    # Test pip list
    result = tools.package_list("pip")
    print(f"Pip packages: Found {len(result.get('packages', []))} packages")
    
    # Show first 5 packages
    if result.get('packages'):
        for pkg in result['packages'][:5]:
            print(f"  - {pkg['name']} {pkg['version']}")

def test_database_tools():
    """Test Database operations"""
    print("\n=== TESTING DATABASE TOOLS ===")
    tools = ExtendedTools(MockServer())
    
    # Test with HAK-GAL database
    db_path = "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hexagonal_kb.db"
    
    if os.path.exists(db_path):
        # Connect
        result = tools.db_connect("sqlite", db_path)
        print(f"DB Connect: Found {len(result.get('tables', []))} tables")
        
        # Query
        result = tools.db_query("sqlite", db_path, "SELECT COUNT(*) as count FROM facts")
        print(f"Fact Count: {result}")
        
        # Schema
        result = tools.db_schema("sqlite", db_path, "facts")
        print(f"Facts table schema: {json.dumps(result, indent=2)}")
    else:
        print("HAK-GAL database not found")

def test_api_tools():
    """Test API request tools"""
    print("\n=== TESTING API TOOLS ===")
    tools = ExtendedTools(MockServer())
    
    # Test local API
    result = tools.api_request("GET", "http://127.0.0.1:5002/health")
    print(f"API Health Check: Status={result.get('status_code')}, Success={result.get('success')}")
    
    # Test with headers
    headers = {"X-API-Key": "test_key"}
    result = tools.api_request("GET", "http://127.0.0.1:5002/api/facts/count", headers=headers)
    print(f"API Facts Count: {result.get('json') if result.get('success') else result.get('error')}")

def test_env_tools():
    """Test Environment Management"""
    print("\n=== TESTING ENVIRONMENT TOOLS ===")
    tools = ExtendedTools(MockServer())
    
    # List Python environments
    result = tools.env_list("python")
    print(f"Python environments: {result}")
    
    # Test freeze
    result = tools.env_freeze("python")
    if result.get('success'):
        packages = result.get('requirements', '').strip().split('\n')
        print(f"Current environment has {len(packages)} packages")

def test_build_tools():
    """Test Build and Test tools"""
    print("\n=== TESTING BUILD & TEST TOOLS ===")
    tools = ExtendedTools(MockServer())
    
    # Check available build tools
    build_tools = ["make", "npm", "cargo", "dotnet"]
    for tool in build_tools:
        # Just check if tool exists
        import shutil
        if shutil.which(tool):
            print(f"✓ {tool} is available")
        else:
            print(f"✗ {tool} not found")
    
    # Test pytest discovery (non-destructive)
    result = tools.run_tests("pytest", pattern="test_nothing_12345")
    print(f"Pytest result: {result.get('error') or 'Executed'}")

def create_test_suite_file():
    """Create example API test suite"""
    suite = {
        "base_url": "http://127.0.0.1:5002",
        "headers": {
            "X-API-Key": "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"
        },
        "tests": [
            {
                "name": "Health Check",
                "path": "/health",
                "method": "GET",
                "expected_status": 200,
                "expected_contains": ["status"]
            },
            {
                "name": "Get Facts Count",
                "path": "/api/facts/count",
                "method": "GET",
                "expected_status": 200,
                "expected_contains": ["count"]
            }
        ]
    }
    
    with open("test_api_suite.json", "w") as f:
        json.dump(suite, f, indent=2)
    
    return "test_api_suite.json"

if __name__ == "__main__":
    print("HAK-GAL Extended Tools Test Suite")
    print("=================================")
    
    # Run tests
    try:
        test_git_tools()
    except Exception as e:
        print(f"Git tools error: {e}")
    
    try:
        test_package_tools()
    except Exception as e:
        print(f"Package tools error: {e}")
    
    try:
        test_database_tools()
    except Exception as e:
        print(f"Database tools error: {e}")
    
    try:
        test_api_tools()
    except Exception as e:
        print(f"API tools error: {e}")
    
    try:
        test_env_tools()
    except Exception as e:
        print(f"Environment tools error: {e}")
    
    try:
        test_build_tools()
    except Exception as e:
        print(f"Build tools error: {e}")
    
    # Create and test API suite
    try:
        suite_file = create_test_suite_file()
        tools = ExtendedTools(MockServer())
        result = tools.api_test_suite(suite_file)
        print(f"\nAPI Test Suite: {result.get('passed')}/{result.get('total')} passed")
        os.unlink(suite_file)  # Clean up
    except Exception as e:
        print(f"API suite test error: {e}")
    
    print("\nTest complete!")
