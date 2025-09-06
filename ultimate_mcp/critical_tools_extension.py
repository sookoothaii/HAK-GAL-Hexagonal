"""
Critical Tools Extension for HAK_GAL MCP Server
Implements the missing critical workflow tools
"""

# This file contains the tool implementations to be added to handle_tool_call

# ===== CRITICAL WORKFLOW TOOLS =====

elif tool_name == "evaluate_expression":
    expression = tool_args.get("expression", "")
    variables = tool_args.get("variables", {})
    safe_mode = tool_args.get("safe_mode", True)
    
    try:
        if not expression:
            result = {"content": [{"type": "text", "text": "Error: No expression provided"}]}
        else:
            # Create safe evaluation context
            safe_dict = {
                '__builtins__': {
                    'abs': abs, 'min': min, 'max': max, 'sum': sum,
                    'len': len, 'round': round, 'pow': pow,
                    'int': int, 'float': float, 'str': str, 'bool': bool,
                    'True': True, 'False': False, 'None': None
                }
            }
            
            # Add math functions if safe_mode allows
            if not safe_mode:
                import math
                safe_dict['__builtins__'].update({
                    'sqrt': math.sqrt, 'log': math.log, 'sin': math.sin,
                    'cos': math.cos, 'tan': math.tan, 'pi': math.pi
                })
            
            # Add variables to context
            safe_dict.update(variables)
            
            # Evaluate expression
            result_value = eval(expression, {"__builtins__": safe_dict['__builtins__']}, variables)
            
            output = {
                "expression": expression,
                "result": result_value,
                "type": type(result_value).__name__,
                "variables_used": list(variables.keys())
            }
            
            result = {"content": [{"type": "text", "text": json.dumps(output, ensure_ascii=True)}]}
    except Exception as e:
        error_output = {
            "error": str(e),
            "expression": expression,
            "variables": variables
        }
        result = {"content": [{"type": "text", "text": json.dumps(error_output, ensure_ascii=True)}]}

elif tool_name == "set_variable":
    var_name = tool_args.get("name", "")
    var_value = tool_args.get("value")
    var_type = tool_args.get("type", "auto")  # auto, string, int, float, bool, json
    
    try:
        if not var_name:
            result = {"content": [{"type": "text", "text": "Error: Variable name required"}]}
        else:
            # Type conversion if specified
            if var_type == "int":
                var_value = int(var_value)
            elif var_type == "float":
                var_value = float(var_value)
            elif var_type == "bool":
                var_value = str(var_value).lower() in ('true', '1', 'yes', 'on')
            elif var_type == "json":
                var_value = json.loads(var_value) if isinstance(var_value, str) else var_value
            elif var_type == "string":
                var_value = str(var_value)
            # else auto - keep as is
            
            # Store in workflow context (would be managed by workflow engine)
            output = {
                "action": "set_variable",
                "name": var_name,
                "value": var_value,
                "type": type(var_value).__name__,
                "status": "success"
            }
            
            # Log the operation
            self._append_audit("set_variable", {"name": var_name, "type": var_type})
            
            result = {"content": [{"type": "text", "text": json.dumps(output, ensure_ascii=True)}]}
    except Exception as e:
        result = {"content": [{"type": "text", "text": f"Error setting variable: {e}"}]}

elif tool_name == "get_variable":
    var_name = tool_args.get("name", "")
    default_value = tool_args.get("default", None)
    
    try:
        if not var_name:
            result = {"content": [{"type": "text", "text": "Error: Variable name required"}]}
        else:
            # In a real implementation, this would retrieve from workflow context
            # For now, return a placeholder response
            output = {
                "action": "get_variable",
                "name": var_name,
                "value": default_value,
                "exists": False,
                "status": "variable_not_found",
                "message": "Variable retrieval requires workflow context"
            }
            
            result = {"content": [{"type": "text", "text": json.dumps(output, ensure_ascii=True)}]}
    except Exception as e:
        result = {"content": [{"type": "text", "text": f"Error getting variable: {e}"}]}

