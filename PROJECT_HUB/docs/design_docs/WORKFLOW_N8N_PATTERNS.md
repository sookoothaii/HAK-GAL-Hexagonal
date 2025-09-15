---
title: "Workflow N8N Patterns"
created: "2025-09-15T00:08:00.994662Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Workflow Patterns: n8n Best Practices für HAK-GAL
**Date**: 2025-09-16  
**Purpose**: Mapping n8n workflow patterns to HAK-GAL WorkflowPro capabilities

## Overview

This document maps n8n's proven workflow patterns to HAK-GAL's WorkflowPro implementation, providing guidance for building robust, production-ready workflows.

## 1. Persistent State Management

### n8n Challenge
- State is lost between workflow executions
- Requires external databases (PostgreSQL, Redis)

### HAK-GAL Solution
WorkflowPro already includes comprehensive state management tools:

```javascript
// Available State Tools
STATE_MANAGEMENT: {
  tools: [
    { id: 'get_global_state', params: { key: '', default: null }},
    { id: 'set_global_state', params: { key: '', value: '' }, write: true},
    { id: 'get_workflow_context', params: { context_path: '' }},
    { id: 'set_workflow_context', params: { context_path: '', value: '' }, write: true},
    { id: 'incr_counter', params: { counter_name: '', step: 1 }, write: true},
    { id: 'atomic_transaction', params: { keys: [], operations: [] }, write: true}
  ]
}
```

### Implementation Pattern
```yaml
Workflow: Daily Report Generator
Steps:
  1. get_global_state → 'last_run_timestamp'
  2. search_knowledge → query since last run
  3. process data → generate report
  4. set_global_state → update timestamp
  5. atomic_transaction → ensure consistency
```

### Best Practice
- Use `atomic_transaction` for critical state updates
- Implement state versioning with timestamps
- Regular state cleanup with `db_vacuum`

## 2. Error Handling Across Node Boundaries

### n8n Approach
- Error Workflows
- Error Trigger Nodes
- Stop and Error Node

### HAK-GAL Enhanced Error Handling

```javascript
ERROR_HANDLING: {
  tools: [
    { id: 'try_catch', params: { try_nodes: [], catch_nodes: [], finally_nodes: [] }},
    { id: 'retry_with_backoff', params: { max_retries: 3, backoff_ms: 1000 }},
    { id: 'circuit_breaker', params: { failure_threshold: 5, timeout_ms: 30000 }},
    { id: 'fallback_chain', params: { fallback_nodes: [], default_value: null }},
    { id: 'error_transform', params: { error_map: {}, default_success: true }}
  ]
}
```

### Error Workflow Pattern
```yaml
Main Workflow:
  1. try_catch wrapper
     - try: [risky_operation_1, risky_operation_2]
     - catch: [log_error, notify_admin, trigger_error_workflow]
     - finally: [cleanup_resources]

Error Recovery Workflow:
  1. get_global_state → 'error_context'
  2. analyze error type
  3. branch on error category:
     - Network: retry_with_backoff
     - Data: fallback_chain
     - Critical: circuit_breaker + alert
```

### Recommended Implementation
```typescript
// Add to WorkflowDefinition
interface WorkflowDefinition {
  errorWorkflowId?: string;
  errorHandling?: 'stop' | 'continue' | 'delegate';
  maxRetries?: number;
  retryDelay?: number;
}
```

## 3. Loops in DAG Model

### n8n Features
- SplitInBatches for large datasets
- IF-Nodes with branches
- Automatic item processing

### HAK-GAL Loop Patterns

```javascript
ITERATION: {
  tools: [
    { id: 'for_each', params: { array_field: 'items', batch_size: 1 }},
    { id: 'split_in_batches', params: { batch_size: 10, reset: false }},
    { id: 'loop_over_items', params: { max_iterations: 100 }},
    { id: 'map_transform', params: { transform_expression: '{{ $item * 2 }}' }},
    { id: 'reduce_aggregate', params: { operation: 'sum', field: 'value' }}
  ]
}
```

