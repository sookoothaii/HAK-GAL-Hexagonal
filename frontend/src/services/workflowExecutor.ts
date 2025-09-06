import { WorkflowDefinition, WorkflowRunResult } from '@/types/workflow';

export async function dryRunWorkflow(def: WorkflowDefinition): Promise<WorkflowRunResult> {
  const runId = `wf-${Date.now()}`;
  const logs: WorkflowRunResult['logs'] = [];
  for (const n of def.nodes) {
    const isWrite = n.name.startsWith('add_') || n.name.startsWith('update_') || n.name.startsWith('delete_') || n.name.startsWith('backup_');
    if (isWrite && n.approvalRequired !== false) {
      logs.push({ nodeId: n.id, status: 'skipped', message: 'write-sensitive node skipped (no approval)' });
      continue;
    }
    logs.push({ nodeId: n.id, status: 'planned', message: `Call tool ${n.name} with ${JSON.stringify(n.params || {})}` });
  }
  return { runId, ok: true, logs };
}

export async function executeWorkflow(def: WorkflowDefinition, authToken?: string): Promise<WorkflowRunResult> {
  const runId = `wf-live-${Date.now()}`;
  const logs: WorkflowRunResult['logs'] = [];
  const mcpEndpoint = 'http://localhost:5002'; // TODO: Make configurable

  for (const n of def.nodes) {
    logs.push({ nodeId: n.id, status: 'planned', message: `Executing tool ${n.name}...` });

    try {
      const isWriteSensitive = n.approvalRequired; // Assuming approvalRequired implies write-sensitive

      // Check for write permissions if needed
      if (isWriteSensitive && !authToken) {
        logs.push({ nodeId: n.id, status: 'error', message: 'Write-sensitive node requires authentication token.' });
        continue;
      }

      const toolArgs = { ...n.params };
      if (isWriteSensitive && authToken) {
        toolArgs.auth_token = authToken;
      }

      // Construct JSON-RPC request
      const requestPayload = {
        jsonrpc: '2.0',
        method: 'tools/call',
        params: {
          name: n.name,
          arguments: toolArgs,
        },
        id: `${n.id}-${Date.now()}`,
      };

      const response = await fetch(mcpEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestPayload),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! Status: ${response.status}, Body: ${errorText}`);
      }

      const jsonResponse = await response.json();

      if (jsonResponse.error) {
        logs.push({ nodeId: n.id, status: 'error', message: `MCP Error: ${jsonResponse.error.message || JSON.stringify(jsonResponse.error)}` });
      } else if (jsonResponse.result && jsonResponse.result.content && jsonResponse.result.content[0] && jsonResponse.result.content[0].text) {
        logs.push({ nodeId: n.id, status: 'executed', message: `Success: ${jsonResponse.result.content[0].text.substring(0, 100)}...` });
      } else {
        logs.push({ nodeId: n.id, status: 'executed', message: `Success: ${JSON.stringify(jsonResponse.result).substring(0, 100)}...` });
      }

    } catch (error: any) {
      logs.push({ nodeId: n.id, status: 'error', message: `Execution failed: ${error.message || error}` });
    }
  }

  return { runId, ok: true, logs };
}






