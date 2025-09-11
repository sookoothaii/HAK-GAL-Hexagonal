#!/usr/bin/env python3
"""
Erweiterte Tests für HAK_GAL Extended Tools
"""

import os
import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extended_tools import ExtendedTools

class MockServer:
    def __init__(self):
        self.write_enabled = True
        self.write_token = "test_token"
    
    def _is_write_allowed(self, token):
        return True

def test_git_advanced():
    """Erweiterte Git-Tests"""
    print("\n=== ERWEITERTE GIT TESTS ===")
    tools = ExtendedTools(MockServer())
    
    # Test in einem temporären Git-Repo
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialisiere Git-Repo
        os.system(f'cd "{tmpdir}" && git init')
        
        # Erstelle Test-Datei
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # Status
        result = tools.git_status(tmpdir)
        print(f"Neues Repo Status: {result}")
        
        # Add und Commit
        os.system(f'cd "{tmpdir}" && git add .')
        result = tools.git_commit(tmpdir, "Initial commit", add_all=True)
        print(f"Commit Result: {result}")

def test_package_advanced():
    """Erweiterte Package-Tests"""
    print("\n=== ERWEITERTE PACKAGE TESTS ===")
    tools = ExtendedTools(MockServer())
    
    # Teste NPM falls verfügbar
    import shutil
    if shutil.which("npm"):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialisiere npm projekt
            os.system(f'cd "{tmpdir}" && npm init -y')
            
            # Liste Packages
            result = tools.package_list("npm", tmpdir)
            print(f"NPM Packages in neuem Projekt: {result}")
    else:
        print("NPM nicht verfügbar")

def test_database_advanced():
    """Erweiterte Datenbank-Tests"""
    print("\n=== ERWEITERTE DATABASE TESTS ===")
    tools = ExtendedTools(MockServer())
    
    # Erstelle temporäre SQLite DB
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        
        # Connect und erstelle Tabelle
        result = tools.db_connect("sqlite", db_path)
        print(f"Neue DB Connect: {result}")
        
        # Create Table
        create_query = """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE
        )
        """
        result = tools.db_query("sqlite", db_path, create_query)
        print(f"Create Table: {result}")
        
        # Insert Data
        insert_query = "INSERT INTO users (name, email) VALUES (?, ?)"
        result = tools.db_query("sqlite", db_path, insert_query, ["Test User", "test@example.com"])
        print(f"Insert: {result}")
        
        # Select
        result = tools.db_query("sqlite", db_path, "SELECT * FROM users")
        print(f"Select: {result}")
        
        # Schema
        result = tools.db_schema("sqlite", db_path)
        print(f"Schema: {result}")

def test_api_mock():
    """Test API mit Mock-Server"""
    print("\n=== API MOCK TESTS ===")
    tools = ExtendedTools(MockServer())
    
    # Test mit httpbin.org (öffentlicher Test-Service)
    result = tools.api_request("GET", "https://httpbin.org/get")
    if result.get('success'):
        print(f"GET Request erfolgreich: Status {result['status_code']}")
        if result.get('json'):
            print(f"Headers empfangen: {result['json'].get('headers', {}).get('User-Agent')}")
    else:
        print(f"API Test fehlgeschlagen: {result.get('error')}")
    
    # POST Test
    test_data = {"key": "value", "test": True}
    result = tools.api_request("POST", "https://httpbin.org/post", data=test_data)
    if result.get('success'):
        print(f"POST Request erfolgreich: {result['status_code']}")
        if result.get('json') and result['json'].get('json'):
            print(f"Daten gesendet: {result['json']['json']}")

def test_env_creation():
    """Test Umgebungs-Erstellung"""
    print("\n=== ENVIRONMENT CREATION TESTS ===")
    tools = ExtendedTools(MockServer())
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Python venv
        result = tools.env_create("python", "test_env", tmpdir)
        print(f"Python venv erstellt: {result.get('success', False)}")
        if result.get('activate'):
            print(f"Aktivierung: {result['activate']}")
        
        # Liste envs
        os.chdir(tmpdir)
        result = tools.env_list("python")
        print(f"Gefundene Python envs: {len(result.get('environments', []))}")