### Common Loop Patterns

#### Pattern 1: Batch Processing Large Datasets
```yaml
Workflow: Process 10,000 KB Facts
  1. get_facts_count → total items
  2. split_in_batches → size: 100
  3. for_each batch:
     - process items
     - set_global_state → progress counter
  4. reduce_aggregate → compile results
```

#### Pattern 2: Conditional Loop with Exit
```yaml
Workflow: Find First Match
  1. loop_over_items → max: 1000
  2. if_condition → match found?
     - true: break loop, return result
     - false: continue
  3. fallback → "No match found"
```

#### Pattern 3: Parallel Processing
```yaml
Workflow: Multi-Source Data Collection
  1. parallel execution:
     - branch 1: query_knowledge_base
     - branch 2: delegate_to_gemini
     - branch 3: search_sentry_issues
  2. merge_data → combine results
  3. reduce_aggregate → unified report
```

## 4. Advanced Patterns

### Rate Limiting Pattern
```yaml
Workflow: API Data Sync
  1. get_global_state → 'api_call_count'
  2. rate_limiter → max: 100/hour
  3. http_request → external API
  4. incr_counter → update call count
  5. delay → respect rate limits
```

### Checkpoint & Resume Pattern
```yaml
Workflow: Long-Running Analysis
  1. get_workflow_context → 'checkpoint'
  2. if checkpoint exists:
     - resume from checkpoint
  3. for_each item:
     - process item
     - every 10 items: set_workflow_context → save checkpoint
  4. on completion: clear checkpoint
```

### Data Validation Pipeline
```yaml
Workflow: Import External Data
  1. read_file → CSV/JSON input
  2. data_validator → schema validation
  3. for_each record:
     - validate_facts → syntax check
     - semantic_similarity → duplicate check
     - if valid: add_fact
     - else: log to error file
  4. generate import report
```

## 5. Production Best Practices

### Monitoring & Observability
- Use `breakpoint` nodes in development
- Add `log_node_input/output` for debugging
- Implement `health_check` at critical points
- Regular `consistency_check` for data integrity

### Performance Optimization
- Batch operations with `bulk_add_facts`
- Use `parallel` nodes for independent tasks
- Implement `cache` pattern with `get/set_global_state`
- Regular `db_vacuum` for database optimization

### Testing Strategies
- Use `mock_data` nodes for unit testing
- Implement `assert_condition` for validation
- Create test workflows with `test_trigger`
- Use `dry_run` mode for safe testing

## 6. Migration Guide: n8n to WorkflowPro

### Mapping n8n Nodes to HAK-GAL Tools

| n8n Node | HAK-GAL Equivalent | Notes |
|----------|-------------------|--------|
| HTTP Request | `http_request`, `webhook_send` | Full REST support |
| IF | `if_condition`, `switch_case` | Enhanced branching |
| SplitInBatches | `split_in_batches` | Direct equivalent |
| Set | `set_fields`, `set_workflow_context` | Context-aware |
| Function | `execute_code` | Python/JS/Bash |
| Wait | `delay`, `wait_for_webhook` | Time-based control |
| Error Trigger | `try_catch` wrapper | Built-in error handling |

### Code Example: n8n Function to HAK-GAL
```javascript
// n8n Function Node
return items.map(item => ({
  ...item,
  json: {
    ...item.json,
    processed: true,
    timestamp: new Date()
  }
}));

// HAK-GAL execute_code equivalent
execute_code: {
  language: 'javascript',
  code: `
    const items = input.items;
    return items.map(item => ({
      ...item,
      processed: true,
      timestamp: new Date().toISOString()
    }));
  `
}
```

## 7. Resources & References

### HAK-GAL Specific
- WorkflowPro UI: Frontend workflow builder
- MCP Tools: 68 backend tools available
- Write Operations: 22 tools with write capability