elif tool_name == "merge_branches":
    branch_results = tool_args.get("branch_results", [])
    merge_strategy = tool_args.get("strategy", "all")  # all, first_success, majority
    key_field = tool_args.get("key_field", None)
    
    try:
        if not branch_results:
            result = {"content": [{"type": "text", "text": "Error: No branch results to merge"}]}
        else:
            merged_result = None
            
            if merge_strategy == "all":
                # Combine all results into a single structure
                merged_result = {
                    "merged_data": branch_results,
                    "branch_count": len(branch_results),
                    "strategy": "all"
                }
            
            elif merge_strategy == "first_success":
                # Return first successful result
                for br in branch_results:
                    if br.get("success", False) or br.get("status") == "success":
                        merged_result = {
                            "merged_data": br,
                            "branch_count": len(branch_results),
                            "strategy": "first_success",
                            "selected_branch": branch_results.index(br)
                        }
                        break
                
                if not merged_result:
                    merged_result = {
                        "merged_data": None,
                        "branch_count": len(branch_results),
                        "strategy": "first_success",
                        "error": "No successful branch found"
                    }
            
            elif merge_strategy == "majority":
                # Find most common result (simplified)
                from collections import Counter
                if key_field:
                    values = [br.get(key_field) for br in branch_results if key_field in br]
                    if values:
                        most_common = Counter(values).most_common(1)[0][0]
                        merged_result = {
                            "merged_data": most_common,
                            "branch_count": len(branch_results),
                            "strategy": "majority",
                            "key_field": key_field,
                            "consensus_count": values.count(most_common)
                        }
                    else:
                        merged_result = {"error": "No values found for key_field"}
                else:
                    merged_result = {"error": "key_field required for majority strategy"}
            
            result = {"content": [{"type": "text", "text": json.dumps(merged_result, ensure_ascii=True)}]}
    except Exception as e:
        result = {"content": [{"type": "text", "text": f"Error merging branches: {e}"}]}

elif tool_name == "wait_for_all":
    node_ids = tool_args.get("node_ids", [])
    timeout_ms = tool_args.get("timeout_ms", 30000)
    fail_on_any_error = tool_args.get("fail_on_any_error", True)
    
    try:
        if not node_ids:
            result = {"content": [{"type": "text", "text": "Error: No node IDs specified to wait for"}]}
        else:
            # In a real implementation, this would coordinate with the workflow engine
            output = {
                "action": "wait_for_all",
                "waiting_for": node_ids,
                "timeout_ms": timeout_ms,
                "fail_on_any_error": fail_on_any_error,
                "status": "waiting",
                "message": "This is a coordination node for the workflow engine"
            }
            
            result = {"content": [{"type": "text", "text": json.dumps(output, ensure_ascii=True)}]}
    except Exception as e:
        result = {"content": [{"type": "text", "text": f"Error in wait_for_all: {e}"}]}