def test_build_simulation():
    """Simuliere Build-Prozesse"""
    print("\n=== BUILD SIMULATION TESTS ===")
    tools = ExtendedTools(MockServer())
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Erstelle Makefile
        makefile = os.path.join(tmpdir, "Makefile")
        with open(makefile, 'w') as f:
            f.write("""
all:
\t@echo "Building project..."

test:
\t@echo "Running tests..."

clean:
\t@echo "Cleaning..."
""")
        
        # Teste make wenn verfügbar
        import shutil
        if shutil.which("make"):
            result = tools.run_build("make", tmpdir)
            print(f"Make build: {result.get('stdout', 'Failed')}")
        
        # Erstelle package.json für npm
        package_json = os.path.join(tmpdir, "package.json")
        with open(package_json, 'w') as f:
            f.write(json.dumps({
                "name": "test-project",
                "scripts": {
                    "build": "echo 'Building with npm...'",
                    "test": "echo 'Testing with npm...'"
                }
            }))
        
        if shutil.which("npm"):
            result = tools.run_build("npm", tmpdir, "build")
            print(f"NPM build: {result.get('stdout', 'Failed')}")

def test_api_suite_advanced():
    """Erweiterte API Test Suite"""
    print("\n=== API TEST SUITE ADVANCED ===")
    tools = ExtendedTools(MockServer())
    
    # Erstelle erweiterte Test-Suite
    suite = {
        "base_url": "https://httpbin.org",
        "headers": {
            "X-Test-Header": "test-value"
        },
        "tests": [
            {
                "name": "GET Test",
                "path": "/get",
                "method": "GET",
                "expected_status": 200,
                "expected_contains": ["args", "headers"]
            },
            {
                "name": "POST Test",
                "path": "/post",
                "method": "POST",
                "body": {"test": "data"},
                "expected_status": 200,
                "expected_contains": ["json"]
            },
            {
                "name": "Status Code Test",
                "path": "/status/404",
                "method": "GET",
                "expected_status": 404
            },
            {
                "name": "Headers Test",
                "path": "/headers",
                "method": "GET",
                "headers": {"Custom-Header": "custom-value"},
                "expected_status": 200,
                "expected_contains": ["Custom-Header"]
            }
        ]
    }
    
    # Speichere Suite
    suite_file = "advanced_test_suite.json"
    with open(suite_file, 'w') as f:
        json.dump(suite, f, indent=2)
    
    # Führe Tests aus
    result = tools.api_test_suite(suite_file)
    print(f"\nTest Suite Ergebnisse: {result['passed']}/{result['total']} bestanden")
    
    for test in result['tests']:
        status = "✓" if test['passed'] else "✗"
        print(f"{status} {test['name']}")
        if test.get('failures'):
            for failure in test['failures']:
                print(f"  - {failure}")
        if test.get('response_time'):
            print(f"  Zeit: {test['response_time']}s")
    
    # Aufräumen
    os.unlink(suite_file)

def test_error_handling():
    """Teste Fehlerbehandlung"""
    print("\n=== ERROR HANDLING TESTS ===")
    tools = ExtendedTools(MockServer())
    
    # Nicht existierende Datei
    result = tools.db_connect("sqlite", "/nicht/existierende/datei.db")
    print(f"DB Connect nicht existierend: {result}")
    
    # Ungültige Query
    result = tools.db_query("sqlite", ":memory:", "INVALID SQL")
    print(f"Invalid SQL: {result}")
    
    # Timeout Test (lange URL)
    result = tools.api_request("GET", "https://httpbin.org/delay/10", timeout=1)
    print(f"Timeout Test: {'Timeout' in str(result.get('error', ''))}")

if __name__ == "__main__":
    print("HAK-GAL Extended Tools - Erweiterte Tests")
    print("==========================================")
    
    # Führe erweiterte Tests durch
    tests = [
        ("Git Advanced", test_git_advanced),
        ("Package Advanced", test_package_advanced),
        ("Database Advanced", test_database_advanced),
        ("API Mock", test_api_mock),
        ("Environment Creation", test_env_creation),
        ("Build Simulation", test_build_simulation),
        ("API Suite Advanced", test_api_suite_advanced),
        ("Error Handling", test_error_handling)
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"\n{test_name} Error: {e}")
    
    print("\n\nAlle Tests abgeschlossen!")