### Community & Support
- HAK-GAL PROJECT_HUB: Central documentation
- Knowledge Base: Query with `search_knowledge`
- System Status: Check with `health_check`

### Workflow Examples Repository
Located in: `PROJECT_HUB/WORKFLOW_EXAMPLES.md`

## 8. Enhanced Production Guidance

### TTL and Expiring State Management

#### Implementation Pattern
```yaml
Workflow: Auto-Expiring Session State
  1. set_global_state:
     - key: 'session_{{user_id}}'
     - value: { data: '...', expires_at: '{{$now.plus(3600)}}' }
  2. Cleanup Workflow (scheduled):
     - get_global_state → all keys with 'session_*'
     - filter: expires_at < now
     - bulk_delete expired states
```

#### State Snapshotting Strategy
```yaml
Periodic State Backup:
  1. Schedule: every 6 hours
  2. Actions:
     - export all global_state → JSON
     - db_backup_now → timestamped backup
     - rotate old snapshots (keep last 10)
  3. Recovery procedure documented
```

> ⚠️ **Pitfalls & Recommendations - State Management**
> - **Zombie States**: Implement TTL for all temporary states
> - **State Bloat**: Regular cleanup with `db_vacuum`
> - **Lost State**: Always snapshot before major operations
> - **Race Conditions**: Use `atomic_transaction` for concurrent access

### Structured Error Handling

#### Error Normalization Pattern
```javascript
// Standard Error Format
{
  code: 'ERR_API_RATE_LIMIT',
  message: 'API rate limit exceeded',
  context: {
    endpoint: '/api/v1/data',
    limit: 100,
    window: '1h',
    retry_after: 3600
  },
  timestamp: '2025-09-16T15:30:00Z',
  workflow_id: 'wf-123',
  node_id: 'http-request-1'
}
```

#### Error Telemetry Integration
```yaml
Error Monitoring Pipeline:
  1. try_catch wrapper → capture all errors
  2. error_transform → normalize to standard format
  3. parallel execution:
     - sentry_report → real-time alerting
     - add_fact → 'ErrorOccurred({{code}}, {{workflow_id}})'
     - incr_counter → 'errors_{{code}}'
  4. health_check → update dashboard metrics
```

> ⚠️ **Pitfalls & Recommendations - Error Handling**
> - **Silent Failures**: Always log errors, never swallow them
> - **Alert Fatigue**: Group similar errors, implement throttling
> - **Missing Context**: Include workflow_id and node_id in all errors
> - **Recovery Chaos**: Test error workflows with chaos engineering

### Advanced Loop Strategies

#### Hybrid Loop Selection Guide
| Use Case | Tool | When to Use | Resource Impact |
|----------|------|-------------|-----------------|
| Simple iteration | `for_each` | < 100 items, no API calls | Low |
| API pagination | `split_in_batches` | External APIs, rate limits | Medium |
| Conditional repeat | `loop_over_items` | Search until found | Variable |
| Parallel processing | `parallel` + `for_each` | Independent operations | High |

#### Exit Guards Implementation
```yaml
Safe Loop Pattern:
  1. set_global_state → 'loop_guard_{{workflow_id}}' = 0
  2. loop_over_items:
     - max_iterations: 1000 (hard limit)
     - exit conditions:
       a. result found
       b. counter > threshold
       c. timeout exceeded
  3. finally: clear loop guard
```

### Idempotency Patterns

```yaml
API Sync with Idempotency:
  1. generate idempotency_key: '{{workflow_id}}_{{timestamp}}_{{hash}}'
  2. check if already processed:
     - get_global_state → 'idem_{{key}}'
     - if exists: skip
  3. process:
     - http_request with header 'Idempotency-Key'
     - set_global_state → mark as processed
  4. cleanup old keys (TTL: 24h)
```

### Checkpoint & Resume Architecture

