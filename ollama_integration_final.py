"""
Ollama Integration für HAK_GAL delegate_task

WICHTIG: Diese Integration muss in die Datei 
D:\MCP Mods\HAK_GAL_HEXAGONAL\ultimate_mcp\hakgal_mcp_ultimate.py
zwischen Zeile 2197 und 2198 eingefügt werden!

Das ist direkt nach dem Claude-Block und vor dem else-Block für unbekannte Agents.
"""

# ===== OLLAMA INTEGRATION - Füge diesen Code zwischen Zeile 2197 und 2198 ein =====
                        # Ollama integration für lokale LLMs
                        elif any(name in target_agent.lower() for name in ["ollama", "qwen"]):
                            if requests is None:
                                result = {"content": [{"type": "text", "text": "Error: requests library not available"}]}
                            else:
                                # Ollama-spezifische Konfiguration
                                ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
                                
                                # Model-Mapping für die 3 verfügbaren Modelle
                                model_map = {
                                    "qwen7b": "qwen2.5:7b",
                                    "qwen14b": "qwen2.5:14b", 
                                    "qwen14b-instruct": "qwen2.5:14b-instruct-q4_K_M",
                                    # Direkte Modellnamen auch unterstützen
                                    "qwen2.5:7b": "qwen2.5:7b",
                                    "qwen2.5:14b": "qwen2.5:14b",
                                    "qwen2.5:14b-instruct-q4_K_M": "qwen2.5:14b-instruct-q4_K_M"
                                }
                                
                                # Extrahiere Modellname aus target_agent
                                model = "qwen2.5:7b"  # Default
                                if ":" in target_agent:
                                    _, model_hint = target_agent.split(":", 1)
                                    model = model_map.get(model_hint, model_hint)
                                
                                # Füge Kontext zur Task hinzu wenn vorhanden
                                full_prompt = task_description
                                if isinstance(context, dict) and context:
                                    context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                                    full_prompt = f"Context:\n{context_str}\n\nTask: {task_description}"
                                
                                # Ollama API-Request  
                                try:
                                    logger.info(f"[Ollama] Using model: {model}")
                                    logger.info(f"[Ollama] Host: {ollama_host}")
                                    
                                    temperature = float(os.environ.get("DELEGATE_TEMPERATURE", "0.2"))
                                    max_tokens = int(os.environ.get("DELEGATE_MAX_TOKENS", "4096"))
                                    
                                    response = requests.post(
                                        f"{ollama_host}/api/generate",
                                        json={
                                            "model": model,
                                            "prompt": full_prompt,
                                            "stream": False,
                                            "temperature": temperature,
                                            "options": {
                                                "num_predict": max_tokens,
                                                "num_ctx": 4096,  # Context window
                                                "top_k": 40,
                                                "top_p": 0.9,
                                                "repeat_penalty": 1.1
                                            }
                                        },
                                        timeout=120  # Ollama kann langsamer sein
                                    )
                                    
                                    if response.status_code == 200:
                                        result_data = response.json()
                                        response_text = result_data.get("response", "No response from Ollama")
                                        
                                        # Log für Debugging
                                        logger.info(f"[Ollama] Response received: {len(response_text)} chars")
                                        logger.debug(f"[Ollama] Full response: {response_text[:500]}...")
                                        
                                        # Audit log
                                        self._append_audit("delegate_task", {
                                            "to": target_agent, 
                                            "model": model,
                                            "task": task_description, 
                                            "ok": True
                                        })
                                        
                                        result = {"content": [{"type": "text", "text": response_text}]}
                                    else:
                                        error_msg = f"Ollama error {response.status_code}: {response.text[:500]}"
                                        logger.error(f"[Ollama] {error_msg}")
                                        result = {"content": [{"type": "text", "text": error_msg}]}
                                        
                                except requests.exceptions.ConnectionError:
                                    error_msg = f"Error: Cannot connect to Ollama at {ollama_host}. Is Ollama running?"
                                    logger.error(f"[Ollama] Connection error: {error_msg}")
                                    result = {"content": [{"type": "text", "text": error_msg}]}
                                except requests.exceptions.Timeout:
                                    error_msg = "Error: Ollama request timeout (120s). Try a smaller model or shorter prompt."
                                    logger.error(f"[Ollama] Timeout error")
                                    result = {"content": [{"type": "text", "text": error_msg}]}
                                except Exception as e:
                                    error_msg = f"Ollama request failed: {e}"
                                    logger.error(f"[Ollama] {error_msg}")
                                    result = {"content": [{"type": "text", "text": error_msg}]}

# ===== ENDE DER OLLAMA INTEGRATION =====

"""
Verwendung nach der Integration:

1. Stelle sicher, dass Ollama läuft:
   ollama serve

2. Verwende die delegate_task Funktion mit diesen Varianten:

   # Mit Default-Modell (qwen2.5:7b)
   delegate_task(target_agent="ollama", task_description="...")
   
   # Mit spezifischem Modell (Kurzform)
   delegate_task(target_agent="ollama:qwen7b", task_description="...")
   delegate_task(target_agent="ollama:qwen14b", task_description="...")
   delegate_task(target_agent="ollama:qwen14b-instruct", task_description="...")
   
   # Mit vollem Modellnamen
   delegate_task(target_agent="ollama:qwen2.5:7b", task_description="...")
   delegate_task(target_agent="ollama:qwen2.5:14b", task_description="...")
   delegate_task(target_agent="ollama:qwen2.5:14b-instruct-q4_K_M", task_description="...")

3. Optionale Umgebungsvariablen:
   - OLLAMA_HOST (default: http://localhost:11434)
   - DELEGATE_TEMPERATURE (default: 0.2)
   - DELEGATE_MAX_TOKENS (default: 4096)

Features:
- Alle 3 Modelle werden unterstützt
- Context wird automatisch eingefügt wenn vorhanden
- Ausführliches Logging für Debugging
- Fehlerbehandlung für Connection/Timeout
- Audit-Logging für alle Anfragen
"""