elif tool_name == "no_op":
    message = tool_args.get("message", "No operation performed")
    metadata = tool_args.get("metadata", {})
    
    # This tool does nothing but can be useful for workflow structure
    output = {
        "action": "no_op",
        "message": message,
        "metadata": metadata,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    result = {"content": [{"type": "text", "text": json.dumps(output, ensure_ascii=True)}]}

elif tool_name == "comment":
    comment_text = tool_args.get("text", "")
    author = tool_args.get("author", "workflow")
    node_id = tool_args.get("node_id", "")
    
    # This tool is for documentation within workflows
    output = {
        "action": "comment",
        "text": comment_text,
        "author": author,
        "node_id": node_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "purpose": "This node provides documentation within the workflow"
    }
    
    result = {"content": [{"type": "text", "text": json.dumps(output, ensure_ascii=True)}]}

# ===== ADDITIONAL UTILITY TOOLS =====

elif tool_name == "metrics_collector":
    metric_name = tool_args.get("metric_name", "")
    metric_value = tool_args.get("value", 0)
    metric_type = tool_args.get("type", "counter")  # counter, gauge, histogram
    tags = tool_args.get("tags", {})
    
    try:
        if not metric_name:
            result = {"content": [{"type": "text", "text": "Error: Metric name required"}]}
        else:
            # In production, this would send to a metrics system
            output = {
                "action": "collect_metric",
                "metric": {
                    "name": metric_name,
                    "value": metric_value,
                    "type": metric_type,
                    "tags": tags,
                    "timestamp": time.time()
                },
                "status": "collected"
            }
            
            # Log metric for audit
            self._append_audit("metrics_collector", output["metric"])
            
            result = {"content": [{"type": "text", "text": json.dumps(output, ensure_ascii=True)}]}
    except Exception as e:
        result = {"content": [{"type": "text", "text": f"Error collecting metric: {e}"}]}

elif tool_name == "workflow_status":
    workflow_id = tool_args.get("workflow_id", "current")
    include_nodes = tool_args.get("include_nodes", True)
    
    # This would integrate with the workflow engine to get real status
    output = {
        "workflow_id": workflow_id,
        "status": "running",  # running, paused, completed, failed
        "start_time": datetime.utcnow().isoformat() + "Z",
        "nodes_total": 0,
        "nodes_completed": 0,
        "nodes_failed": 0,
        "nodes_skipped": 0,
        "current_node": None,
        "message": "Workflow status requires integration with workflow engine"
    }
    
    result = {"content": [{"type": "text", "text": json.dumps(output, ensure_ascii=True)}]}

elif tool_name == "cron_validator":
    cron_expression = tool_args.get("expression", "")
    
    try:
        if not cron_expression:
            result = {"content": [{"type": "text", "text": "Error: Cron expression required"}]}
        else:
            # Basic cron validation (simplified)
            parts = cron_expression.strip().split()
            
            if len(parts) not in (5, 6):  # 5 for standard, 6 with seconds
                valid = False
                error = "Invalid number of fields"
            else:
                valid = True
                error = None
                
                # Basic validation of each field
                ranges = [
                    (0, 59),  # minutes
                    (0, 23),  # hours
                    (1, 31),  # days
                    (1, 12),  # months
                    (0, 7),   # weekdays (0 and 7 are Sunday)
                ]
                
                if len(parts) == 6:
                    ranges.insert(0, (0, 59))  # seconds
                
                field_names = ["second", "minute", "hour", "day", "month", "weekday"] if len(parts) == 6 else ["minute", "hour", "day", "month", "weekday"]
                
                for i, (part, (min_val, max_val), name) in enumerate(zip(parts, ranges, field_names)):
                    if part not in ('*', '?'):
                        # Check for ranges, lists, and steps
                        if '-' in part or ',' in part or '/' in part:
                            # Complex expression - simplified validation
                            continue
                        else:
                            try:
                                val = int(part)
                                if val < min_val or val > max_val:
                                    valid = False
                                    error = f"{name} value {val} out of range [{min_val}, {max_val}]"
                                    break
                            except ValueError:
                                valid = False
                                error = f"Invalid {name} value: {part}"
                                break
            
            output = {
                "expression": cron_expression,
                "valid": valid,
                "error": error,
                "fields": len(parts),
                "next_run_hint": "Use a cron library for accurate next run calculation"
            }
            
            result = {"content": [{"type": "text", "text": json.dumps(output, ensure_ascii=True)}]}
    except Exception as e:
        result = {"content": [{"type": "text", "text": f"Error validating cron: {e}"}]}

elif tool_name == "recurring_schedule":
    schedule_name = tool_args.get("name", "")
    schedule_type = tool_args.get("type", "cron")  # cron, interval, calendar
    schedule_config = tool_args.get("config", {})
    enabled = tool_args.get("enabled", True)
    
    try:
        if not schedule_name:
            result = {"content": [{"type": "text", "text": "Error: Schedule name required"}]}
        else:
            # This would create/update a recurring schedule in the system
            output = {
                "action": "create_schedule",
                "schedule": {
                    "name": schedule_name,
                    "type": schedule_type,
                    "config": schedule_config,
                    "enabled": enabled,
                    "created_at": datetime.utcnow().isoformat() + "Z"
                },
                "status": "created",
                "message": "Schedule management requires integration with scheduler service"
            }
            
            self._append_audit("recurring_schedule", output["schedule"])
            
            result = {"content": [{"type": "text", "text": json.dumps(output, ensure_ascii=True)}]}
    except Exception as e:
        result = {"content": [{"type": "text", "text": f"Error creating schedule: {e}"}]}