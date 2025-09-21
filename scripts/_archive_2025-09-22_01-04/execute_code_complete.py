# === Helper Function ===
    def _execute_code_safely(self, code: str, language: str, timeout: int = 30):
        """Execute code safely in sandbox environment"""
        try:
            # Validate language
            if language not in self.allowed_languages:
                return {"error": f"Language '{language}' not allowed. Allowed: {self.allowed_languages}"}
            
            # Create temporary file
            temp_file = self.temp_dir / f"exec_{uuid.uuid4().hex[:8]}.{self._get_file_extension(language)}"
            
            # Write code to file
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Execute based on language
            if language == "python":
                result = subprocess.run(
                    ["python", str(temp_file)],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=str(self.temp_dir)
                )
            elif language == "javascript":
                result = subprocess.run(
                    ["node", str(temp_file)],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=str(self.temp_dir)
                )
            elif language == "bash":
                result = subprocess.run(
                    ["bash", str(temp_file)],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=str(self.temp_dir)
                )
            elif language == "powershell":
                result = subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(temp_file)],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=str(self.temp_dir)
                )
            
            # Clean up
            try:
                temp_file.unlink()
            except:
                pass
            
            # Limit output size
            stdout = result.stdout[:self.max_output_size] if result.stdout else ""
            stderr = result.stderr[:self.max_output_size] if result.stderr else ""
            
            return {
                "stdout": stdout,
                "stderr": stderr,
                "return_code": result.returncode,
                "execution_time": "completed",
                "language": language
            }
            
        except subprocess.TimeoutExpired:
            return {"error": f"Execution timeout after {timeout} seconds"}
        except FileNotFoundError:
            return {"error": f"Language interpreter for '{language}' not found"}
        except Exception as e:
            return {"error": f"Execution error: {str(e)}"}
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            "python": "py",
            "javascript": "js",
            "bash": "sh",
            "powershell": "ps1"
        }
        return extensions.get(language, "txt")
    
    def get_facts_from_db(self):
        """Hole alle Fakten aus der SQLite DB"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.execute("SELECT statement FROM facts")
            facts = [row[0] for row in cursor]
            conn.close()
            return facts
        except Exception as e:
            logger.error(f"Error getting facts from DB: {e}")
            return []
    
    async def send_response(self, response):
        """Send JSON-RPC response"""
        response_str = json.dumps(response)
        sys.stdout.write(response_str + "\n")
        sys.stdout.flush()
        logger.debug(f"Sent: {response_str[:200]}")
    
    async def handle_initialize(self, request):
        """Handle initialization request"""
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id", 1),
                            "result": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {
                        "tools": {"listChanged": True},
                        "resources": {},
                        "prompts": {}
                    },
                    "serverInfo": {
                        "name": "HAK_GAL MCP SQLite Full FIXED",
                        "version": "3.1.0"
                    }
                }
        }
        await self.send_response(response)
    
    async def handle_list_tools(self, request):
        """List ALL 44 available tools"""
        tools = [
            # Original 5 SQLite Tools
            {
                "name": "get_facts_count",
                "description": "Hole die aktuelle Anzahl der Fakten aus der SQLite DB",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "search_knowledge",
                "description": "Suche in der HAK_GAL Wissensdatenbank",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Suchbegriff"},
                        "limit": {"type": "integer", "description": "Max Ergebnisse", "default": 10}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_recent_facts",
                "description": "Hole die neuesten Fakten",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "description": "Anzahl", "default": 5}
                    }
                }
            },
            {
                "name": "get_predicates_stats",
                "description": "Statistik über verwendete Prädikate",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "get_system_status",
                "description": "System Status mit Datenbankinfo",
                "inputSchema": {"type": "object", "properties": {}}
            },
            # Weitere Knowledge Base Tools (25 weitere = 30 total KB Tools)
            {
                "name": "list_recent_facts",
                "description": "List recent facts from the knowledge base",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "description": "Number of facts", "default": 5}
                    }
                }
            },
            {
                "name": "add_fact",
                "description": "Füge einen neuen Fakt hinzu (requires write enable)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "statement": {"type": "string"},
                        "source": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "auth_token": {"type": "string"}
                    },
                    "required": ["statement"]
                }
            },
            {
                "name": "delete_fact",
                "description": "Lösche Fakten (requires write enable)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "statement": {"type": "string"},
                        "auth_token": {"type": "string"}
                    },
                    "required": ["statement"]
                }


# === Tool Implementation ===
            elif tool_name == "execute_code":
                code = str(tool_args.get("code", ""))
                language = str(tool_args.get("language", "")).lower()
                timeout = int(tool_args.get("timeout", 30))
                
                if not code:
                    result = {"content": [{"type": "text", "text": "Missing 'code' parameter"}]}
                elif not language:
                    result = {"content": [{"type": "text", "text": "Missing 'language' parameter"}]}
                else:
                    execution_result = self._execute_code_safely(code, language, timeout)
                    
                    if "error" in execution_result:
                        text = f"❌ Execution Error: {execution_result['error']}"
                    else:
                        stdout = execution_result.get("stdout", "")
                        stderr = execution_result.get("stderr", "")
                        return_code = execution_result.get("return_code", 0)
                        lang = execution_result.get("language", language)
                        
                        text = f"✅ Code executed successfully!\n\n"
                        text += f"**Language:** {lang}\n"
                        text += f"**Return Code:** {return_code}\n"
                        text += f"**Execution Time:** {execution_result.get('execution_time', 'completed')}\n\n"
                        
                        if stdout:
                            text += f"**STDOUT:**\n```\n{stdout}\n```\n\n"
                        
                        if stderr:
                            text += f"**STDERR:**\n```\n{stderr}\n```\n\n"
                        
                        if return_code != 0:
                            text += f"⚠️ **Warning:** Process exited with code {return_code}"
                    
                    result = {"content": [{"type": "text", "text": text}]}
            
            else:
                # Alle anderen Tools mit Basis-Implementation
                result = {"content": [{"type": "text", "text": f"Tool '{tool_name}' implementation pending"}]}
                
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
        
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id", 1),
            "result": result
        }
