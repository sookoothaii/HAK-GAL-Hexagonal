# Add these tool definitions to the _get_tool_list() function in hakgal_mcp_ultimate.py

# ===== CRITICAL WORKFLOW TOOLS =====
{
    "name": "evaluate_expression",
    "description": "Evaluate mathematical or logical expressions with variables",
    "inputSchema": {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "Expression to evaluate (e.g., 'x * 2 + y')"},
            "variables": {"type": "object", "description": "Variables to use in expression", "default": {}},
            "safe_mode": {"type": "boolean", "description": "Restrict to safe operations", "default": True}
        },
        "required": ["expression"]
    }
},
{
    "name": "set_variable",
    "description": "Set a variable in the workflow context",
    "inputSchema": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Variable name"},
            "value": {"description": "Variable value (any type)"},
            "type": {"type": "string", "enum": ["auto", "string", "int", "float", "bool", "json"], "default": "auto"}
        },
        "required": ["name", "value"]
    }
},
{
    "name": "get_variable",
    "description": "Get a variable from the workflow context",
    "inputSchema": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Variable name"},
            "default": {"description": "Default value if variable not found"}
        },
        "required": ["name"]
    }
},
{
    "name": "merge_branches",
    "description": "Merge results from multiple workflow branches",
    "inputSchema": {
        "type": "object",
        "properties": {
            "branch_results": {"type": "array", "description": "Array of branch results to merge"},
            "strategy": {"type": "string", "enum": ["all", "first_success", "majority"], "default": "all"},
            "key_field": {"type": "string", "description": "Field to use for majority strategy"}
        },
        "required": ["branch_results"]
    }
},
{
    "name": "wait_for_all",
    "description": "Wait for multiple parallel nodes to complete",
    "inputSchema": {
        "type": "object",
        "properties": {
            "node_ids": {"type": "array", "items": {"type": "string"}, "description": "Node IDs to wait for"},
            "timeout_ms": {"type": "integer", "description": "Timeout in milliseconds", "default": 30000},
            "fail_on_any_error": {"type": "boolean", "description": "Fail if any node fails", "default": True}
        },
        "required": ["node_ids"]
    }
},
{
    "name": "no_op",
    "description": "No operation - placeholder node for workflow structure",
    "inputSchema": {
        "type": "object",
        "properties": {
            "message": {"type": "string", "description": "Optional message", "default": "No operation performed"},
            "metadata": {"type": "object", "description": "Optional metadata", "default": {}}
        }
    }
},
{
    "name": "comment",
    "description": "Add a comment/documentation node to the workflow",
    "inputSchema": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Comment text"},
            "author": {"type": "string", "description": "Comment author", "default": "workflow"},
            "node_id": {"type": "string", "description": "Associated node ID"}
        },
        "required": ["text"]
    }
},

# ===== ADDITIONAL UTILITY TOOLS =====
{
    "name": "metrics_collector",
    "description": "Collect performance metrics from workflow execution",
    "inputSchema": {
        "type": "object",
        "properties": {
            "metric_name": {"type": "string", "description": "Name of the metric"},
            "value": {"type": "number", "description": "Metric value", "default": 0},
            "type": {"type": "string", "enum": ["counter", "gauge", "histogram"], "default": "counter"},
            "tags": {"type": "object", "description": "Metric tags", "default": {}}
        },
        "required": ["metric_name"]
    }
},
{
    "name": "workflow_status",
    "description": "Get the current workflow execution status",
    "inputSchema": {
        "type": "object",
        "properties": {
            "workflow_id": {"type": "string", "description": "Workflow ID", "default": "current"},
            "include_nodes": {"type": "boolean", "description": "Include node details", "default": True}
        }
    }
},
{
    "name": "cron_validator",
    "description": "Validate and parse cron expressions",
    "inputSchema": {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "Cron expression to validate"}
        },
        "required": ["expression"]
    }
},
{
    "name": "recurring_schedule",
    "description": "Create or manage recurring workflow schedules",
    "inputSchema": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Schedule name"},
            "type": {"type": "string", "enum": ["cron", "interval", "calendar"], "default": "cron"},
            "config": {"type": "object", "description": "Schedule configuration"},
            "enabled": {"type": "boolean", "description": "Enable schedule", "default": True}
        },
        "required": ["name"]
    }
}