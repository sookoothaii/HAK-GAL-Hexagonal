#!/usr/bin/env python3
"""
HAK_GAL Filesystem MCP Server - Extended Tools Module
New tools for Version Control, Package Management, Build/Test, Database, API Testing, Environment Management
"""

import subprocess
import sqlite3
import urllib.request
import urllib.parse
import urllib.error
import venv
import sys
import os
import json
import platform
import re
import time
import shutil
from pathlib import Path

class ExtendedTools:
    """Extended tools for HAK_GAL Filesystem MCP Server"""
    
    def __init__(self, parent_server):
        self.server = parent_server
        self.logger = parent_server.logger if hasattr(parent_server, 'logger') else None
    
    # ========== VERSION CONTROL (GIT) ==========
    
    def git_status(self, path="."):
        """Get git repository status"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain", "-b"],
                cwd=path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {"error": f"Not a git repository or git error: {result.stderr}"}
            
            lines = result.stdout.strip().split('\n')
            branch_info = lines[0] if lines else ""
            changes = [l for l in lines[1:] if l.strip()]
            
            # Get more info
            ahead_behind = subprocess.run(
                ["git", "rev-list", "--left-right", "--count", "HEAD...@{upstream}"],
                cwd=path,
                capture_output=True,
                text=True
            )
            
            ahead = behind = 0
            if ahead_behind.returncode == 0:
                parts = ahead_behind.stdout.strip().split()
                if len(parts) == 2:
                    ahead, behind = int(parts[0]), int(parts[1])
            
            return {
                "branch": branch_info.replace("## ", ""),
                "changes": len(changes),
                "files": changes,
                "ahead": ahead,
                "behind": behind,
                "clean": len(changes) == 0
            }
        except FileNotFoundError:
            return {"error": "Git not installed"}
        except Exception as e:
            return {"error": str(e)}
    
    def git_log(self, path=".", limit=10):
        """Get git commit log"""
        try:
            result = subprocess.run(
                ["git", "log", f"--max-count={limit}", "--pretty=format:%H|%an|%ae|%at|%s"],
                cwd=path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {"error": result.stderr}
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 4)
                    if len(parts) == 5:
                        commits.append({
                            "hash": parts[0][:8],
                            "author": parts[1],
                            "email": parts[2],
                            "timestamp": parts[3],
                            "message": parts[4]
                        })
            
            return {"commits": commits}
        except Exception as e:
            return {"error": str(e)}
    
    def git_branch(self, path=".", action="list", name=None):
        """Git branch operations"""
        try:
            if action == "list":
                result = subprocess.run(
                    ["git", "branch", "-a"],
                    cwd=path,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    branches = []
                    current = None
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            if line.startswith('* '):
                                current = line[2:].strip()
                                branches.append(current)
                            else:
                                branches.append(line.strip())
                    
                    return {"branches": branches, "current": current}
            
            elif action == "create" and name:
                result = subprocess.run(
                    ["git", "checkout", "-b", name],
                    cwd=path,
                    capture_output=True,
                    text=True
                )
                return {"success": result.returncode == 0, "message": result.stdout or result.stderr}
            
            elif action == "switch" and name:
                result = subprocess.run(
                    ["git", "checkout", name],
                    cwd=path,
                    capture_output=True,
                    text=True
                )
                return {"success": result.returncode == 0, "message": result.stdout or result.stderr}
            
            elif action == "delete" and name:
                result = subprocess.run(
                    ["git", "branch", "-d", name],
                    cwd=path,
                    capture_output=True,
                    text=True
                )
                return {"success": result.returncode == 0, "message": result.stdout or result.stderr}
            
            else:
                return {"error": "Invalid action. Use: list, create, switch, delete"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def git_commit(self, path=".", message="", add_all=False):
        """Git commit changes"""
        try:
            if add_all:
                # Stage all changes
                add_result = subprocess.run(
                    ["git", "add", "-A"],
                    cwd=path,
                    capture_output=True,
                    text=True
                )
                if add_result.returncode != 0:
                    return {"error": f"Failed to stage changes: {add_result.stderr}"}
            
            if not message:
                return {"error": "Commit message is required"}
            
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Get commit hash
                hash_result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=path,
                    capture_output=True,
                    text=True
                )
                commit_hash = hash_result.stdout.strip()[:8] if hash_result.returncode == 0 else "unknown"
                
                return {
                    "success": True,
                    "hash": commit_hash,
                    "message": result.stdout
                }
            else:
                return {"error": result.stderr or "Nothing to commit"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def git_pull(self, path=".", remote="origin", branch=None):
        """Git pull from remote"""
        try:
            cmd = ["git", "pull", remote]
            if branch:
                cmd.append(branch)
            
            result = subprocess.run(
                cmd,
                cwd=path,
                capture_output=True,
                text=True
            )
            
            return {
                "success": result.returncode == 0,
                "message": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"error": str(e)}
    
    def git_push(self, path=".", remote="origin", branch=None):
        """Git push to remote"""
        try:
            cmd = ["git", "push", remote]
            if branch:
                cmd.append(branch)
            
            result = subprocess.run(
                cmd,
                cwd=path,
                capture_output=True,
                text=True
            )
            
            return {
                "success": result.returncode == 0,
                "message": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ========== PACKAGE MANAGEMENT ==========
    
    def package_install(self, package_manager, packages, path="."):
        """Install packages using various package managers"""
        try:
            if package_manager == "pip":
                cmd = [sys.executable, "-m", "pip", "install"] + packages
            elif package_manager == "npm":
                cmd = ["npm", "install"] + packages
            elif package_manager == "yarn":
                cmd = ["yarn", "add"] + packages
            elif package_manager == "nuget":
                cmd = ["dotnet", "add", "package"] + packages
            else:
                return {"error": f"Unsupported package manager: {package_manager}"}
            
            result = subprocess.run(
                cmd,
                cwd=path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "installed": packages if result.returncode == 0 else []
            }
        except subprocess.TimeoutExpired:
            return {"error": "Installation timeout after 5 minutes"}
        except FileNotFoundError:
            return {"error": f"{package_manager} not found"}
        except Exception as e:
            return {"error": str(e)}
    
    def package_list(self, package_manager, path="."):
        """List installed packages"""
        try:
            if package_manager == "pip":
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "list", "--format=json"],
                    cwd=path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    packages = json.loads(result.stdout)
                    return {"packages": packages}
            
            elif package_manager == "npm":
                result = subprocess.run(
                    ["npm", "list", "--json", "--depth=0"],
                    cwd=path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    deps = data.get("dependencies", {})
                    packages = [{"name": k, "version": v.get("version", "")} for k, v in deps.items()]
                    return {"packages": packages}
            
            elif package_manager == "yarn":
                result = subprocess.run(
                    ["yarn", "list", "--json", "--depth=0"],
                    cwd=path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    # Yarn outputs multiple JSON objects, one per line
                    packages = []
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            try:
                                data = json.loads(line)
                                if data.get("type") == "tree":
                                    for item in data.get("data", {}).get("trees", []):
                                        name = item.get("name", "")
                                        if "@" in name:
                                            pkg_name, version = name.rsplit("@", 1)
                                            packages.append({"name": pkg_name, "version": version})
                            except:
                                pass
                    return {"packages": packages}
            
            elif package_manager == "nuget":
                result = subprocess.run(
                    ["dotnet", "list", "package"],
                    cwd=path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    packages = []
                    for line in result.stdout.split('\n'):
                        if ">" in line:
                            parts = line.split()
                            if len(parts) >= 3:
                                packages.append({"name": parts[1], "version": parts[2]})
                    return {"packages": packages}
            
            else:
                return {"error": f"Unsupported package manager: {package_manager}"}
                
            return {"error": result.stderr}
            
        except FileNotFoundError:
            return {"error": f"{package_manager} not found"}
        except Exception as e:
            return {"error": str(e)}
    
    def package_update(self, package_manager, packages=None, path="."):
        """Update packages"""
        try:
            if package_manager == "pip":
                if packages:
                    cmd = [sys.executable, "-m", "pip", "install", "--upgrade"] + packages
                else:
                    # Update all packages
                    list_result = subprocess.run(
                        [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
                        capture_output=True,
                        text=True
                    )
                    if list_result.returncode == 0:
                        outdated = json.loads(list_result.stdout)
                        if outdated:
                            packages = [pkg["name"] for pkg in outdated]
                            cmd = [sys.executable, "-m", "pip", "install", "--upgrade"] + packages
                        else:
                            return {"message": "All packages are up to date"}
                    else:
                        return {"error": "Failed to check outdated packages"}
            
            elif package_manager == "npm":
                cmd = ["npm", "update"] + (packages or [])
            
            elif package_manager == "yarn":
                cmd = ["yarn", "upgrade"] + (packages or [])
            
            elif package_manager == "nuget":
                if packages:
                    results = []
                    for pkg in packages:
                        result = subprocess.run(
                            ["dotnet", "add", "package", pkg],
                            cwd=path,
                            capture_output=True,
                            text=True
                        )
                        results.append({"package": pkg, "success": result.returncode == 0})
                    return {"results": results}
                else:
                    return {"error": "NuGet requires specific package names to update"}
            
            else:
                return {"error": f"Unsupported package manager: {package_manager}"}
            
            result = subprocess.run(
                cmd,
                cwd=path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Update timeout after 5 minutes"}
        except Exception as e:
            return {"error": str(e)}
    
    # ========== BUILD & TEST TOOLS ==========
    
    def run_build(self, build_tool, path=".", target=None):
        """Run build tools"""
        try:
            if build_tool == "make":
                cmd = ["make"]
                if target:
                    cmd.append(target)
            
            elif build_tool == "maven":
                cmd = ["mvn", "clean", "install"]
                if target:
                    cmd = ["mvn", target]
            
            elif build_tool == "gradle":
                cmd = ["gradle", "build"]
                if target:
                    cmd = ["gradle", target]
            
            elif build_tool == "npm":
                cmd = ["npm", "run", "build"]
                if target:
                    cmd = ["npm", "run", target]
            
            elif build_tool == "dotnet":
                cmd = ["dotnet", "build"]
                if target:
                    cmd.append(target)
            
            elif build_tool == "cargo":
                cmd = ["cargo", "build"]
                if target == "release":
                    cmd.append("--release")
            
            else:
                return {"error": f"Unsupported build tool: {build_tool}"}
            
            result = subprocess.run(
                cmd,
                cwd=path,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[-10000:],  # Last 10k chars
                "stderr": result.stderr[-10000:],
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Build timeout after 10 minutes"}
        except FileNotFoundError:
            return {"error": f"{build_tool} not found"}
        except Exception as e:
            return {"error": str(e)}
    
    def run_tests(self, test_framework, path=".", pattern=None):
        """Run tests using various frameworks"""
        try:
            if test_framework == "pytest":
                cmd = [sys.executable, "-m", "pytest", "-v"]
                if pattern:
                    cmd.extend(["-k", pattern])
            
            elif test_framework == "unittest":
                cmd = [sys.executable, "-m", "unittest", "discover"]
                if pattern:
                    cmd.extend(["-p", f"*{pattern}*.py"])
            
            elif test_framework == "jest":
                cmd = ["jest"]
                if pattern:
                    cmd.append(pattern)
            
            elif test_framework == "mocha":
                cmd = ["mocha"]
                if pattern:
                    cmd.extend(["--grep", pattern])
            
            elif test_framework == "dotnet":
                cmd = ["dotnet", "test"]
                if pattern:
                    cmd.extend(["--filter", pattern])
            
            elif test_framework == "cargo":
                cmd = ["cargo", "test"]
                if pattern:
                    cmd.append(pattern)
            
            else:
                return {"error": f"Unsupported test framework: {test_framework}"}
            
            result = subprocess.run(
                cmd,
                cwd=path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            
            # Try to extract test summary
            summary = self._extract_test_summary(result.stdout, test_framework)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[-10000:],
                "stderr": result.stderr[-5000:],
                "return_code": result.returncode,
                "summary": summary
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Test timeout after 5 minutes"}
        except FileNotFoundError:
            return {"error": f"{test_framework} not found"}
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_test_summary(self, output, framework):
        """Extract test summary from output"""
        summary = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
        
        if framework == "pytest":
            # Look for pytest summary line
            match = re.search(r'(\d+) passed(?:, (\d+) failed)?(?:, (\d+) skipped)?', output)
            if match:
                summary["passed"] = int(match.group(1))
                summary["failed"] = int(match.group(2) or 0)
                summary["skipped"] = int(match.group(3) or 0)
                summary["total"] = sum(summary.values())
        
        elif framework == "jest":
            # Look for jest summary
            match = re.search(r'Tests:\s+(\d+) passed, (\d+) total', output)
            if match:
                summary["passed"] = int(match.group(1))
                summary["total"] = int(match.group(2))
                summary["failed"] = summary["total"] - summary["passed"]
        
        return summary
    
    # ========== DATABASE OPERATIONS ==========
    
    def db_connect(self, db_type, connection_string):
        """Connect to database and run query"""
        try:
            if db_type == "sqlite":
                # For SQLite, connection string is the file path
                if not os.path.exists(connection_string):
                    return {"error": f"SQLite database not found: {connection_string}"}
                
                conn = sqlite3.connect(connection_string)
                conn.row_factory = sqlite3.Row
                
                # Get database info
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                conn.close()
                
                return {
                    "success": True,
                    "db_type": "sqlite",
                    "tables": tables,
                    "connection": connection_string
                }
            
            else:
                return {"error": f"Unsupported database type: {db_type}. Currently only SQLite is supported."}
                
        except Exception as e:
            return {"error": str(e)}
    
    def db_query(self, db_type, connection_string, query, params=None):
        """Execute database query"""
        try:
            if db_type == "sqlite":
                conn = sqlite3.connect(connection_string)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Determine query type
                query_lower = query.strip().lower()
                is_select = query_lower.startswith("select")
                is_write = any(query_lower.startswith(cmd) for cmd in ["insert", "update", "delete", "create", "drop", "alter"])
                
                # Execute query
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if is_select:
                    # Fetch results
                    rows = cursor.fetchall()
                    columns = [description[0] for description in cursor.description] if cursor.description else []
                    
                    # Convert rows to dicts
                    results = []
                    for row in rows[:1000]:  # Limit to 1000 rows
                        results.append(dict(zip(columns, row)))
                    
                    conn.close()
                    
                    return {
                        "success": True,
                        "rows": len(results),
                        "columns": columns,
                        "data": results,
                        "truncated": len(rows) > 1000
                    }
                
                elif is_write:
                    # Commit changes
                    conn.commit()
                    affected_rows = cursor.rowcount
                    conn.close()
                    
                    return {
                        "success": True,
                        "affected_rows": affected_rows,
                        "operation": query_lower.split()[0].upper()
                    }
                
                else:
                    # Other queries (PRAGMA, etc.)
                    try:
                        results = cursor.fetchall()
                        conn.close()
                        return {
                            "success": True,
                            "results": [dict(row) for row in results] if results else None
                        }
                    except:
                        conn.close()
                        return {"success": True, "message": "Query executed"}
                
            else:
                return {"error": f"Unsupported database type: {db_type}"}
                
        except Exception as e:
            return {"error": f"Database error: {str(e)}"}
    
    def db_schema(self, db_type, connection_string, table=None):
        """Get database schema information"""
        try:
            if db_type == "sqlite":
                conn = sqlite3.connect(connection_string)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if table:
                    # Get specific table schema
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = []
                    for row in cursor.fetchall():
                        columns.append({
                            "name": row["name"],
                            "type": row["type"],
                            "nullable": not row["notnull"],
                            "primary_key": bool(row["pk"]),
                            "default": row["dflt_value"]
                        })
                    
                    # Get indexes
                    cursor.execute(f"PRAGMA index_list({table})")
                    indexes = []
                    for row in cursor.fetchall():
                        indexes.append({
                            "name": row["name"],
                            "unique": bool(row["unique"])
                        })
                    
                    conn.close()
                    
                    return {
                        "table": table,
                        "columns": columns,
                        "indexes": indexes
                    }
                
                else:
                    # Get all tables schema
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                    tables = {}
                    
                    for row in cursor.fetchall():
                        table_name = row[0]
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = []
                        for col in cursor.fetchall():
                            columns.append({
                                "name": col["name"],
                                "type": col["type"]
                            })
                        tables[table_name] = columns
                    
                    conn.close()
                    
                    return {"tables": tables}
                
            else:
                return {"error": f"Unsupported database type: {db_type}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    # ========== API TESTING ==========
    
    def api_request(self, method, url, headers=None, data=None, params=None, timeout=30):
        """Make HTTP API request"""
        try:
            # Prepare request
            method = method.upper()
            headers = headers or {}
            
            # Add default headers
            if "User-Agent" not in headers:
                headers["User-Agent"] = "HAK-GAL-MCP/1.0"
            
            # Handle data
            body_data = None
            if data:
                if isinstance(data, dict):
                    body_data = json.dumps(data).encode('utf-8')
                    if "Content-Type" not in headers:
                        headers["Content-Type"] = "application/json"
                else:
                    body_data = data.encode('utf-8')
            
            # Handle params
            if params:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            
            # Create request
            request = urllib.request.Request(url, data=body_data, headers=headers)
            request.get_method = lambda: method
            
            # Make request
            start_time = time.time()
            
            try:
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    response_data = response.read()
                    response_text = response_data.decode('utf-8', errors='replace')
                    
                    # Try to parse JSON
                    response_json = None
                    if response.headers.get('Content-Type', '').startswith('application/json'):
                        try:
                            response_json = json.loads(response_text)
                        except:
                            pass
                    
                    elapsed = time.time() - start_time
                    
                    return {
                        "success": True,
                        "status_code": response.code,
                        "headers": dict(response.headers),
                        "body": response_text[:10000],  # Limit to 10k chars
                        "json": response_json,
                        "elapsed_seconds": round(elapsed, 3),
                        "size_bytes": len(response_data)
                    }
                    
            except urllib.error.HTTPError as e:
                elapsed = time.time() - start_time
                error_body = e.read().decode('utf-8', errors='replace')
                
                return {
                    "success": False,
                    "status_code": e.code,
                    "headers": dict(e.headers),
                    "body": error_body[:10000],
                    "elapsed_seconds": round(elapsed, 3),
                    "error": f"HTTP {e.code}: {e.reason}"
                }
                
            except urllib.error.URLError as e:
                return {"error": f"URL Error: {str(e.reason)}"}
                
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def api_test_suite(self, suite_file):
        """Run API test suite from JSON file"""
        try:
            with open(suite_file, 'r') as f:
                suite = json.load(f)
            
            results = {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "tests": []
            }
            
            base_url = suite.get("base_url", "")
            global_headers = suite.get("headers", {})
            
            for test in suite.get("tests", []):
                results["total"] += 1
                
                # Prepare test
                url = base_url + test.get("path", "")
                method = test.get("method", "GET")
                headers = {**global_headers, **test.get("headers", {})}
                data = test.get("body")
                params = test.get("params")
                expected_status = test.get("expected_status", 200)
                expected_contains = test.get("expected_contains", [])
                
                # Run test
                response = self.api_request(method, url, headers, data, params)
                
                # Check results
                test_passed = True
                failures = []
                
                if response.get("error"):
                    test_passed = False
                    failures.append(f"Request failed: {response['error']}")
                else:
                    if response["status_code"] != expected_status:
                        test_passed = False
                        failures.append(f"Expected status {expected_status}, got {response['status_code']}")
                    
                    for expected in expected_contains:
                        if expected not in response.get("body", ""):
                            test_passed = False
                            failures.append(f"Response missing expected content: {expected}")
                
                if test_passed:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                
                results["tests"].append({
                    "name": test.get("name", "Unnamed test"),
                    "passed": test_passed,
                    "failures": failures,
                    "response_status": response.get("status_code"),
                    "response_time": response.get("elapsed_seconds")
                })
            
            return results
            
        except Exception as e:
            return {"error": f"Test suite error: {str(e)}"}
    
    # ========== ENVIRONMENT MANAGEMENT ==========
    
    def env_create(self, env_type, name, path="."):
        """Create virtual environment"""
        try:
            env_path = os.path.join(path, name)
            
            if env_type == "python":
                # Create Python venv
                venv.create(env_path, with_pip=True)
                
                # Get activation script path
                if platform.system() == "Windows":
                    activate = os.path.join(env_path, "Scripts", "activate.bat")
                else:
                    activate = os.path.join(env_path, "bin", "activate")
                
                return {
                    "success": True,
                    "type": "python",
                    "path": env_path,
                    "activate": activate
                }
            
            elif env_type == "conda":
                # Create Conda environment
                result = subprocess.run(
                    ["conda", "create", "-n", name, "-y"],
                    capture_output=True,
                    text=True
                )
                
                return {
                    "success": result.returncode == 0,
                    "type": "conda",
                    "name": name,
                    "message": result.stdout
                }
            
            elif env_type == "node":
                # Initialize Node.js project
                project_path = os.path.join(path, name)
                os.makedirs(project_path, exist_ok=True)
                
                result = subprocess.run(
                    ["npm", "init", "-y"],
                    cwd=project_path,
                    capture_output=True,
                    text=True
                )
                
                return {
                    "success": result.returncode == 0,
                    "type": "node",
                    "path": project_path,
                    "message": result.stdout
                }
            
            else:
                return {"error": f"Unsupported environment type: {env_type}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def env_list(self, env_type):
        """List environments"""
        try:
            if env_type == "python":
                # List Python venvs in current directory
                envs = []
                for item in os.listdir("."):
                    if os.path.isdir(item):
                        # Check if it's a venv
                        if os.path.exists(os.path.join(item, "pyvenv.cfg")):
                            envs.append({
                                "name": item,
                                "type": "python-venv",
                                "path": os.path.abspath(item)
                            })
                return {"environments": envs}
            
            elif env_type == "conda":
                result = subprocess.run(
                    ["conda", "env", "list"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    envs = []
                    for line in result.stdout.strip().split('\n')[2:]:  # Skip header
                        if line.strip() and not line.startswith('#'):
                            parts = line.split()
                            if len(parts) >= 2:
                                envs.append({
                                    "name": parts[0],
                                    "path": parts[1] if len(parts) > 1 else ""
                                })
                    return {"environments": envs}
                else:
                    return {"error": "Failed to list conda environments"}
            
            else:
                return {"error": f"Unsupported environment type: {env_type}"}
                
        except FileNotFoundError:
            return {"error": f"{env_type} not found"}
        except Exception as e:
            return {"error": str(e)}
    
    def env_freeze(self, env_type, output_file=None, path="."):
        """Export environment dependencies"""
        try:
            if env_type == "python":
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "freeze"],
                    cwd=path,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    requirements = result.stdout
                    
                    if output_file:
                        with open(os.path.join(path, output_file), 'w') as f:
                            f.write(requirements)
                        return {
                            "success": True,
                            "file": output_file,
                            "packages": len(requirements.strip().split('\n'))
                        }
                    else:
                        return {
                            "success": True,
                            "requirements": requirements
                        }
                else:
                    return {"error": result.stderr}
            
            elif env_type == "conda":
                cmd = ["conda", "env", "export"]
                if output_file:
                    cmd.extend(["-f", output_file])
                
                result = subprocess.run(
                    cmd,
                    cwd=path,
                    capture_output=True,
                    text=True
                )
                
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout if not output_file else f"Exported to {output_file}"
                }
            
            elif env_type == "node":
                # package.json already serves as the freeze file
                package_file = os.path.join(path, "package.json")
                if os.path.exists(package_file):
                    with open(package_file, 'r') as f:
                        package_data = json.load(f)
                    
                    return {
                        "success": True,
                        "dependencies": package_data.get("dependencies", {}),
                        "devDependencies": package_data.get("devDependencies", {})
                    }
                else:
                    return {"error": "No package.json found"}
            
            else:
                return {"error": f"Unsupported environment type: {env_type}"}
                
        except Exception as e:
            return {"error": str(e)}

# Helper function to integrate with main server
def get_extended_tools():
    """Return list of tool definitions for the extended tools"""
    return [
        # Version Control
        {
            "name": "git_status",
            "description": "Get git repository status",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "default": ".", "description": "Repository path"}
                }
            }
        },
        {
            "name": "git_log",
            "description": "Get git commit history",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "default": ".", "description": "Repository path"},
                    "limit": {"type": "integer", "default": 10, "description": "Number of commits"}
                }
            }
        },
        {
            "name": "git_branch",
            "description": "Git branch operations (list, create, switch, delete)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "default": ".", "description": "Repository path"},
                    "action": {"type": "string", "default": "list", "description": "Action: list, create, switch, delete"},
                    "name": {"type": "string", "description": "Branch name (for create/switch/delete)"}
                }
            }
        },
        {
            "name": "git_commit",
            "description": "Commit changes to git",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "default": ".", "description": "Repository path"},
                    "message": {"type": "string", "description": "Commit message"},
                    "add_all": {"type": "boolean", "default": False, "description": "Stage all changes"},
                    "auth_token": {"type": "string"}
                },
                "required": ["message"]
            }
        },
        {
            "name": "git_push",
            "description": "Push commits to remote repository",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "default": ".", "description": "Repository path"},
                    "remote": {"type": "string", "default": "origin", "description": "Remote name"},
                    "branch": {"type": "string", "description": "Branch name"},
                    "auth_token": {"type": "string"}
                }
            }
        },
        {
            "name": "git_pull",
            "description": "Pull changes from remote repository",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "default": ".", "description": "Repository path"},
                    "remote": {"type": "string", "default": "origin", "description": "Remote name"},
                    "branch": {"type": "string", "description": "Branch name"}
                }
            }
        },
        # Package Management
        {
            "name": "package_install",
            "description": "Install packages using pip, npm, yarn, or nuget",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "package_manager": {"type": "string", "description": "Package manager: pip, npm, yarn, nuget"},
                    "packages": {"type": "array", "items": {"type": "string"}, "description": "List of packages"},
                    "path": {"type": "string", "default": ".", "description": "Working directory"},
                    "auth_token": {"type": "string"}
                },
                "required": ["package_manager", "packages"]
            }
        },
        {
            "name": "package_list",
            "description": "List installed packages",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "package_manager": {"type": "string", "description": "Package manager: pip, npm, yarn, nuget"},
                    "path": {"type": "string", "default": ".", "description": "Working directory"}
                },
                "required": ["package_manager"]
            }
        },
        {
            "name": "package_update",
            "description": "Update packages",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "package_manager": {"type": "string", "description": "Package manager: pip, npm, yarn, nuget"},
                    "packages": {"type": "array", "items": {"type": "string"}, "description": "Specific packages (optional)"},
                    "path": {"type": "string", "default": ".", "description": "Working directory"},
                    "auth_token": {"type": "string"}
                },
                "required": ["package_manager"]
            }
        },
        # Build & Test
        {
            "name": "run_build",
            "description": "Run build tools (make, maven, gradle, npm, dotnet, cargo)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "build_tool": {"type": "string", "description": "Build tool: make, maven, gradle, npm, dotnet, cargo"},
                    "path": {"type": "string", "default": ".", "description": "Project directory"},
                    "target": {"type": "string", "description": "Build target (optional)"},
                    "auth_token": {"type": "string"}
                },
                "required": ["build_tool"]
            }
        },
        {
            "name": "run_tests",
            "description": "Run tests using various frameworks",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "test_framework": {"type": "string", "description": "Framework: pytest, unittest, jest, mocha, dotnet, cargo"},
                    "path": {"type": "string", "default": ".", "description": "Project directory"},
                    "pattern": {"type": "string", "description": "Test pattern/filter (optional)"}
                },
                "required": ["test_framework"]
            }
        },
        # Database Operations
        {
            "name": "db_connect",
            "description": "Connect to database and get info",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "db_type": {"type": "string", "description": "Database type: sqlite"},
                    "connection_string": {"type": "string", "description": "Connection string or path"}
                },
                "required": ["db_type", "connection_string"]
            }
        },
        {
            "name": "db_query",
            "description": "Execute database query",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "db_type": {"type": "string", "description": "Database type: sqlite"},
                    "connection_string": {"type": "string", "description": "Connection string or path"},
                    "query": {"type": "string", "description": "SQL query"},
                    "params": {"type": "array", "description": "Query parameters (optional)"},
                    "auth_token": {"type": "string", "description": "Required for write operations"}
                },
                "required": ["db_type", "connection_string", "query"]
            }
        },
        {
            "name": "db_schema",
            "description": "Get database schema information",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "db_type": {"type": "string", "description": "Database type: sqlite"},
                    "connection_string": {"type": "string", "description": "Connection string or path"},
                    "table": {"type": "string", "description": "Specific table (optional)"}
                },
                "required": ["db_type", "connection_string"]
            }
        },
        # API Testing
        {
            "name": "api_request",
            "description": "Make HTTP API request",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "method": {"type": "string", "description": "HTTP method: GET, POST, PUT, DELETE, etc."},
                    "url": {"type": "string", "description": "Request URL"},
                    "headers": {"type": "object", "description": "Request headers"},
                    "data": {"description": "Request body (string or object)"},
                    "params": {"type": "object", "description": "Query parameters"},
                    "timeout": {"type": "integer", "default": 30, "description": "Timeout in seconds"}
                },
                "required": ["method", "url"]
            }
        },
        {
            "name": "api_test_suite",
            "description": "Run API test suite from JSON file",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "suite_file": {"type": "string", "description": "Path to test suite JSON file"}
                },
                "required": ["suite_file"]
            }
        },
        # Environment Management
        {
            "name": "env_create",
            "description": "Create virtual environment",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "env_type": {"type": "string", "description": "Environment type: python, conda, node"},
                    "name": {"type": "string", "description": "Environment name"},
                    "path": {"type": "string", "default": ".", "description": "Parent directory"},
                    "auth_token": {"type": "string"}
                },
                "required": ["env_type", "name"]
            }
        },
        {
            "name": "env_list",
            "description": "List environments",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "env_type": {"type": "string", "description": "Environment type: python, conda"}
                },
                "required": ["env_type"]
            }
        },
        {
            "name": "env_freeze",
            "description": "Export environment dependencies",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "env_type": {"type": "string", "description": "Environment type: python, conda, node"},
                    "output_file": {"type": "string", "description": "Output file (optional)"},
                    "path": {"type": "string", "default": ".", "description": "Working directory"},
                    "auth_token": {"type": "string"}
                },
                "required": ["env_type"]
            }
        }
    ]