// Add this new category to NODE_CATALOG in WorkflowPro.tsx

WORKFLOW_ESSENTIALS: {
  label: 'Workflow Essentials',
  icon: Settings,  // or Wrench
  color: '#22c55e', // Green
  tools: [
    { id: 'evaluate_expression', label: 'Evaluate Expression', params: { expression: '2 + 2', variables: {}, safe_mode: true }},
    { id: 'set_variable', label: 'Set Variable', params: { name: 'myVar', value: '', type: 'auto' }, write: true },
    { id: 'get_variable', label: 'Get Variable', params: { name: 'myVar', default: null }},
    { id: 'merge_branches', label: 'Merge Branches', params: { branch_results: [], strategy: 'all' }},
    { id: 'wait_for_all', label: 'Wait For All', params: { node_ids: [], timeout_ms: 30000, fail_on_any_error: true }},
    { id: 'no_op', label: 'No Operation', params: { message: 'Placeholder node', metadata: {} }},
    { id: 'comment', label: 'Comment', params: { text: 'Add your comment here', author: 'workflow' }},
  ]
},
MONITORING_SCHEDULING: {
  label: 'Monitoring & Scheduling',
  icon: BarChart3,  // or Activity
  color: '#f97316', // Orange
  tools: [
    { id: 'metrics_collector', label: 'Collect Metrics', params: { metric_name: 'workflow_duration', value: 0, type: 'counter', tags: {} }},
    { id: 'workflow_status', label: 'Workflow Status', params: { workflow_id: 'current', include_nodes: true }},
    { id: 'cron_validator', label: 'Validate Cron', params: { expression: '0 9 * * *' }},
    { id: 'recurring_schedule', label: 'Recurring Schedule', params: { name: 'daily_backup', type: 'cron', config: {}, enabled: true }, write: true},
  ]
},

// Also update the imports at the top to include the new icons:
// import { ..., Settings, Wrench, BarChart3, Activity } from 'lucide-react';

// Update the tool count in the status bar from 122 to match actual count:
// Change: <span>Tools: 122</span>
// To: <span>Tools: 125</span>  // or whatever the actual count is