```yaml
Long-Running Workflow with Checkpoints:
  1. Initial Setup:
     - workflow_id: generate unique ID
     - set_workflow_context → initialize checkpoint
  
  2. Processing Loop:
     for_each item:
       - process item
       - every 10 items:
         * set_workflow_context → {
             last_processed: item_id,
             progress: percentage,
             state: current_data
           }
  
  3. Resume Logic:
     - get_workflow_context → checkpoint
     - if checkpoint exists:
       * skip to last_processed + 1
       * restore state
       * continue processing
```

> ⚠️ **Pitfalls & Recommendations - Advanced Patterns**
> - **Idempotency Leaks**: Always use unique keys with TTL
> - **Checkpoint Corruption**: Validate checkpoint data before resume
> - **Infinite Loops**: Mandatory exit conditions + monitoring
> - **State Explosion**: Limit checkpoint size, use references

### Production Deployment Strategies

#### Blue/Green Workflow Deployment
```yaml
Deployment Process:
  1. Current: workflow_v1 (blue) running
  2. Deploy: workflow_v2 (green) in parallel
  3. Traffic Split:
     - 10% to green (canary)
     - monitor error rates
  4. Gradual rollout:
     - 25% → 50% → 100%
  5. Rollback trigger: error rate > threshold
```

#### Chaos Testing Scenarios
```yaml
Test Suite:
  1. API Failures:
     - 429 Rate Limit
     - 500 Internal Server
     - Network timeout
  2. State Corruption:
     - Invalid checkpoint data
     - Missing state keys
  3. Resource Limits:
     - Memory exhaustion
     - CPU throttling
  4. Validate error workflows handle all cases
```

### HTTP Pagination Patterns

#### n8n Manual vs WorkflowPro Automated
```yaml
# n8n Approach (Manual)
1. HTTP Request → page 1
2. Check: has_next_page?
3. Loop back to step 1 with page + 1

# WorkflowPro Automated Pattern
1. http_paginated_request:
   - url: '/api/items'
   - pagination_type: 'cursor' | 'page' | 'offset'
   - max_pages: 100
   - combine_results: true
2. Automatic handling of:
   - Next page detection
   - Rate limit respect
   - Result aggregation
```

### Monitoring & Observability Enhanced

```yaml
Production Monitoring Stack:
  1. Metrics Collection:
     - execution_duration per node
     - error_rate by type
     - throughput (items/second)
  
  2. Dashboards:
     - Real-time workflow status
     - Error heatmap by node
     - Resource utilization
  
  3. Alerts:
     - Execution time > 2x average
     - Error rate > 5%
     - State size > 1MB
```

> ⚠️ **Master Pitfalls & Recommendations**
> - **No Monitoring**: Can't improve what you don't measure
> - **Missing Rollback**: Always have a quick rollback plan
> - **Untested Errors**: Chaos test before production
> - **State Management**: TTL everything, snapshot critical state
> - **Loop Safety**: Exit conditions are mandatory, not optional
> - **Error Context**: Structured errors save debugging time

## 9. Quick Reference Card

### State Management Checklist
- [ ] TTL for temporary states
- [ ] Atomic transactions for critical updates
- [ ] Regular snapshots (6h)
- [ ] Cleanup job scheduled

### Error Handling Checklist
- [ ] Structured error format
- [ ] Error workflows tested
- [ ] Monitoring integration
- [ ] Recovery procedures documented

### Loop Safety Checklist
- [ ] Exit conditions defined
- [ ] Max iterations set
- [ ] Progress tracking
- [ ] Resource limits checked

### Production Checklist
- [ ] Blue/green deployment ready
- [ ] Chaos tests passed
- [ ] Monitoring dashboards live
- [ ] Rollback procedure tested

---
*Based on n8n community best practices adapted for HAK-GAL WorkflowPro v2.1*
*Enhanced with production operational guidance v2.0*
