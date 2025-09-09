#!/usr/bin/env python3
"""
Integration instructions for HAK_GAL Extended Tools

This file shows how to integrate the extended_tools.py module into the existing
hak_gal_filesystem.py server.
"""

# ========== INTEGRATION STEPS ==========

# 1. Add import at the top of hak_gal_filesystem.py (after other imports):
"""
from extended_tools import ExtendedTools, get_extended_tools
"""

# 2. In __init__ method of FileSystemMCPServer class, add:
"""
# Initialize extended tools
self.extended_tools = ExtendedTools(self)
"""

# 3. In handle_list_tools method, after the existing tools list, add:
"""
# Add extended tools
tools.extend(get_extended_tools())
"""

# 4. In handle_tool_call method, add these cases before the final else:

"""
            # ========== EXTENDED TOOLS ==========
            
            # Git operations
            elif name == "git_status":
                path = arguments.get("path", ".")
                ext_result = self.extended_tools.git_status(path)
                if "error" in ext_result:
                    result = {"content": [{"type": "text", "text": f"Error: {ext_result['error']}"}]}
                else:
                    text = f"Branch: {ext_result['branch']}\n"
                    text += f"Status: {'Clean' if ext_result['clean'] else f'{ext_result['changes']} changes'}\n"
                    if ext_result['ahead'] or ext_result['behind']:
                        text += f"Ahead: {ext_result['ahead']}, Behind: {ext_result['behind']}\n"
                    if ext_result['files']:
                        text += "\nChanged files:\n" + "\n".join(ext_result['files'][:20])
                    result = {"content": [{"type": "text", "text": text}]}
            
            elif name == "git_log":
                path = arguments.get("path", ".")
                limit = arguments.get("limit", 10)
                ext_result = self.extended_tools.git_log(path, limit)
                if "error" in ext_result:
                    result = {"content": [{"type": "text", "text": f"Error: {ext_result['error']}"}]}
                else:
                    text = f"Recent commits ({len(ext_result['commits'])}):\n\n"
                    for commit in ext_result['commits']:
                        text += f"{commit['hash']} - {commit['author']} - {commit['message']}\n"
                    result = {"content": [{"type": "text", "text": text}]}
            
            elif name == "git_branch":
                path = arguments.get("path", ".")
                action = arguments.get("action", "list")
                name_arg = arguments.get("name")
                ext_result = self.extended_tools.git_branch(path, action, name_arg)
                if "error" in ext_result:
                    result = {"content": [{"type": "text", "text": f"Error: {ext_result['error']}"}]}
                elif action == "list":
                    text = f"Current branch: {ext_result['current']}\n\nAll branches:\n"
                    for branch in ext_result['branches']:
                        text += f"  {'*' if branch == ext_result['current'] else ' '} {branch}\n"
                    result = {"content": [{"type": "text", "text": text}]}
                else:
                    result = {"content": [{"type": "text", "text": ext_result['message']]}]}
            
            elif name == "git_commit":
                if not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    path = arguments.get("path", ".")
                    message = arguments.get("message", "")
                    add_all = arguments.get("add_all", False)
                    ext_result = self.extended_tools.git_commit(path, message, add_all)
                    if "error" in ext_result:
                        result = {"content": [{"type": "text", "text": f"Error: {ext_result['error']}"}]}
                    else:
                        text = f"Commit successful: {ext_result['hash']}\n{ext_result['message']}"
                        result = {"content": [{"type": "text", "text": text}]}
            
            elif name == "git_push":
                if not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    path = arguments.get("path", ".")
                    remote = arguments.get("remote", "origin")
                    branch = arguments.get("branch")
                    ext_result = self.extended_tools.git_push(path, remote, branch)
                    text = ext_result['message'] if ext_result['success'] else f"Error: {ext_result['error']}"
                    result = {"content": [{"type": "text", "text": text}]}
            
            elif name == "git_pull":
                path = arguments.get("path", ".")
                remote = arguments.get("remote", "origin")
                branch = arguments.get("branch")
                ext_result = self.extended_tools.git_pull(path, remote, branch)
                text = ext_result['message'] if ext_result['success'] else f"Error: {ext_result['error']}"
                result = {"content": [{"type": "text", "text": text}]}
            
            # Package management
            elif name == "package_install":
                if not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    pm = arguments.get("package_manager", "")
                    packages = arguments.get("packages", [])
                    path = arguments.get("path", ".")
                    ext_result = self.extended_tools.package_install(pm, packages, path)
                    if "error" in ext_result:
                        result = {"content": [{"type": "text", "text": f"Error: {ext_result['error']}"}]}
                    else:
                        text = f"{'Success' if ext_result['success'] else 'Failed'}: Installing {len(packages)} packages\n"
                        if ext_result.get('stdout'):
                            text += f"\nOutput:\n{ext_result['stdout'][-2000:]}"
                        result = {"content": [{"type": "text", "text": text}]}
            
            elif name == "package_list":
                pm = arguments.get("package_manager", "")
                path = arguments.get("path", ".")
                ext_result = self.extended_tools.package_list(pm, path)
                if "error" in ext_result:
                    result = {"content": [{"type": "text", "text": f"Error: {ext_result['error']}"}]}
                else:
                    packages = ext_result.get('packages', [])
                    text = f"Found {len(packages)} packages:\n\n"
                    for pkg in packages[:50]:  # Show first 50
                        text += f"  {pkg['name']} == {pkg['version']}\n"
                    if len(packages) > 50:
                        text += f"\n... and {len(packages) - 50} more"
                    result = {"content": [{"type": "text", "text": text}]}
            
            elif name == "package_update":
                if not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    pm = arguments.get("package_manager", "")
                    packages = arguments.get("packages")
                    path = arguments.get("path", ".")
                    ext_result = self.extended_tools.package_update(pm, packages, path)
                    if "error" in ext_result:
                        result = {"content": [{"type": "text", "text": f"Error: {ext_result['error']}"}]}
                    else:
                        text = "Update " + ("successful" if ext_result.get('success') else "failed")
                        if ext_result.get('message'):
                            text = ext_result['message']
                        elif ext_result.get('stdout'):
                            text += f"\n\n{ext_result['stdout'][-2000:]}"
                        result = {"content": [{"type": "text", "text": text}]}
            
            # Build and test
            elif name == "run_build":
                if not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    build_tool = arguments.get("build_tool", "")
                    path = arguments.get("path", ".")
                    target = arguments.get("target")
                    ext_result = self.extended_tools.run_build(build_tool, path, target)
                    if "error" in ext_result:
                        result = {"content": [{"type": "text", "text": f"Error: {ext_result['error']}"}]}
                    else:
                        text = f"Build {'succeeded' if ext_result['success'] else 'failed'}\n"
                        text += f"Return code: {ext_result['return_code']}\n\n"
                        if ext_result['stdout']:
                            text += f"Output:\n{ext_result['stdout']}"
                        if ext_result['stderr']:
                            text += f"\n\nErrors:\n{ext_result['stderr']}"
                        result = {"content": [{"type": "text", "text": text}]}
            
            elif name == "run_tests":
                test_framework = arguments.get("test_framework", "")
                path = arguments.get("path", ".")
                pattern = arguments.get("pattern")
                ext_result = self.extended_tools.run_tests(test_framework, path, pattern)
                if "error" in ext_result:
                    result = {"content": [{"type": "text", "text": f"Error: {ext_result['error']}"}]}
                else:
                    text = f"Tests {'passed' if ext_result['success'] else 'failed'}\n"
                    if ext_result.get('summary'):
                        s = ext_result['summary']
                        text += f"\nSummary: {s['passed']} passed, {s['failed']} failed, {s['skipped']} skipped\n"
                    text += f"\n{ext_result['stdout']}"
                    result = {"content": [{"type": "text", "text": text}]}
            
            # Database operations
            elif name == "db_connect":
                db_type = arguments.get("db_type", "")
                conn_str = arguments.get("connection_string", "")
                ext_result = self.extended_tools.db_connect(db_type, conn_str)
                if "error" in ext_result:
                    result = {"content": [{"type": "text", "text": f"Error: {ext_result['error']}"}]}
                else:
                    text = f"Connected to {db_type} database\n"
                    text += f"Tables ({len(ext_result['tables'])}):\n"
                    for table in ext_result['tables']:
                        text += f"  - {table}\n"
                    result = {"content": [{"type": "text", "text": text}]}
            
            elif name == "db_query":
                # Check write permission for write queries
                query_lower = arguments.get("query", "").strip().lower()
                is_write_query = any(query_lower.startswith(cmd) for cmd in ["insert", "update", "delete", "create", "drop", "alter"])
                
                if is_write_query and not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    db_type = arguments.get("db_type", "")
                    conn_str = arguments.get("connection_string", "")
                    query = arguments.get("query", "")
                    params = arguments.get("params")
                    ext_result = self.extended_tools.db_query(db_type, conn_str, query, params)
                    if "error" in ext_result:
                        result = {"content": [{"type": "text", "text": f"Error: {ext_result['error']}"}]}
                    elif ext_result.get('data'):
                        # Format query results
                        text = f"Query returned {ext_result['rows']} rows\n\n"
                        if ext_result['data']:
                            # Show as table
                            import json
                            text += json.dumps(ext_result['data'][:10], indent=2)
                            if ext_result['truncated']:
                                text += "\n\n... results truncated"
                        result = {"content": [{"type": "text", "text": text}]}
                    elif ext_result.get('affected_rows') is not None:
                        text = f"{ext_result['operation']} affected {ext_result['affected_rows']} rows"
                        result = {"content": [{"type": "text", "text": text}]}
                    else:
                        result = {"content": [{"type": "text", "text": "Query executed successfully"}]}
            
            elif name == "db_schema":
                db_type = arguments.get("db_type", "")
                conn_str = arguments.get("connection_string", "")
                table = arguments.get("table")
                ext_result = self.extended_tools.db_schema(db_type, conn_str, table)
                if "error" in ext_result:
                    result = {"content": [{"type": "text", "text": f"Error: {ext_result['error']}"}]}
                else:
                    import json
                    result = {"content": [{"type": "text", "text": json.dumps(ext_result, indent=2)}]}
            
            # API testing
            elif name == "api_request":
                method = arguments.get("method", "")
                url = arguments.get("url", "")
                headers = arguments.get("headers", {})
                data = arguments.get("data")
                params = arguments.get("params")
                timeout = arguments.get("timeout", 30)
                ext_result = self.extended_tools.api_request(method, url, headers, data, params, timeout)
                if "error" in ext_result:
                    result = {"content": [{"type": "text", "text": f"Error: {ext_result['error']}"}]}
                else:
                    text = f"{method} {url}\n"
                    text += f"Status: {ext_result['status_code']}\n"
                    text += f"Time: {ext_result['elapsed_seconds']}s\n"
                    text += f"Size: {ext_result.get('size_bytes', 0)} bytes\n\n"
                    if ext_result.get('json'):
                        import json
                        text += "Response (JSON):\n" + json.dumps(ext_result['json'], indent=2)[:5000]
                    else:
                        text += "Response:\n" + ext_result['body'][:5000]
                    result = {"content": [{"type": "text", "text": text}]}
            
            elif name == "api_test_suite":
                suite_file = arguments.get("suite_file", "")
                ext_result = self.extended_tools.api_test_suite(suite_file)
                if "error" in ext_result:
                    result = {"content": [{"type": "text", "text": f"Error: {ext_result['error']}"}]}
                else:
                    text = f"Test Suite Results: {ext_result['passed']}/{ext_result['total']} passed\n\n"
                    for test in ext_result['tests']:
                        status = "✓" if test['passed'] else "✗"
                        text += f"{status} {test['name']}\n"
                        if test['failures']:
                            for failure in test['failures']:
                                text += f"  - {failure}\n"
                    result = {"content": [{"type": "text", "text": text}]}
            
            # Environment management
            elif name == "env_create":
                if not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    env_type = arguments.get("env_type", "")
                    name = arguments.get("name", "")
                    path = arguments.get("path", ".")
                    ext_result = self.extended_tools.env_create(env_type, name, path)
                    if "error" in ext_result:
                        result = {"content": [{"type": "text", "text": f"Error: {ext_result['error']}"}]}
                    else:
                        text = f"Created {env_type} environment: {name}\n"
                        if ext_result.get('activate'):
                            text += f"Activate with: {ext_result['activate']}"
                        result = {"content": [{"type": "text", "text": text}]}
            
            elif name == "env_list":
                env_type = arguments.get("env_type", "")
                ext_result = self.extended_tools.env_list(env_type)
                if "error" in ext_result:
                    result = {"content": [{"type": "text", "text": f"Error: {ext_result['error']}"}]}
                else:
                    envs = ext_result.get('environments', [])
                    text = f"Found {len(envs)} {env_type} environments:\n\n"
                    for env in envs:
                        text += f"  - {env['name']}"
                        if env.get('path'):
                            text += f" ({env['path']})"
                        text += "\n"
                    result = {"content": [{"type": "text", "text": text}]}
            
            elif name == "env_freeze":
                env_type = arguments.get("env_type", "")
                output_file = arguments.get("output_file")
                path = arguments.get("path", ".")
                auth_required = output_file is not None
                
                if auth_required and not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    ext_result = self.extended_tools.env_freeze(env_type, output_file, path)
                    if "error" in ext_result:
                        result = {"content": [{"type": "text", "text": f"Error: {ext_result['error']}"}]}
                    elif output_file:
                        text = f"Exported to {output_file} ({ext_result.get('packages', 'unknown')} packages)"
                        result = {"content": [{"type": "text", "text": text}]}
                    else:
                        text = ext_result.get('requirements', '') or str(ext_result)
                        result = {"content": [{"type": "text", "text": text}]}
"""

# ========== FULL INTEGRATION EXAMPLE ==========

print("""
INTEGRATION COMPLETE!

To integrate the extended tools:

1. Copy extended_tools.py to the filesystem_mcp directory
2. Apply the changes shown above to hak_gal_filesystem.py
3. Restart the MCP server

The new tools will be available through the MCP interface:
- Git operations (status, log, branch, commit, push, pull)
- Package management (pip, npm, yarn, nuget)
- Build tools (make, maven, gradle, npm, dotnet, cargo)
- Test runners (pytest, unittest, jest, mocha, dotnet, cargo)
- Database operations (SQLite queries and schema)
- API testing (HTTP requests and test suites)
- Environment management (Python, Conda, Node.js)

All write operations require the auth_token parameter.
""")
